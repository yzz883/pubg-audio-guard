#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PUBG Audio Guard — GUI（多语言: 简体中文 / English / Русский / Español / 日本語）

用法: python pubg_audio_gui.py  （或双击 start_gui.bat）

把鼠标悬停在任何参数上，下方会显示该参数的详细说明和调节建议。
语言切换: 右上角下拉框，立即生效并保存。
"""

import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import numpy as np
    import sounddevice as sd
    import pubg_audio as pa
    import i18n
except ImportError as e:
    r = tk.Tk()
    r.withdraw()
    messagebox.showerror("Missing dependency", f"{e}\n\npython -m pip install numpy sounddevice scipy")
    sys.exit(1)

CONFIG_PATH = pa.DEFAULT_CONFIG_PATH

# (参数键, 最小, 最大, 步进, 数值显示格式)
MAIN_PARAMS = [
    ("pre_gain_db",        -20, 24,   0.5, "{:+.1f} dB"),
    ("comp_threshold_db",  -40, 0,    0.5, "{:.1f} dBFS"),
    ("comp_ratio",         1.0, 10,   0.1, "{:.1f} : 1"),
    ("low_shelf_gain_db",  -18, 0,    0.5, "{:.1f} dB"),
    ("high_shelf_gain_db", -18, 0,    0.5, "{:.1f} dB"),
    ("limiter_ceiling_db", -12, -0.5, 0.5, "{:.1f} dBFS"),
]

ADV_PARAMS = [
    ("comp_attack_ms",     1,   100,  1,   "{:.0f} ms"),
    ("comp_release_ms",    20,  1000, 5,   "{:.0f} ms"),
    ("limiter_release_ms", 20,  500,  5,   "{:.0f} ms"),
    ("low_shelf_freq",     80,  400,  5,   "{:.0f} Hz"),
    ("high_shelf_freq",    2000, 8000, 100, "{:.0f} Hz"),
]

PRESETS = [
    ("preset_light", {
        "pre_gain_db": 2.0, "comp_threshold_db": -14.0, "comp_ratio": 2.0,
        "comp_attack_ms": 10, "comp_release_ms": 150,
        "low_shelf_gain_db": -4.0, "high_shelf_gain_db": -2.0,
        "limiter_ceiling_db": -3.0, "limiter_release_ms": 80, "auto_makeup": True}),
    ("preset_balanced", {
        "pre_gain_db": 3.0, "comp_threshold_db": -18.0, "comp_ratio": 2.5,
        "comp_attack_ms": 10, "comp_release_ms": 150,
        "low_shelf_gain_db": -8.0, "high_shelf_gain_db": -4.0,
        "limiter_ceiling_db": -3.0, "limiter_release_ms": 80, "auto_makeup": True}),
    ("preset_strong", {
        "pre_gain_db": 5.0, "comp_threshold_db": -24.0, "comp_ratio": 4.0,
        "comp_attack_ms": 8, "comp_release_ms": 200,
        "low_shelf_gain_db": -12.0, "high_shelf_gain_db": -6.0,
        "limiter_ceiling_db": -3.0, "limiter_release_ms": 60, "auto_makeup": True}),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cfg = pa.load_config(CONFIG_PATH)
        self.lang = i18n.resolve(self.cfg.get("language", "auto"))
        self.cfg["language"] = self.lang
        self.T = i18n.strings(self.lang)
        self.dsp = pa.DSP(self.cfg)
        self.in_stream = None
        self.out_stream = None
        self.engine = None
        self.test_stream = None
        self.running = False
        self.scales = {}
        # 电平表平滑值（dB，快上慢下）
        self.m_in = -60.0
        self.m_out = -60.0
        self.m_comp = 0.0
        self.m_lim = 0.0
        self._build()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(80, self._poll)

    # ---------- 界面构建（语言切换时会整体重建） ----------

    def _build(self):
        T = self.T
        self.title(f"PUBG Audio Guard · {T['title_suffix']}")
        self.geometry("720x930")
        self.minsize(640, 880)

        # 状态栏最先 pack（贴底），窗口高度不足时被裁的是最后 pack 的帮助区而不是状态栏
        self.status_var = tk.StringVar(value=T["status_stopped"])
        tk.Label(self, textvariable=self.status_var, anchor="w", bd=1,
                 relief="sunken").pack(fill="x", side="bottom")

        # 语言选择（右上角）
        langrow = tk.Frame(self)
        langrow.pack(fill="x", padx=8, pady=(6, 0))
        self.lang_names = {name: code for code, name in i18n.SUPPORTED}
        self.lang_var = tk.StringVar(value=dict(i18n.SUPPORTED)[self.lang])
        cb_lang = ttk.Combobox(langrow, textvariable=self.lang_var,
                               values=[n for _, n in i18n.SUPPORTED],
                               state="readonly", width=11)
        cb_lang.pack(side="right")
        cb_lang.bind("<<ComboboxSelected>>", self._set_language)
        tk.Label(langrow, text="🌐").pack(side="right", padx=(0, 4))

        # 设备
        top = tk.LabelFrame(self, text=T["devices"])
        top.pack(fill="x", padx=8, pady=(4, 3))
        self.in_var = tk.StringVar()
        self.out_var = tk.StringVar()
        row1 = tk.Frame(top)
        row1.pack(fill="x", padx=6, pady=(4, 1))
        tk.Label(row1, text=T["source_label"]).pack(side="left")
        self.cb_in = ttk.Combobox(row1, textvariable=self.in_var, state="readonly", width=24)
        self.cb_in.pack(side="left", padx=4)
        tk.Button(row1, text=T["refresh"], width=9,
                  command=self._refresh_devices).pack(side="left", padx=4)
        row2 = tk.Frame(top)
        row2.pack(fill="x", padx=6, pady=(1, 2))
        tk.Label(row2, text=T["out_label"]).pack(side="left")
        self.cb_out = ttk.Combobox(row2, textvariable=self.out_var, state="readonly", width=24)
        self.cb_out.pack(side="left", padx=4)
        tk.Button(row2, text=T["install_vbcable"], width=16, fg="#b00",
                  command=self._install_cable).pack(side="left", padx=4)
        self.cb_in.bind("<<ComboboxSelected>>", self._on_device_change)
        self.cb_out.bind("<<ComboboxSelected>>", self._on_device_change)

        self.hint_var = tk.StringVar(value="")
        self.hint_lbl = tk.Label(top, textvariable=self.hint_var, fg="#b00", justify="left",
                                 wraplength=680, font=("Microsoft YaHei UI", 9))
        self.hint_lbl.pack(anchor="w", padx=6, pady=(0, 4))
        self._refresh_devices()

        # 电平表
        mf = tk.LabelFrame(self, text=T["meters"])
        mf.pack(fill="x", padx=8, pady=3)
        self.cv = tk.Canvas(mf, height=104, bg="#fafafa", highlightthickness=0)
        self.cv.pack(fill="x", padx=4, pady=2)

        # 主要参数
        pf = tk.LabelFrame(self, text=T["main_params"])
        pf.pack(fill="x", padx=8, pady=3)
        for key, lo, hi, res, fmt in MAIN_PARAMS:
            self._param_row(pf, key, lo, hi, res, fmt)
        self.makeup_var = tk.BooleanVar(value=bool(self.cfg.get("auto_makeup", True)))
        tk.Checkbutton(pf, text=T["chk_makeup"], variable=self.makeup_var,
                       command=self._on_makeup).pack(anchor="w", padx=6, pady=2)

        # 按钮
        bf = tk.Frame(self)
        bf.pack(fill="x", padx=8, pady=2)
        self.btn_start = tk.Button(bf, text=T["btn_start"], width=9, bg="#e8f6e8", command=self._start)
        self.btn_start.pack(side="left", padx=2)
        self.btn_stop = tk.Button(bf, text=T["btn_stop"], width=9, state="disabled", command=self._stop)
        self.btn_stop.pack(side="left", padx=2)
        self.btn_test = tk.Button(bf, text=T["btn_test"], width=10, command=self._test_sound)
        self.btn_test.pack(side="left", padx=2)
        self.bypass_var = tk.BooleanVar(value=bool(self.dsp.bypass))
        tk.Checkbutton(bf, text=T["chk_bypass"], variable=self.bypass_var,
                       command=self._on_bypass).pack(side="left", padx=10)
        for text, cmd in ((T["btn_save"], self._save), (T["btn_reset"], self._reset),
                          (T["btn_help"], lambda: self._show_explain(None))):
            tk.Button(bf, text=text, width=11, command=cmd).pack(side="left", padx=2)

        # 预设
        prf = tk.Frame(self)
        prf.pack(fill="x", padx=8, pady=2)
        tk.Label(prf, text=T["preset_label"]).pack(side="left")
        for key, preset in PRESETS:
            tk.Button(prf, text=T[key], relief="groove",
                      command=lambda p=preset: self._apply_preset(p)).pack(side="left", padx=4)

        # 进阶参数
        af = tk.LabelFrame(self, text=T["adv_params"])
        af.pack(fill="x", padx=8, pady=3)
        for key, lo, hi, res, fmt in ADV_PARAMS:
            self._param_row(af, key, lo, hi, res, fmt)

        # 说明文字（带滚动条；窗口高度不够时牺牲它）
        df = tk.Frame(self)
        df.pack(fill="both", padx=8, pady=3)
        self.detail = tk.Text(df, height=6, wrap="word", bg="#f7f7f7", relief="flat",
                              font=("Microsoft YaHei UI", 9), state="disabled")
        dsb = ttk.Scrollbar(df, orient="vertical", command=self.detail.yview)
        self.detail.configure(yscrollcommand=dsb.set)
        dsb.pack(side="right", fill="y")
        self.detail.pack(side="left", fill="both", expand=True)
        self._show_explain(None)

    def _param_row(self, parent, key, lo, hi, res, fmt):
        T = self.T
        row = tk.Frame(parent)
        row.pack(fill="x", pady=0)
        name = tk.Label(row, text=T[f"lbl_{key}"], width=13, anchor="w")
        name.pack(side="left", padx=(6, 0))
        var = tk.StringVar(value=fmt.format(self.cfg[key]))
        val = tk.Label(row, textvariable=var, width=11, anchor="e", fg="#06c")
        val.pack(side="right", padx=(0, 6))
        sc = tk.Scale(row, from_=lo, to=hi, resolution=res, orient="horizontal",
                      showvalue=False, length=230,
                      command=lambda v, k=key, f=fmt, vv=var: self._on_slide(k, v, f, vv))
        sc.set(self.cfg[key])
        sc.pack(side="left", expand=True, fill="x", padx=6)
        self.scales[key] = sc
        for w in (name, sc, val):
            w.bind("<Enter>", lambda e, k=key: self._show_explain(k))
        return row

    # ---------- 语言切换 ----------

    def _set_language(self, _e=None):
        code = self.lang_names.get(self.lang_var.get())
        if not code or code == self.lang:
            return
        self.lang = code
        self.cfg["language"] = code
        self.T = i18n.strings(code)
        try:
            pa.save_config(CONFIG_PATH, self.cfg)
        except Exception:
            pass
        for w in self.winfo_children():
            w.destroy()
        self._build()

    # ---------- 文案/交互 ----------

    def _show_explain(self, key):
        T = self.T
        text = T.get(f"ex_{key}", T["overview"]) if key else T["overview"]
        self.detail.configure(state="normal")
        self.detail.delete("1.0", "end")
        self.detail.insert("1.0", text)
        self.detail.configure(state="disabled")

    def _on_slide(self, key, val, fmt, var):
        v = float(val)
        self.cfg[key] = v
        self.dsp.set_params(self.cfg)
        var.set(fmt.format(v))

    def _on_makeup(self):
        self.cfg["auto_makeup"] = bool(self.makeup_var.get())
        self.dsp.set_params(self.cfg)
        self._show_explain("auto_makeup")

    def _on_bypass(self):
        self.dsp.bypass = bool(self.bypass_var.get())

    def _apply_preset(self, preset):
        self.cfg.update(preset)
        self.dsp.set_params(self.cfg)
        for k, sc in self.scales.items():
            sc.set(self.cfg[k])
        self.makeup_var.set(bool(self.cfg.get("auto_makeup", True)))

    def _save(self):
        pa.save_config(CONFIG_PATH, self.cfg)

    def _reset(self):
        self.cfg.update(pa.DEFAULTS)
        self.cfg["language"] = self.lang
        self.dsp.set_params(self.cfg)
        for k, sc in self.scales.items():
            sc.set(self.cfg[k])
        self.makeup_var.set(bool(self.cfg.get("auto_makeup", True)))
        self._show_explain(None)

    # ---------- 设备 ----------

    def _refresh_devices(self):
        """重新枚举音频设备，更新下拉框、预选与提示。返回是否找到 CABLE Output。"""
        T = self.T
        self.in_map, self.in_names = self._device_map(True)
        self.out_map, self.out_names = self._device_map(False)
        self.in_names.sort(key=lambda n: 0 if "CABLE" in n.upper() else 1)
        self.out_names.sort(key=lambda n: 0 if "CABLE" in n.upper() else 1)
        cur_in, cur_out = self.in_var.get(), self.out_var.get()
        if cur_in not in self.in_names:
            cur_in = next((n for n in self.in_names if "CABLE Output" in n), "")
        if cur_out not in self.out_names:
            dflt_name = ""
            try:
                for h in sd.query_hostapis():
                    if "WASAPI" in h["name"] and h["default_output_device"] >= 0:
                        dflt = h["default_output_device"]
                        dflt_name = next((n for n, i in self.out_map.items() if i == dflt), "")
                        break
            except Exception:
                dflt_name = ""
            non_cable = [n for n in self.out_names
                         if "CABLE" not in n.upper() and "声音映射器" not in n]
            if dflt_name and "CABLE" not in dflt_name.upper():
                cur_out = dflt_name
            elif non_cable:
                cur_out = non_cable[0]
            else:
                cur_out = self.out_names[0] if self.out_names else ""
        self.in_var.set(cur_in)
        self.out_var.set(cur_out)
        self.cb_in.config(values=self.in_names)
        self.cb_out.config(values=self.out_names)
        try:
            di, do = sd.default.device
            hijacked = ("CABLE" in sd.query_devices(do)["name"].upper() or
                        "CABLE" in sd.query_devices(di)["name"].upper())
        except Exception:
            hijacked = False
        if any("CABLE Output" in n for n in self.in_names):
            if hijacked:
                self.hint_var.set(T["hint_hijack"])
                self.hint_lbl.config(fg="#c60")
            else:
                self.hint_var.set(T["hint_found"])
                self.hint_lbl.config(fg="#080")
            return True
        self.hint_var.set(T["hint_missing"])
        self.hint_lbl.config(fg="#b00")
        return False

    def _device_map(self, want_input):
        field = "max_input_channels" if want_input else "max_output_channels"
        hosts = sd.query_hostapis()
        best = {}
        for i, d in enumerate(sd.query_devices()):
            if d[field] <= 0:
                continue
            api = hosts[d["hostapi"]]["name"]
            sc = (1 if "WASAPI" in api else 0, -d[field], -i)
            name = d["name"]
            if name not in best or sc > best[name][0]:
                best[name] = (sc, i)
        items = sorted(best.items(), key=lambda kv: kv[1][1])
        return {n: idx for n, (_s, idx) in items}, [n for n, _ in items]

    def _on_device_change(self, _e=None):
        if self.running:
            self._stop()
            self._start()

    def _install_cable(self):
        T = self.T
        exe = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "VBCABLE", "VBCABLE_Setup_x64.exe")
        if not os.path.exists(exe):
            messagebox.showerror(T["err_installer_t"], T["err_installer_b"].format(path=exe))
            return
        try:
            subprocess.Popen(["powershell", "-NoProfile", "-Command",
                              f"Start-Process -Verb RunAs -FilePath '{exe}'"],
                             creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            messagebox.showerror(T["err_launch_t"], T["err_launch_b"].format(e=e))
            return
        messagebox.showinfo(T["info_install_t"], T["info_install_b"])

    # ---------- 启动/停止 ----------

    def _start(self):
        T = self.T
        self._refresh_devices()
        in_idx = self.in_map.get(self.in_var.get())
        out_idx = self.out_map.get(self.out_var.get())
        if in_idx is None or out_idx is None:
            messagebox.showerror(T["err_no_device_t"], T["err_no_device_b"])
            return
        if "CABLE" in self.out_var.get().upper():
            messagebox.showerror(T["err_out_cable_t"], T["err_out_cable_b"])
            return
        if "CABLE" not in self.in_var.get().upper():
            ok = messagebox.askyesno(
                T["ask_input_t"], T["ask_input_b"].format(name=self.in_var.get()))
            if not ok:
                return
        try:
            self.in_stream, self.out_stream, self.engine = pa.open_streams(
                self.cfg, self.dsp, in_idx, out_idx)
            self.in_stream.start()
        except Exception as e:
            self.in_stream = self.out_stream = self.engine = None
            messagebox.showerror(T["err_start_t"], T["err_start_b"].format(e=e))
            return
        self.running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        priming_ms = 1000.0 * (self.cfg["queue_target_blocks"] + 1) * self.cfg["blocksize"] / self.cfg["samplerate"]
        self.after(int(priming_ms) + 30, self._start_out)

    def _start_out(self):
        if self.running and self.out_stream is not None:
            try:
                self.out_stream.start()
            except Exception as e:
                messagebox.showerror(self.T["err_start_t"],
                                     self.T["err_start_out_b"].format(e=e))
                self._stop()

    def _stop(self):
        self.running = False
        for s in (self.in_stream, self.out_stream, self.test_stream):
            try:
                if s:
                    s.stop()
                    s.close()
            except Exception:
                pass
        self.in_stream = self.out_stream = self.engine = self.test_stream = None
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.m_in = self.m_out = -60.0
        self.m_comp = self.m_lim = 0.0

    def _on_close(self):
        self._stop()
        self.destroy()

    # ---------- 测试声音 ----------

    def _test_sound(self):
        T = self.T
        if not self.running:
            messagebox.showinfo(T["btn_test"], T["info_need_start"])
            return
        if self.test_stream is not None:
            return
        self._refresh_devices()
        cable_in = next((i for n, i in self.out_map.items()
                         if "CABLE Input" in n or "VB-Audio Virtual Cable" in n), None)
        if cable_in is None:
            found = "\n".join("  · " + n for n in self.out_names) or "  ()"
            messagebox.showerror(T["err_no_cable_in_t"],
                                 T["err_no_cable_in_b"].format(list=found))
            return
        self.test_sig = pa.make_test_signal(self.cfg, shot_peak=0.35)  # 试听音量调低
        self.test_pos = 0
        try:
            self.test_stream = sd.OutputStream(
                samplerate=self.cfg["samplerate"], blocksize=self.cfg["blocksize"],
                device=cable_in, channels=2, dtype="float32", latency="low",
                callback=self._test_cb)
            self.test_stream.start()
        except Exception as e:
            self.test_stream = None
            messagebox.showerror(T["err_test_t"], T["err_test_b"].format(e=e))
            return
        self.btn_test.config(state="disabled")
        dur_ms = 1000.0 * len(self.test_sig) / self.cfg["samplerate"]
        self.after(int(dur_ms) + 400, self._test_end)

    def _test_cb(self, outdata, frames, time_info, status):
        s = self.test_pos
        e = min(s + frames, len(self.test_sig))
        blk = self.test_sig[s:e]
        if len(blk) < frames:
            blk = np.vstack([blk, np.zeros((frames - len(blk), 2), np.float32)])
        outdata[:] = blk
        self.test_pos = e

    def _test_end(self):
        try:
            if self.test_stream:
                self.test_stream.stop()
                self.test_stream.close()
        except Exception:
            pass
        self.test_stream = None
        self.btn_test.config(state="normal")

    # ---------- 电平表轮询 ----------

    def _poll(self):
        self.after(80, self._poll)
        try:
            self._poll_body()
        except tk.TclError:
            pass  # 语言切换重建界面时，旧控件可能刚好被销毁

    def _poll_body(self):
        T = self.T
        st = self.dsp.pop_stats()
        in_db = pa.lin2db(st["in"]) if st["in"] > 0 else -60.0
        out_db = pa.lin2db(st["out"]) if st["out"] > 0 else -60.0
        comp = max(0.0, -pa.lin2db(st["comp"]))
        lim = max(0.0, -pa.lin2db(st["lim"]))
        self.m_in = max(in_db, self.m_in - 2.5, -60.0)
        self.m_out = max(out_db, self.m_out - 2.5, -60.0)
        self.m_comp = min(20.0, max(comp, self.m_comp - 0.9))
        self.m_lim = min(12.0, max(lim, self.m_lim - 0.9))
        self._draw_meters()
        if self.running and self.engine:
            with self.engine.lock:
                fill = len(self.engine.q)
            txt = T["status_running"].format(q=fill, u=self.engine.underruns,
                                             d=self.engine.drops, o=self.engine.overruns)
        elif self.running:
            txt = T["status_priming"]
        else:
            txt = T["status_stopped"]
        if self.dsp.bypass:
            txt += T["status_bypass"]
        self.status_var.set(txt)

    def _draw_meters(self):
        T = self.T
        c = self.cv
        c.delete("all")
        W = max(c.winfo_width(), 420)
        x0, x1 = 86, W - 70

        def bar(y, frac, color, label, val_text):
            c.create_text(6, y + 9, text=label, anchor="w", font=("Microsoft YaHei UI", 9))
            c.create_rectangle(x0, y, x1, y + 18, outline="#999")
            if frac > 0:
                xe = x0 + (x1 - x0) * min(1.0, frac)
                c.create_rectangle(x0 + 1, y + 1, xe, y + 17, fill=color, width=0)
            c.create_text(W - 6, y + 9, text=val_text, anchor="e", font=("Consolas", 9))

        bar(2, (self.m_in + 60) / 60.0,
            "#3fbf6f" if self.m_in < -6 else ("#e8c341" if self.m_in < -3 else "#e05555"),
            T["m_in"], f"{self.m_in:5.1f} dB")
        bar(26, (self.m_out + 60) / 60.0, "#39c2a0", T["m_out"], f"{self.m_out:5.1f} dB")
        bar(50, self.m_comp / 20.0, "#4da3ff", T["m_comp"], f"-{self.m_comp:4.1f} dB")
        bar(74, self.m_lim / 12.0, "#ff9f43", T["m_lim"], f"-{self.m_lim:4.1f} dB")

        for frac, lab in ((1.0, "0"), (0.9, "-6"), (0.8, "-12")):
            xx = x0 + (x1 - x0) * frac
            c.create_line(xx, 2, xx, 44, fill="#e05555", dash=(2, 3))
            c.create_text(xx, 96, text=lab + "dB", fill="#e05555", font=("Consolas", 7))


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
