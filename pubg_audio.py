#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PUBG 音频后处理器（夜间模式 / 听力保护）

把 PUBG 的声音（通过虚拟声卡单独送进来）做动态处理后送进耳机：
压缩器 + 限幅器 + 软削波 —— 压平枪声/爆炸/震爆弹的尖峰，抬高脚步等小声音，
这样总音量可以调低保护听力，同时依然听得清。
其他程序（比如你的脚本提示音）不经过本程序，完全不受影响。

链路:
    PUBG -> 虚拟声卡 CABLE Input -> 本程序(抓取->DSP->回放) -> 耳机
    其他程序 -----------------------------------------------> 耳机 (原路, 不处理)

用法:
    python pubg_audio.py --list      列出音频设备（确认 CABLE Output 存在）
    python pubg_audio.py --selftest  DSP 自测（不需要声卡）
    python pubg_audio.py             启动

运行中的控制命令（一行一个，回车执行）:
    g+ / g-   前置增益 ±1 dB
    t+ / t-   压缩阈值 ±1 dB
    r+ / r-   压缩比 ±0.5
    b         旁路/恢复（A/B 对比）
    s         显示当前参数
    save      保存参数到 config.json
    q         退出
"""

import argparse
import json
import math
import os
import sys
import threading
import time
from collections import deque

try:
    import numpy as np
    import sounddevice as sd
    from scipy.signal import lfilter
except ImportError as e:
    print(f"缺少依赖: {e}")
    print("请运行: python -m pip install numpy sounddevice scipy")
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(HERE, "config.json")

DEFAULTS = {
    "language": "auto",                # 界面语言: auto/zh_CN/en_US/ru_RU/es_ES/ja_JP
    "input_match": "CABLE Output",     # 输入设备名子串（虚拟声卡的录音端）
    "output_match": "",                # 输出设备名子串，空 = 系统默认输出
    "samplerate": 48000,
    "blocksize": 480,                  # 10 ms @48k
    "channels": 2,
    "queue_target_blocks": 5,          # 队列目标块数（实测 5 块零丢块零欠载）
    "pre_gain_db": 3.0,                # 前置增益：把小声音整体抬起来
    "comp_threshold_db": -18.0,        # 压缩阈值 dBFS
    "comp_ratio": 2.5,                 # 压缩比
    "comp_attack_ms": 10.0,
    "comp_release_ms": 150.0,
    "auto_makeup": True,               # 自动补偿增益
    "limiter_ceiling_db": -3.0,        # 限幅上限 dBFS（尖峰再也不会超过它）
    "limiter_attack_ms": 2.0,
    "limiter_release_ms": 80.0,
    "low_shelf_freq": 180.0,           # EQ：低频搁架，切爆炸/手雷的"闷压感"
    "low_shelf_gain_db": -8.0,
    "high_shelf_freq": 4000.0,         # EQ：高频搁架，切耳鸣音效/炸裂"刺"感
    "high_shelf_gain_db": -4.0,
}

print_lock = threading.Lock()

HELP_TEXT = """控制命令:  g+/g- 前置增益±1dB | t+/t- 压缩阈值±1dB | r+/r- 压缩比±0.5
           b 旁路对比 | s 显示参数 | save 保存 | q 退出"""


def db2lin(db):
    return 10.0 ** (db / 20.0)


def lin2db(v):
    return 20.0 * math.log10(max(float(v), 1e-12))


def _shelf_coeffs(f0, gain_db, fs, high):
    """RBJ cookbook 搁架式 EQ 系数（低频搁架/高频搁架）。gain_db=0 时直通。"""
    if abs(gain_db) < 1e-6:
        return np.array([1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])
    A = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * math.pi * min(float(f0), fs * 0.45) / fs
    cw = math.cos(w0)
    sa = math.sqrt(A)
    alpha = math.sin(w0) / math.sqrt(2.0)   # shelf slope S=1
    if high:
        b0 = A * ((A + 1) + (A - 1) * cw + 2 * sa * alpha)
        b1 = -2 * A * ((A - 1) + (A + 1) * cw)
        b2 = A * ((A + 1) + (A - 1) * cw - 2 * sa * alpha)
        a0 = (A + 1) - (A - 1) * cw + 2 * sa * alpha
        a1 = 2 * ((A - 1) - (A + 1) * cw)
        a2 = (A + 1) - (A - 1) * cw - 2 * sa * alpha
    else:
        b0 = A * ((A + 1) - (A - 1) * cw + 2 * sa * alpha)
        b1 = 2 * A * ((A - 1) - (A + 1) * cw)
        b2 = A * ((A + 1) - (A - 1) * cw - 2 * sa * alpha)
        a0 = (A + 1) + (A - 1) * cw + 2 * sa * alpha
        a1 = -2 * ((A - 1) + (A + 1) * cw)
        a2 = (A + 1) + (A - 1) * cw - 2 * sa * alpha
    return (np.array([b0 / a0, b1 / a0, b2 / a0]),
            np.array([1.0, a1 / a0, a2 / a0]))


class DSP:
    """压缩器 + 限幅器 + 软削波。输入/输出都是 float32，形状 (n, ch)。

    实现要点：以 2.5ms 子块为单位计算峰值包络（attack/release 单极平滑），
    子块间增益线性插值避免"拉链声"，最后软削波兜底保证峰值绝不超限。
    """

    def __init__(self, cfg):
        self.bypass = False
        self.comp_env = 0.0
        self.lim_env = 0.0
        self.stat_comp = 1.0   # 区间内最小增益（线性），用于状态显示
        self.stat_lim = 1.0
        self.stat_in = 0.0     # 区间内输入/输出峰值（线性），用于电平表
        self.stat_out = 0.0
        self.ls_zi = None      # EQ 滤波器状态（懒初始化，随声道数适配）
        self.hs_zi = None
        self.set_params(cfg)

    def set_params(self, cfg):
        self.sub = max(1, int(round(cfg["samplerate"] * 0.0025)))  # 2.5ms
        dt = self.sub / cfg["samplerate"]
        self.pre_gain = db2lin(cfg["pre_gain_db"])
        self.comp_t = db2lin(cfg["comp_threshold_db"])
        self.comp_r = max(1.0, float(cfg["comp_ratio"]))
        self.makeup = self.comp_t ** (-1.0 / self.comp_r) if cfg.get("auto_makeup", True) else 1.0
        self.comp_a = math.exp(-dt / max(1e-4, cfg["comp_attack_ms"] / 1000.0))
        self.comp_rl = math.exp(-dt / max(1e-4, cfg["comp_release_ms"] / 1000.0))
        self.lim = db2lin(cfg["limiter_ceiling_db"])
        self.lim_a = math.exp(-dt / max(1e-4, cfg["limiter_attack_ms"] / 1000.0))
        self.lim_rl = math.exp(-dt / max(1e-4, cfg["limiter_release_ms"] / 1000.0))
        # EQ 搁架滤波器系数
        self.ls_b, self.ls_a = _shelf_coeffs(cfg.get("low_shelf_freq", 180.0),
                                             cfg.get("low_shelf_gain_db", 0.0),
                                             cfg["samplerate"], high=False)
        self.hs_b, self.hs_a = _shelf_coeffs(cfg.get("high_shelf_freq", 4000.0),
                                             cfg.get("high_shelf_gain_db", 0.0),
                                             cfg["samplerate"], high=True)

    def reset_stats(self):
        self.stat_comp = 1.0
        self.stat_lim = 1.0

    def pop_stats(self):
        """读取并清空区间统计（供状态栏/电平表轮询）。"""
        s = {"in": self.stat_in, "out": self.stat_out, "comp": self.stat_comp, "lim": self.stat_lim}
        self.stat_in = 0.0
        self.stat_out = 0.0
        self.stat_comp = 1.0
        self.stat_lim = 1.0
        return s

    def process(self, x):
        if x.size:
            in_pk = float(np.abs(x).max())
            if in_pk > self.stat_in:
                self.stat_in = in_pk
        if self.bypass:
            if x.size and self.stat_in > self.stat_out:
                self.stat_out = self.stat_in
            return x
        n, ch = x.shape
        y = x * self.pre_gain

        # --- EQ 整形：低切去手雷/爆炸的"闷压感"，高切耳鸣音效的"尖锐" ---
        if lfilter is not None and (self.ls_b[1] != 0.0 or self.hs_b[1] != 0.0):
            if self.ls_zi is None or self.ls_zi.shape[1] != ch:
                self.ls_zi = np.zeros((2, ch))
                self.hs_zi = np.zeros((2, ch))
            y = y.astype(np.float64)
            y, self.ls_zi = lfilter(self.ls_b, self.ls_a, y, axis=0, zi=self.ls_zi)
            y, self.hs_zi = lfilter(self.hs_b, self.hs_a, y, axis=0, zi=self.hs_zi)
            y = y.astype(np.float32)

        sub = self.sub
        ns = n // sub
        if ns == 0:
            peaks = np.array([float(np.abs(y).max())])
        else:
            peaks = np.abs(y[: ns * sub].reshape(ns, sub, ch)).max(axis=(1, 2)).astype(np.float64)

        # --- 压缩器（子块包络 + 增益插值） ---
        gains = np.empty(max(ns, 1), dtype=np.float64)
        env = self.comp_env
        for i in range(gains.size):
            p = peaks[i]
            c = self.comp_a if p > env else self.comp_rl
            env = c * env + (1.0 - c) * p
            gains[i] = (env / self.comp_t) ** (1.0 / self.comp_r - 1.0) if env > self.comp_t else 1.0
        self.comp_env = env
        if gains.size > 1:
            self.stat_comp = min(self.stat_comp, float(gains.min()))
        g_curve = np.interp(np.arange(n, dtype=np.float64),
                            np.arange(gains.size) * sub, gains) * self.makeup
        y *= g_curve.astype(np.float32)[:, None]

        # --- 限幅器（把残余尖峰压到上限以内） ---
        lgains = np.empty_like(gains)
        lenv = self.lim_env
        for i in range(lgains.size):
            p = peaks[i]
            c = self.lim_a if p > lenv else self.lim_rl
            lenv = c * lenv + (1.0 - c) * p
            lgains[i] = min(1.0, self.lim / lenv) if lenv > 0 else 1.0
        self.lim_env = lenv
        if lgains.size > 1:
            self.stat_lim = min(self.stat_lim, float(lgains.min()))
        y *= np.interp(np.arange(n, dtype=np.float64),
                       np.arange(lgains.size) * sub, lgains).astype(np.float32)[:, None]

        # --- 软削波兜底：超过拐点的样本用 tanh 平滑压回，峰值不超 lim ---
        knee = 0.8 * self.lim
        a = np.abs(y)
        m = a > knee
        if m.any():
            av = a[m]
            t = (av - knee) / max(1e-9, self.lim - knee)
            s = (knee + np.tanh(t) * (self.lim - knee)).astype(np.float32)
            y[m] = np.sign(y[m]) * s
        if y.size:
            out_pk = float(np.abs(y).max())
            if out_pk > self.stat_out:
                self.stat_out = out_pk
        return y


def mix_channels(x, n):
    ch = x.shape[1]
    if ch == n:
        return x
    if ch > n:
        if n == 1:
            return x.mean(axis=1, keepdims=True)
        return np.ascontiguousarray(x[:, :n])
    rep = (n + ch - 1) // ch
    return np.tile(x, (1, rep))[:, :n]


class Engine:
    """两个音频流之间的搬运工：抓取队列 -> DSP -> 回放，含时钟漂移校正。"""

    def __init__(self, cfg, dsp, out_ch, in_ch=None, fs_in=None):
        self.cfg = cfg
        self.dsp = dsp
        self.out_ch = out_ch
        self.in_ch = in_ch or out_ch
        self.fs_out = cfg["samplerate"]
        self.fs_in = fs_in or self.fs_out
        self.src_ratio = self.fs_in / self.fs_out  # 抓取率/回放率，≠1 时走重采样路径
        self.raw = np.zeros((0, self.in_ch), dtype=np.float32)  # 待重采样的抓取数据
        self.src_pos = 0.0
        self.lock = threading.Lock()
        self.q = deque()
        self.residual = None   # 上次输出回调没用完的样本（同采样率路径用）
        self.tail = None       # 刚送出去的最后几个样本（交叉淡化用）
        self.seam = False
        self.underruns = 0
        self.overruns = 0
        self.drops = 0
        self.last_status_in = ""
        self.last_status_out = ""

    def input_cb(self, indata, frames, time_info, status):
        if status:
            self.last_status_in = str(status)
        with self.lock:
            if len(self.q) >= 64:
                self.overruns += 1
                return
            self.q.append(indata.copy())

    def output_cb(self, outdata, frames, time_info, status):
        if status:
            self.last_status_out = str(status)
        try:
            self._fill(outdata, frames)
        except Exception as e:  # 回调里绝不能抛异常
            outdata[:] = 0
            self.last_status_out = f"callback error: {e}"

    def _fill(self, outdata, frames):
        if abs(self.src_ratio - 1.0) < 1e-9:
            self._fill_same_rate(outdata, frames)
        else:
            self._fill_resample(outdata, frames)

    def _pull_block(self):
        """从队列取一块，带漂移校正（缓冲超了就丢最旧的）。队列空返回 None。"""
        try:
            blk = self.q.popleft()
        except IndexError:
            self.underruns += 1
            self.seam = True
            return None
        if len(self.q) > self.cfg["queue_target_blocks"]:
            self.q.popleft()  # 两个设备时钟有微小偏差，缓冲超了就丢最旧的一块
            self.drops += 1
            self.seam = True
        return blk

    def _fill_same_rate(self, outdata, frames):
        need = frames
        buf = self.residual
        chunks = []
        with self.lock:
            while need > 0:
                if buf is not None and len(buf) > 0:
                    take = min(need, len(buf))
                    chunks.append(buf[:take])
                    buf = buf[take:]
                    need -= take
                    continue
                blk = self._pull_block()
                if blk is None:
                    chunks.append(np.zeros((need, self.out_ch), dtype=np.float32))
                    need = 0
                    break
                buf = blk
        self.residual = buf if (buf is not None and len(buf)) else None
        self._emit(outdata, np.concatenate(chunks, axis=0), frames)

    def _fill_resample(self, outdata, frames):
        """抓取/回放采样率不同（如 VB-Cable 抓 44.1k/放 48k）：线性插值重采样。"""
        need = int(self.src_pos + frames * self.src_ratio) + 2
        with self.lock:
            while len(self.raw) < need:
                blk = self._pull_block()
                if blk is None:
                    blk = np.zeros((self.cfg["blocksize"], self.in_ch), dtype=np.float32)
                if blk.shape[1] != self.in_ch:
                    blk = mix_channels(blk, self.in_ch)
                self.raw = np.concatenate([self.raw, blk])
        base = self.src_pos + np.arange(frames, dtype=np.float64) * self.src_ratio
        i0 = base.astype(np.int64)
        w = (base - i0).astype(np.float32)[:, None]
        audio = self.raw[i0] * (1.0 - w) + self.raw[i0 + 1] * w
        self.src_pos += frames * self.src_ratio
        self.raw = self.raw[i0[-1]:]          # 保留末尾历史样本供下次插值
        self.src_pos -= i0[-1]
        self._emit(outdata, audio, frames)

    def _emit(self, outdata, audio, frames):
        if audio.shape[1] != self.out_ch:
            audio = mix_channels(audio, self.out_ch)
        audio = self.dsp.process(audio)
        outdata[:frames] = audio[:frames]
        # 丢块/欠载造成的内容跳变，用 64 样本交叉淡化抹平
        if self.seam and self.tail is not None:
            nf = min(64, frames, len(self.tail))
            if nf > 0:
                w = np.linspace(0.0, 1.0, nf, dtype=np.float32)[:, None]
                outdata[:nf] = self.tail[:nf] * (1.0 - w) + outdata[:nf] * w
            self.seam = False
        self.tail = outdata[max(0, frames - 64):frames].copy()


def list_devices():
    hosts = sd.query_hostapis()
    devs = sd.query_devices()
    default_in, default_out = sd.default.device
    print(f"{'序号':>4}  {'API':<16} {'输入':>4} {'输出':>4}  设备名")
    for i, d in enumerate(devs):
        api = hosts[d["hostapi"]]["name"]
        mark = ""
        if i == default_in:
            mark += "  *默认输入"
        if i == default_out:
            mark += "  *默认输出"
        print(f"{i:>4}  {api:<16} {d['max_input_channels']:>4} {d['max_output_channels']:>4}  {d['name']}{mark}")
    print("\n提示: 本程序需要的输入设备是虚拟声卡的 'CABLE Output'（装好 VB-Cable 后会出现）。")


def find_device(match, want_input):
    """按名字子串找设备（优先 WASAPI）。match 为空时用系统默认设备。"""
    if not match:
        return sd.default.device[0 if want_input else 1]
    field = "max_input_channels" if want_input else "max_output_channels"
    hosts = sd.query_hostapis()
    best = None
    for i, d in enumerate(sd.query_devices()):
        if d[field] <= 0:
            continue
        if match.lower() not in d["name"].lower():
            continue
        api = hosts[d["hostapi"]]["name"]
        score = (1 if "WASAPI" in api else 0, -d[field], -i)
        if best is None or score > best[0]:
            best = (score, i)
    return None if best is None else best[1]


def make_test_signal(cfg, dur=6.0, shot_peak=0.98):
    """合成一段'脚步+枪声'测试信号（背景噪声约 -34dBFS，每秒一次枪声），返回 (n, 2) float32。

    shot_peak: 枪声峰值振幅。离线自测用默认 0.98；GUI 试听用小值（如 0.35），避免耳机炸响。
    """
    fs = cfg["samplerate"]
    n = int(fs * dur)
    rng = np.random.default_rng(7)
    x = (0.02 * rng.standard_normal(n)).astype(np.float32)          # 背景"脚步"层 ~ -34 dBFS
    for k in range(int(dur) - 1):
        s = int((k + 0.5) * fs)
        L = int(0.03 * fs)
        burst = rng.standard_normal(L).astype(np.float32)           # 30ms 衰减噪声 = 枪声
        burst *= np.exp(-np.arange(L) / (0.004 * fs)).astype(np.float32)
        burst /= np.max(np.abs(burst))
        x[s:s + L] += burst * shot_peak
    return np.stack([x, x], axis=1)


def run_selftest(cfg):
    """合成一段'脚步+枪声'信号过一遍 DSP，验证压尖峰/抬小声的效果。不需要声卡。"""
    fs = cfg["samplerate"]
    dur = 6.0
    x = make_test_signal(cfg, dur)[:, :1]

    dsp = DSP(cfg)
    y = dsp.process(x)

    quiet_in, quiet_out = [], []
    for k in range(int(dur) - 1):
        s = int((k + 0.5) * fs) - int(0.2 * fs)
        quiet_in.append(x[s:s + int(0.1 * fs)])
        quiet_out.append(y[s:s + int(0.1 * fs)])
    qi, qo = np.concatenate(quiet_in), np.concatenate(quiet_out)
    peak_in = lin2db(np.abs(x).max())
    peak_out = lin2db(np.abs(y).max())
    rms_in = lin2db(np.sqrt((qi.astype(np.float64) ** 2).mean()))
    rms_out = lin2db(np.sqrt((qo.astype(np.float64) ** 2).mean()))
    gun_db = lin2db(0.98)

    print(f"输入峰值 {peak_in:6.1f} dBFS | 输出峰值 {peak_out:6.1f} dBFS (限幅上限 {cfg['limiter_ceiling_db']:.0f} dB)")
    print(f"安静段(脚步) RMS {rms_in:6.1f} dBFS -> {rms_out:6.1f} dBFS  (提升 {rms_out - rms_in:+.1f} dB)")
    print(f"枪声峰值  {gun_db:6.1f} dBFS -> {peak_out:6.1f} dBFS  (压低 {peak_out - gun_db:+.1f} dB)")

    # 真正的目标指标：峰值-安静段的对比度（动态范围）被压缩了多少
    contrast_in = peak_in - rms_in
    contrast_out = peak_out - rms_out
    print(f"动静对比度 {contrast_in:.1f} dB -> {contrast_out:.1f} dB  (压缩 {contrast_out - contrast_in:+.1f} dB)")

    ok1 = peak_out <= cfg["limiter_ceiling_db"] + 0.5
    ok2 = (rms_out - rms_in) >= 4.0
    ok3 = contrast_out <= contrast_in - 8.0
    passed = ok1 and ok2 and ok3
    print(f"自测: {'通过' if passed else '未通过'}  "
          f"[限幅不超限 {'√' if ok1 else '×'} | 抬高小声 {'√' if ok2 else '×'} | 压缩对比度 {'√' if ok3 else '×'}]")
    return 0 if passed else 1


def load_config(path):
    cfg = dict(DEFAULTS)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg.update(json.load(f))
        except Exception as e:
            print(f"[警告] 读取 {path} 失败: {e}，使用默认参数")
    return cfg


def save_config(path, cfg):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({k: cfg[k] for k in DEFAULTS}, f, ensure_ascii=False, indent=2)
    print(f"已保存参数到 {path}")


def handle_command(c, cfg, dsp, config_path):
    def clamp(v, lo, hi):
        return max(lo, min(hi, v))

    if c in ("h", "help", "?"):
        print("\n" + HELP_TEXT)
    elif c == "g+":
        cfg["pre_gain_db"] = clamp(cfg["pre_gain_db"] + 1, -20, 24)
        dsp.set_params(cfg)
        print(f"\n前置增益 {cfg['pre_gain_db']:+.0f} dB")
    elif c == "g-":
        cfg["pre_gain_db"] = clamp(cfg["pre_gain_db"] - 1, -20, 24)
        dsp.set_params(cfg)
        print(f"\n前置增益 {cfg['pre_gain_db']:+.0f} dB")
    elif c == "t+":
        cfg["comp_threshold_db"] = clamp(cfg["comp_threshold_db"] + 1, -40, 0)
        dsp.set_params(cfg)
        print(f"\n压缩阈值 {cfg['comp_threshold_db']:.0f} dBFS")
    elif c == "t-":
        cfg["comp_threshold_db"] = clamp(cfg["comp_threshold_db"] - 1, -40, 0)
        dsp.set_params(cfg)
        print(f"\n压缩阈值 {cfg['comp_threshold_db']:.0f} dBFS")
    elif c == "r+":
        cfg["comp_ratio"] = clamp(cfg["comp_ratio"] + 0.5, 1.0, 10.0)
        dsp.set_params(cfg)
        print(f"\n压缩比 {cfg['comp_ratio']:.1f}:1")
    elif c == "r-":
        cfg["comp_ratio"] = clamp(cfg["comp_ratio"] - 0.5, 1.0, 10.0)
        dsp.set_params(cfg)
        print(f"\n压缩比 {cfg['comp_ratio']:.1f}:1")
    elif c == "b":
        dsp.bypass = not dsp.bypass
        print("\n[旁路中：原始声音直通]" if dsp.bypass else "\n[恢复处理]")
    elif c == "s":
        print(f"\n增益 {cfg['pre_gain_db']:+.1f}dB | 阈值 {cfg['comp_threshold_db']:.0f}dB | "
              f"比例 {cfg['comp_ratio']:.1f}:1 | 限幅上限 {cfg['limiter_ceiling_db']:.0f}dB"
              f"{' | [旁路]' if dsp.bypass else ''}")
    elif c == "save":
        save_config(config_path, cfg)
    elif c == "q":
        return False
    else:
        print(f"\n未知命令: {c}  (h=帮助)")
    return True


def cmd_loop(dsp, cfg, config_path, stop):
    try:
        for line in sys.stdin:
            c = line.strip().lower()
            if not c:
                continue
            with print_lock:
                ok = handle_command(c, cfg, dsp, config_path)
            if not ok:
                stop.set()
                return
    except Exception:
        pass
    with print_lock:
        print("\n[标准输入已关闭，用 Ctrl+C 退出]")


def status_loop(engine, dsp, cfg, stop):
    while not stop.wait(0.5):
        with engine.lock:
            fill = len(engine.q)
        st = dsp.pop_stats()
        comp_red = max(0.0, -lin2db(st["comp"]))
        lim_red = max(0.0, -lin2db(st["lim"]))
        in_db = lin2db(st["in"]) if st["in"] > 0 else -60.0
        line = (f"输入{in_db:6.1f}dBFS | 缓冲{fill:>2}块 | "
                f"压低 {comp_red:5.1f}dB | 限幅 {lim_red:4.1f}dB | "
                f"欠载{engine.underruns} 丢弃{engine.drops}{' | [旁路]' if dsp.bypass else ''}")
        with print_lock:
            sys.stdout.write("\r" + line.ljust(110))
            sys.stdout.flush()


def _rate_ok(cfg, fs, idx, ch, is_input):
    """试开一个流来确认该设备支持采样率 fs。"""
    try:
        if is_input:
            s = sd.InputStream(samplerate=fs, blocksize=cfg["blocksize"], device=idx,
                               channels=ch, dtype="float32", latency="low")
        else:
            s = sd.OutputStream(samplerate=fs, blocksize=cfg["blocksize"], device=idx,
                                channels=ch, dtype="float32", latency="low")
        s.close()
        return True
    except Exception:
        return False


def open_streams(cfg, dsp, in_idx, out_idx):
    """创建抓取/回放两条流和 Engine（不启动），返回 (in_stream, out_stream, engine)。

    采样率优先用配置值；设备不支持时（如 VB-Cable 抓取端只有 44100、播放端只有
    48000）分别为两端挑选可用采样率，引擎自动做重采样。写回 cfg["samplerate"]。
    """
    din, dout = sd.query_devices(in_idx), sd.query_devices(out_idx)
    in_ch = min(cfg["channels"], din["max_input_channels"])
    out_ch = min(cfg["channels"], dout["max_output_channels"])
    if in_ch < 1 or out_ch < 1:
        raise RuntimeError("设备声道数异常")

    fs = int(cfg["samplerate"])
    fs_in, fs_out = fs, fs
    if not (_rate_ok(cfg, fs, in_idx, in_ch, True) and _rate_ok(cfg, fs, out_idx, out_ch, False)):
        def cands(dev):
            seen, out = set(), []
            for r in (fs, int(round(dev["default_samplerate"])), 48000, 44100, 96000, 88200):
                r = int(r)
                if r > 0 and r not in seen:
                    seen.add(r)
                    out.append(r)
            return out
        fs_in = next((r for r in cands(din) if _rate_ok(cfg, r, in_idx, in_ch, True)), None)
        fs_out = next((r for r in cands(dout) if _rate_ok(cfg, r, out_idx, out_ch, False)), None)
        if fs_in is None or fs_out is None:
            raise RuntimeError("采样率协商失败: 无法确定抓取/回放设备支持的采样率，"
                               "请在 Windows 声音设置里检查设备默认格式")
    cfg["samplerate"] = fs_out      # DSP 与延迟估算以回放率为准
    dsp.set_params(cfg)
    engine = Engine(cfg, dsp, out_ch, in_ch, fs_in)
    bs = cfg["blocksize"]
    in_stream = sd.InputStream(samplerate=fs_in, blocksize=bs, device=in_idx, channels=in_ch,
                               dtype="float32", latency="low", callback=engine.input_cb)
    out_stream = sd.OutputStream(samplerate=fs_out, blocksize=bs, device=out_idx, channels=out_ch,
                                 dtype="float32", latency="low", callback=engine.output_cb)
    return in_stream, out_stream, engine


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="PUBG 音频后处理器（压缩+限幅，保护听力）")
    ap.add_argument("--list", action="store_true", help="列出音频设备")
    ap.add_argument("--selftest", action="store_true", help="DSP 自测（不需要声卡）")
    ap.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="配置文件路径")
    ap.add_argument("--input", help="输入设备名子串（默认找 CABLE Output）")
    ap.add_argument("--output", help="输出设备名子串（默认系统默认输出）")
    ap.add_argument("--gain", type=float, help="前置增益 dB")
    ap.add_argument("--threshold", type=float, help="压缩阈值 dBFS")
    ap.add_argument("--ratio", type=float, help="压缩比")
    ap.add_argument("--blocksize", type=int, help="块大小（默认480=10ms）")
    ap.add_argument("--target", type=int, help="队列目标块数（延迟粗调）")
    ap.add_argument("--channels", type=int, help="声道数（默认2）")
    args = ap.parse_args()

    cfg = load_config(args.config)
    if args.input is not None:
        cfg["input_match"] = args.input
    if args.output is not None:
        cfg["output_match"] = args.output
    if args.gain is not None:
        cfg["pre_gain_db"] = args.gain
    if args.threshold is not None:
        cfg["comp_threshold_db"] = args.threshold
    if args.ratio is not None:
        cfg["comp_ratio"] = args.ratio
    if args.blocksize:
        cfg["blocksize"] = args.blocksize
    if args.target:
        cfg["queue_target_blocks"] = args.target
    if args.channels:
        cfg["channels"] = args.channels

    if args.list:
        list_devices()
        return
    if args.selftest:
        sys.exit(run_selftest(cfg))

    in_idx = find_device(cfg["input_match"], True)
    out_idx = find_device(cfg["output_match"], False)
    if in_idx is None:
        print("找不到输入设备（需要虚拟声卡的 'CABLE Output'）。")
        print("请先安装 VB-Cable: https://vb-audio.com/Cable/ 下载 -> 解压 -> 管理员运行 VBCABLE_Setup_x64.exe -> 重启")
        print("装好后用 --list 确认设备出现，再运行本程序。")
        sys.exit(1)
    if out_idx is None:
        print("找不到输出设备。")
        sys.exit(1)

    din, dout = sd.query_devices(in_idx), sd.query_devices(out_idx)
    dsp = DSP(cfg)
    stop = threading.Event()

    print(f"输入: [{in_idx}] {din['name']}")
    print(f"输出: [{out_idx}] {dout['name']}")
    try:
        in_stream, out_stream, engine = open_streams(cfg, dsp, in_idx, out_idx)
    except Exception as e:
        print(f"音频流启动失败: {e}")
        sys.exit(1)
    fs, bs = cfg["samplerate"], cfg["blocksize"]
    block_ms = 1000.0 * bs / fs
    print(f"采样率 {fs}Hz | 块 {bs} ({block_ms:.1f}ms) | 目标缓冲 {cfg['queue_target_blocks']} 块 | "
          f"附加延迟约 {(cfg['queue_target_blocks'] + 2) * block_ms:.0f}ms")
    print("提醒: 请把 PUBG 的输出设备设置为 'CABLE Input'（音量混合器里按应用设置）。")
    print(HELP_TEXT)
    print("-" * 70)

    in_stream.start()
    time.sleep(block_ms * (cfg["queue_target_blocks"] + 1) / 1000.0)  # 预充缓冲
    out_stream.start()

    threading.Thread(target=cmd_loop, args=(dsp, cfg, args.config, stop), daemon=True).start()
    threading.Thread(target=status_loop, args=(engine, dsp, cfg, stop), daemon=True).start()

    try:
        while not stop.wait(0.25):
            pass
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        time.sleep(0.1)
        try:
            in_stream.stop(); in_stream.close()
            out_stream.stop(); out_stream.close()
        except Exception:
            pass
        with print_lock:
            print(f"\n已退出。本次会话: 欠载{engine.underruns} 丢弃{engine.drops} 溢出{engine.overruns}"
                  f"（持续增长才需要调 blocksize/target）")
            print("若程序不再运行，请把 PUBG 的输出设备改回默认，否则游戏没声音。")


if __name__ == "__main__":
    main()
