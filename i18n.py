# -*- coding: utf-8 -*-
"""PUBG Audio Guard — GUI 多语言字符串表 (i18n strings for the GUI).

支持语言 / Supported languages: 简体中文 zh_CN, English en_US,
Русский ru_RU, Español es_ES, 日本語 ja_JP.

新语言只需在本文件加一段 STRINGS["xx_XX"]；缺失的键自动回退 en_US。
"""

# (代码, 原生语言名) —— 语言下拉框按此顺序显示
SUPPORTED = [
    ("zh_CN", "简体中文"),
    ("en_US", "English"),
    ("ru_RU", "Русский"),
    ("es_ES", "Español"),
    ("ja_JP", "日本語"),
]

STRINGS = {}

# ======================================================================
# 简体中文
# ======================================================================
STRINGS["zh_CN"] = {
    "title_suffix": "调参台",
    "devices": " 设备 ",
    "source_label": "抓取源(录音设备):",
    "out_label": "播放到(耳机):",
    "refresh": "刷新设备",
    "install_vbcable": "安装 VB-Cable",
    "hint_found": "已找到 CABLE Output ✓（在'抓取源'列表顶部）—— 下一步: 启动 → 测试声音",
    "hint_hijack": "已找到 CABLE Output ✓ 但 ⚠ 系统默认输入/输出被虚拟声卡占了（安装时自动设置的）——"
                   "请到 Windows 声音设置把默认输出改回耳机、默认输入改回麦克风，"
                   "否则其他程序的声音和麦克风都会被劫持",
    "hint_missing": "未找到 CABLE Output。'抓取源'列表里全是麦克风是正常的——CABLE Output 也是一个"
                    "录音设备（它录的是放进虚拟声卡的声音），装好驱动后会出现在同一列表顶部。"
                    "点【安装 VB-Cable】→ UAC 点'是' → 安装窗口点'Install Driver' → 装完点【刷新设备】（没出现就重启电脑）",
    "meters": " 实时电平表 ",
    "m_in": "输入电平", "m_out": "输出电平", "m_comp": "压缩量", "m_lim": "限幅量",
    "main_params": " 主要参数 ",
    "adv_params": " 进阶参数（一般不用动） ",
    "btn_start": "启动", "btn_stop": "停止", "btn_test": "测试声音",
    "chk_bypass": "旁路对比", "btn_save": "保存参数", "btn_reset": "恢复默认",
    "btn_help": "? 参数说明",
    "preset_label": "一键预设:",
    "preset_light": "轻度·保留距离感",
    "preset_balanced": "均衡·默认",
    "preset_strong": "强力·夜间模式",
    "status_stopped": "已停止",
    "status_priming": "正在预充缓冲…",
    "status_running": "运行中 | 缓冲{q}块 | 欠载{u} 丢弃{d} 溢出{o}",
    "status_bypass": " | [旁路: 原始声音直通]",
    "overview": """使用步骤:
1. 点【启动】开始处理（需要已装好 VB-Cable；没装就点【安装 VB-Cable】按钮）
2. 进游戏后: Windows 设置 → 系统 → 声音 → 音量混合器 → PUBG → 输出设备改为 CABLE Input
3. 开一枪/跑几步，看电平表，拖动滑块调到满意，点【保存参数】
4. 验证效果: 点【测试声音】(合成"脚步+枪声"走一遍处理链，音量已调低；建议先把系统总音量调到 30%)，
   或勾【旁路对比】来回切换
5. 调好后把系统总音量调低 —— 这才是护耳的目的

【为什么"抓取源"里都是麦克风，却说需要 CABLE Output?】
虚拟声卡是一对设备，名字是从"声卡自己"的视角起的:
  · CABLE Input  = 播放端 → PUBG 往里"放"声音（出现在输出设备列表）
  · CABLE Output = 录音端 → 本程序从这里"取"声音（出现在录音设备列表，和麦克风混在一起）
类比快递柜: PUBG 往"投放口"(Input)放件，本程序从"取件口"(Output)取件。
所以程序要"输入"，拿的却是名字里带 Output 的那个——列表里全是麦克风是正常的。

把鼠标停到任一参数上，这里会显示它的详细说明；点【? 参数说明】回到本页。""",
    "lbl_pre_gain_db": "前置增益",
    "lbl_comp_threshold_db": "压缩阈值",
    "lbl_comp_ratio": "压缩比",
    "lbl_low_shelf_gain_db": "低频切除",
    "lbl_high_shelf_gain_db": "高频切除",
    "lbl_limiter_ceiling_db": "限幅上限",
    "lbl_comp_attack_ms": "启动时间",
    "lbl_comp_release_ms": "释放时间",
    "lbl_limiter_release_ms": "限幅释放",
    "lbl_low_shelf_freq": "低频转折",
    "lbl_high_shelf_freq": "高频转折",
    "chk_makeup": "自动补偿（响度稳定）",
    "ex_pre_gain_db": """前置增益 —— 处理前的整体音量（默认 +3 dB）
作用: 先把脚步、换弹这类小声音整体"垫高"，再交给压缩器。
类比: 开会前先把话筒音量拧大一格。
建议: 抬得太狠会觉得底噪变大、声音发闷，退 1~2 dB。调完后把系统总音量调低才是护耳关键。""",
    "ex_comp_threshold_db": """压缩阈值 —— 开始压缩的响度线（默认 -18 dBFS）
作用: 声音超过这条线，超出的部分被往下压；线以下的声音（脚步）不受影响。
类比: 水位警戒线，涨过线的水被抽掉一部分。
建议: 觉得枪声还是吓人 → 往低调（t-）；觉得远枪近枪分不清 → 往高调（t+）。""",
    "ex_comp_ratio": """压缩比 —— 超出部分压回去的比例（默认 2.5:1）
作用: 超过阈值的部分只保留 1/比例。2.5:1 = 超出 2.5dB 只留 1dB。
类比: 超速罚款，超得越多罚得越狠。
建议: 越大越"夜间模式"，但距离感越差。轻度 2:1，强力 4:1。""",
    "ex_low_shelf_gain_db": """低频切除 —— 把"闷/压迫感"切掉多少（默认 -8dB）
为什么需要它: 手雷、爆炸、汽车轰鸣的能量集中在低频（一两百赫兹以下），
耳朵对它的感受是"胸口被撞"的闷压感——压缩器只能压音量，动不了音色，
必须用 EQ 把这一段切掉。切完后爆炸会变"干脆"。
建议: 手雷还是闷 → 往低调到 -12；觉得游戏声音单薄/没劲 → 往回调向 0。""",
    "ex_high_shelf_gain_db": """高频切除 —— 把"刺耳/尖锐"压掉多少（默认 -4dB）
为什么需要它: 手雷爆炸后那声尖响是 PUBG 故意模拟的"耳鸣"音效（几千赫兹），
属于音效设计而不是 bug；高频切一刀后它会明显变钝，整体听感更温。
代价: 脚步会略闷一点点。
建议: 耳鸣声还是刺 → 往低调到 -8；声音发闷不真实 → 往回调向 0。""",
    "ex_limiter_ceiling_db": """限幅上限 —— 绝对不逾越的红线（默认 -3 dBFS）
作用: 最终保险丝，爆炸/震爆弹再响也绝不超过这条线。这是"护耳"的硬保证。
类比: 升降机的天花板，顶到就停。
建议: -3 dBFS 合适。如果电平表"限幅量"经常亮满，说明前面压缩不够，应先调阈值/比例，而不是把上限越调越低。""",
    "ex_comp_attack_ms": """启动时间 —— 冲过阈值后多久开始压（默认 10 ms）
作用: 太长 → 枪声第一下"啪"漏过去；太短 → 音头被掐住，声音发闷发糊。
类比: 反应速度，太慢挨打，太快显得神经质。
建议: 8~15ms 是射击游戏的常用折中，一般不用动。""",
    "ex_comp_release_ms": """释放时间 —— 压下去之后多久放开（默认 150 ms）
作用: 太短 → 声音忽大忽小，有"喘气/抽吸"感；太长 → 枪声过后脚步也被压着听不清。
类比: 松手的速度，太快一抖一抖，太慢一直捂着。
建议: 100~250ms 之间微调。""",
    "ex_limiter_release_ms": """限幅释放 —— 限幅器松开的速度（默认 80 ms）
作用: 尖峰被压住后放开的时间；太快有轻微抽吸感，太慢让后面的声音发闷。
建议: 60~120ms，一般不用动。""",
    "ex_low_shelf_freq": """低频转折频率 —— 从这个频率以下开始切（默认 180 Hz）
太低切不干净闷感，太高会伤枪声/爆炸的"厚度"。一般不用动。""",
    "ex_high_shelf_freq": """高频转折频率 —— 从这个频率以上开始切（默认 4000 Hz）
越低切得越多、声音越闷；嫌脚步变闷就往上调（如 5000）。""",
    "ex_auto_makeup": """自动补偿 —— 压缩削掉的响度自动补回（默认开）
作用: 压缩把大声压小了，整体响度会掉；打开后自动补上，输出响度稳定。
建议: 保持开启，否则每次改阈值/比例声音都会忽大忽小。""",
    "err_no_device_t": "设备未选择",
    "err_no_device_b": "输入设备需要虚拟声卡的 CABLE Output。\n"
                       "若下拉框里没有它，请先安装 VB-Cable：\n"
                       "程序文件夹 VBCABLE\\VBCABLE_Setup_x64.exe 右键管理员运行 → 装完重启电脑 → 点【刷新设备】。",
    "err_out_cable_t": "输出设备不能选虚拟声卡",
    "err_out_cable_b": "把处理后的声音再送回虚拟声卡会形成声音循环（啸叫）。\n"
                       "请在'播放到'里选择你的耳机/音箱。",
    "ask_input_t": "确认输入设备",
    "ask_input_b": "你选的输入不是虚拟声卡 CABLE Output，而是:\n「{name}」\n\n"
                   "本程序设计上抓的是虚拟声卡里的 PUBG 声音；\n"
                   "如果选了麦克风，耳机里会听到自己麦的声音。\n确定继续吗？",
    "err_start_t": "启动失败",
    "err_start_b": "{e}\n\n若提示找不到 CABLE Output，请先安装 VB-Cable。",
    "err_start_out_b": "输出流启动失败: {e}",
    "err_no_cable_in_t": "没有虚拟声卡（VB-Cable 未安装）",
    "err_no_cable_in_b": "【测试声音】的原理: 把测试信号播进虚拟声卡 CABLE Input\n"
                         "→ 程序抓取并处理 → 从你的耳机播出。\n"
                         "所以它不走你上面选的耳机，而是需要系统里存在 CABLE Input 设备。\n\n"
                         "当前系统里没有它，说明 VB-Cable 驱动还没装好。安装步骤:\n"
                         "1. 打开本程序文件夹里的 VBCABLE\\VBCABLE_Setup_x64.exe\n"
                         "2. 右键 → 以管理员身份运行 → 点 Install\n"
                         "3. 重启电脑\n"
                         "4. 回到本窗口点【刷新设备】，出现 CABLE Output 后再【启动】\n\n"
                         "当前系统里的输出设备:\n{list}",
    "info_need_start": "请先点【启动】，再点【测试声音】。",
    "err_test_t": "测试失败",
    "err_test_b": "{e}",
    "err_installer_t": "找不到安装程序",
    "err_installer_b": "未找到:\n{path}",
    "err_launch_t": "启动安装程序失败",
    "err_launch_b": "{e}",
    "info_install_t": "安装 VB-Cable（两步确认）",
    "info_install_b": "1. 屏幕会弹出 UAC 提示（用户账户控制）→ 点【是】\n"
                      "2. 出现 VB-Cable 安装窗口 → 点【Install Driver】按钮\n\n"
                      "装完后回到本窗口点【刷新设备】；若列表顶部没出现 CABLE Output，重启电脑再看。",
}

# ======================================================================
# English
# ======================================================================
STRINGS["en_US"] = {
    "title_suffix": "Tuner",
    "devices": " Devices ",
    "source_label": "Capture (recording device):",
    "out_label": "Playback (headphones):",
    "refresh": "Refresh",
    "install_vbcable": "Install VB-Cable",
    "hint_found": "CABLE Output found ✓ (top of the 'Capture' list) — next: Start → Test sound",
    "hint_hijack": "CABLE Output found ✓ but ⚠ the virtual cable became the system default input/output "
                   "(set automatically during installation) — set your default output back to headphones "
                   "and default input back to your microphone in Windows Sound settings, otherwise every "
                   "other app's audio and your mic get routed into the cable",
    "hint_missing": "CABLE Output not found. Seeing only microphones in the 'Capture' list is normal — "
                    "CABLE Output is also a recording device (it records what is played into the virtual "
                    "cable) and appears at the top of the same list once the driver is installed. "
                    "Click [Install VB-Cable] → UAC 'Yes' → installer 'Install Driver' → then [Refresh] "
                    "(reboot if it still doesn't show up)",
    "meters": " Live meters ",
    "m_in": "Input", "m_out": "Output", "m_comp": "Compression", "m_lim": "Limiter",
    "main_params": " Main parameters ",
    "adv_params": " Advanced (usually leave as-is) ",
    "btn_start": "Start", "btn_stop": "Stop", "btn_test": "Test sound",
    "chk_bypass": "Bypass compare", "btn_save": "Save settings", "btn_reset": "Defaults",
    "btn_help": "? Help",
    "preset_label": "Presets:",
    "preset_light": "Light · keep distance cues",
    "preset_balanced": "Balanced · default",
    "preset_strong": "Strong · night mode",
    "status_stopped": "Stopped",
    "status_priming": "Priming buffer…",
    "status_running": "Running | queue {q} | underruns {u} drops {d} overruns {o}",
    "status_bypass": " | [BYPASSED: raw audio]",
    "overview": """How to use:
1. Click [Start] (VB-Cable must be installed; if not, click [Install VB-Cable])
2. In game: Windows Settings → System → Sound → Volume mixer → PUBG → set its output device to CABLE Input
3. Fire a shot / run around, watch the meters, tune the sliders, click [Save settings]
4. Verify: click [Test sound] (a synthetic 'footsteps + gunshot' runs through the whole chain, volume is
   kept low; lower your system volume to ~30% first), or toggle [Bypass compare]
5. Finally turn your system volume DOWN — that is the whole point of hearing protection

[Why does 'Capture' only show microphones when we need CABLE Output?]
A virtual cable is a PAIR of devices, named from the cable's own point of view:
  · CABLE Input  = playback end → PUBG plays INTO it (shows up in output device lists)
  · CABLE Output = recording end → this app takes audio FROM it (shows up in recording lists, next to mics)
Think of a parcel locker: PUBG drops parcels into the deposit slot (Input), this app picks them up
from the collection slot (Output). So the app's "input" is the device named "Output".

Hover any parameter for a detailed explanation; click [? Help] to come back to this page.""",
    "lbl_pre_gain_db": "Pre-gain",
    "lbl_comp_threshold_db": "Threshold",
    "lbl_comp_ratio": "Ratio",
    "lbl_low_shelf_gain_db": "Low cut",
    "lbl_high_shelf_gain_db": "High cut",
    "lbl_limiter_ceiling_db": "Limiter ceiling",
    "lbl_comp_attack_ms": "Attack",
    "lbl_comp_release_ms": "Release",
    "lbl_limiter_release_ms": "Limiter release",
    "lbl_low_shelf_freq": "Low freq",
    "lbl_high_shelf_freq": "High freq",
    "chk_makeup": "Auto makeup (stable level)",
    "ex_pre_gain_db": """Pre-gain — overall level before processing (default +3 dB)
Purpose: lifts quiet sounds (footsteps, reloads) as a whole before the compressor.
Analogy: turning the mic up one notch before the meeting starts.
Advice: too much makes noise floor hissy and sound dull — back off 1~2 dB. Lowering your system
volume afterwards is what actually protects your hearing.""",
    "ex_comp_threshold_db": """Threshold — the loudness line where compression starts (default -18 dBFS)
Purpose: anything above the line gets pushed down; below it (footsteps) is untouched.
Analogy: a water-level alarm line — water above it gets pumped away.
Advice: gunshots still scary → lower it; can't tell far shots from near ones → raise it.""",
    "ex_comp_ratio": """Ratio — how much of the excess gets pushed back (default 2.5:1)
Purpose: above the threshold only 1/ratio survives. 2.5:1 = 2.5 dB over becomes 1 dB.
Analogy: a speeding fine — the more over, the harder it hurts.
Advice: higher = stronger "night mode" but worse distance cues. Light 2:1, strong 4:1.""",
    "ex_low_shelf_gain_db": """Low cut — how much of the "boomy/chest-punch" is removed (default -8 dB)
Why: grenades, explosions and vehicle rumbles concentrate their energy in the low end
(below ~200 Hz), which you feel in your chest rather than hear. A compressor only works on
volume, not timbre — an EQ cut is the right tool. After the cut explosions sound "crisp".
Advice: grenades still boomy → go to -12; game sounds thin/weak → move back toward 0.""",
    "ex_high_shelf_gain_db": """High cut — how much of the "piercing/harsh" is tamed (default -4 dB)
Why: that sharp whine after a grenade is PUBG's intentional "tinnitus" sound effect (several kHz) —
by design, not a bug. Cutting the highs dulls it noticeably and softens the overall bite.
Cost: footsteps get slightly duller too.
Advice: the whine still stings → go to -8; sounds muffled/unreal → move back toward 0.""",
    "ex_limiter_ceiling_db": """Limiter ceiling — the hard red line nothing may cross (default -3 dBFS)
Purpose: the final fuse — no explosion, however loud, ever exceeds it. This is the hearing-protection
guarantee.
Analogy: an elevator's ceiling — hit it and you stop.
Advice: -3 dBFS is right. If the 'Limiter' meter is constantly full, compression upstream is too
weak — tune threshold/ratio instead of lowering the ceiling.""",
    "ex_comp_attack_ms": """Attack — how fast compression kicks in after crossing the line (default 10 ms)
Purpose: too long → the first crack of a shot slips through; too short → transients get choked,
sound gets dull/mushy.
Advice: 8~15 ms is the usual compromise for shooters; normally leave it.""",
    "ex_comp_release_ms": """Release — how long until compression lets go (default 150 ms)
Purpose: too short → "pumping/breathing"; too long → footsteps after a shot stay suppressed.
Advice: fine-tune between 100~250 ms.""",
    "ex_limiter_release_ms": """Limiter release — how fast the limiter lets go (default 80 ms)
Purpose: too fast = slight pumping; too slow = muffled tail after each peak.
Advice: 60~120 ms; normally leave it.""",
    "ex_low_shelf_freq": """Low-corner frequency — the cut starts below this (default 180 Hz)
Too low won't clean the boom; too high thins out gunshots. Normally leave it.""",
    "ex_high_shelf_freq": """High-corner frequency — the cut starts above this (default 4000 Hz)
Lower = more taming but duller; if footsteps sound too dull, raise it (e.g. 5000).""",
    "ex_auto_makeup": """Auto makeup — automatically restores loudness removed by compression (default on)
Purpose: compression makes things quieter overall; makeup compensates so output level stays stable.
Advice: keep it on, otherwise output jumps whenever you change threshold/ratio.""",
    "err_no_device_t": "No device selected",
    "err_no_device_b": "The capture device must be the virtual cable's CABLE Output.\n"
                       "If it is not in the dropdown, install VB-Cable first:\n"
                       "right-click VBCABLE\\VBCABLE_Setup_x64.exe in this folder → Run as administrator → "
                       "reboot → click [Refresh].",
    "err_out_cable_t": "Output cannot be the virtual cable",
    "err_out_cable_b": "Feeding processed audio back into the virtual cable creates an audio loop "
                       "(howling).\nPick your headphones/speakers under 'Playback'.",
    "ask_input_t": "Confirm capture device",
    "ask_input_b": "Your capture device is not the virtual cable's CABLE Output but:\n\"{name}\"\n\n"
                   "This app is designed to capture PUBG audio from the virtual cable; capturing a "
                   "microphone means you will hear your own mic in the headphones.\nContinue anyway?",
    "err_start_t": "Start failed",
    "err_start_b": "{e}\n\nIf it says CABLE Output is missing, install VB-Cable first.",
    "err_start_out_b": "Playback stream failed to start: {e}",
    "err_no_cable_in_t": "No virtual cable (VB-Cable not installed)",
    "err_no_cable_in_b": "How [Test sound] works: a test signal is played INTO the virtual cable's "
                         "CABLE Input → captured and processed by this app → played out of your headphones.\n"
                         "It does not use the headphone you picked above — it needs a CABLE Input device "
                         "to exist.\n\nIt is missing, which means the VB-Cable driver is not installed yet:\n"
                         "1. Open VBCABLE\\VBCABLE_Setup_x64.exe in this folder\n"
                         "2. Right-click → Run as administrator → click Install\n"
                         "3. Reboot\n"
                         "4. Click [Refresh] here; once CABLE Output shows up, click [Start]\n\n"
                         "Output devices currently visible:\n{list}",
    "info_need_start": "Click [Start] first, then [Test sound].",
    "err_test_t": "Test failed",
    "err_test_b": "{e}",
    "err_installer_t": "Installer not found",
    "err_installer_b": "Missing:\n{path}",
    "err_launch_t": "Failed to launch installer",
    "err_launch_b": "{e}",
    "info_install_t": "Install VB-Cable (two confirmations)",
    "info_install_b": "1. A UAC prompt appears → click [Yes]\n"
                      "2. The VB-Cable installer window appears → click [Install Driver]\n\n"
                      "Then click [Refresh] here; if CABLE Output still isn't at the top of the list, reboot.",
}

# ======================================================================
# Русский
# ======================================================================
STRINGS["ru_RU"] = {
    "title_suffix": "Пульт",
    "devices": " Устройства ",
    "source_label": "Захват (устройство записи):",
    "out_label": "Вывод (наушники):",
    "refresh": "Обновить",
    "install_vbcable": "Установить VB-Cable",
    "hint_found": "CABLE Output найден ✓ (вверху списка «Захват») — далее: Пуск → Тест звука",
    "hint_hijack": "CABLE Output найден ✓, но ⚠ виртуальный кабель стал устройством по умолчанию "
                   "(устанавливается автоматически при инсталляции) — верните вывод по умолчанию на "
                   "наушники, а вход — на микрофон в настройках звука Windows, иначе звук всех других "
                   "программ и микрофон уйдут в кабель",
    "hint_missing": "CABLE Output не найден. То, что в списке «Захват» только микрофоны — нормально: "
                    "CABLE Output тоже устройство записи (он записывает то, что играет в виртуальный "
                    "кабель) и появится вверху этого же списка после установки драйвера. "
                    "Нажмите [Установить VB-Cable] → UAC «Да» → в установщике «Install Driver» → "
                    "затем [Обновить] (если не появился — перезагрузите ПК)",
    "meters": " Индикаторы ",
    "m_in": "Вход", "m_out": "Выход", "m_comp": "Компрессия", "m_lim": "Лимитер",
    "main_params": " Основные параметры ",
    "adv_params": " Дополнительные (обычно не трогать) ",
    "btn_start": "Пуск", "btn_stop": "Стоп", "btn_test": "Тест звука",
    "chk_bypass": "Сравнение (байпас)", "btn_save": "Сохранить", "btn_reset": "Сброс",
    "btn_help": "? Справка",
    "preset_label": "Пресеты:",
    "preset_light": "Лёгкий · дистанция слышна",
    "preset_balanced": "Сбалансированный",
    "preset_strong": "Сильный · ночной режим",
    "status_stopped": "Остановлено",
    "status_priming": "Заполнение буфера…",
    "status_running": "Работает | буфер {q} | недогрузки {u} сбросы {d} переполнения {o}",
    "status_bypass": " | [БАЙПАС: исходный звук]",
    "overview": """Как пользоваться:
1. Нажмите [Пуск] (нужен установленный VB-Cable; если нет — [Установить VB-Cable])
2. В игре: Параметры Windows → Система → Звук → Микшер громкости → PUBG → устройство вывода = CABLE Input
3. Стреляйте/бегайте, смотрите на индикаторы, крутите ползунки, нажмите [Сохранить]
4. Проверка: [Тест звука] (синтетические «шаги + выстрел» через всю цепочку, громкость снижена;
   сначала уберите общую громкость на ~30%) или переключатель [Сравнение]
5. В конце убавьте общую громкость — в этом и есть защита слуха

[Почему в «Захвате» только микрофоны, если нужен CABLE Output?]
Виртуальный кабель — ПАРА устройств, имена даны с точки зрения самого кабеля:
  · CABLE Input  = выход → PUBG играет В него (в списке устройств вывода)
  · CABLE Output = вход → программа берёт звук ИЗ него (в списке записи, рядом с микрофонами)
Как в пункте выдачи: PUBG кладёт посылку в ячейку приёма (Input), программа забирает из ячейки
выдачи (Output). Поэтому «вход» программы называется Output.

Наведите мышь на любой параметр — здесь появится описание; [? Справка] вернёт эту страницу.""",
    "lbl_pre_gain_db": "Предусиление",
    "lbl_comp_threshold_db": "Порог",
    "lbl_comp_ratio": "Соотношение",
    "lbl_low_shelf_gain_db": "Срез низа",
    "lbl_high_shelf_gain_db": "Срез верха",
    "lbl_limiter_ceiling_db": "Потолок",
    "lbl_comp_attack_ms": "Атака",
    "lbl_comp_release_ms": "Восстановление",
    "lbl_limiter_release_ms": "Восст. лимитера",
    "lbl_low_shelf_freq": "Частота низа",
    "lbl_high_shelf_freq": "Частота верха",
    "chk_makeup": "Авто-компенсация (стабильный уровень)",
    "ex_pre_gain_db": """Предусиление — общая громкость до обработки (по умолчанию +3 дБ).
Поднимает тихие звуки (шаги, перезарядку) целиком перед компрессором.
Слишком много → шумный фон и глухой звук, убавьте на 1–2 дБ. Защиту слуха даёт общая громкость.""",
    "ex_comp_threshold_db": """Порог — линия громкости, с которой начинается сжатие (-18 дБFS).
Выше линии — прижимается, ниже (шаги) — не трогается.
Выстрелы всё ещё пугают → ниже; не отличить дальний от ближнего → выше.""",
    "ex_comp_ratio": """Соотношение — сколько лишнего прижимается (2.5:1).
Выше порога остаётся 1/соотношения. Чем больше — тем «режим ночи» сильнее, но хуже дистанция.
Лёгкий 2:1, сильный 4:1.""",
    "ex_low_shelf_gain_db": """Срез низа — сколько «бубнения/удара в грудь» убрать (-8 дБ).
Гранаты, взрывы и гул машин несут энергию в низах — компрессор меняет громкость, но не тембр,
нужен EQ. Граната всё ещё бубнит → -12; звук стал плоским → к 0.""",
    "ex_high_shelf_gain_db": """Срез верха — сколько «резкости» убрать (-4 дБ).
Писк после гранаты — намеренный эффект «звона в ушах» в PUBG. Срез верха его притупляет.
Минус: шаги чуть глуше. Всё ещё режет → -8; звук глухой → к 0.""",
    "ex_limiter_ceiling_db": """Потолок лимитера — жёсткая красная линия (-3 дБFS). Ни один взрыв её не превысит —
это и есть гарантия защиты слуха. Если индикатор лимитера постоянно полный — усилите компрессию,
а не опускайте потолок.""",
    "ex_comp_attack_ms": """Атака — как быстро сжатие включается (10 мс). Долго — первый «треск» выстрела
просочится; быстро — звук станет глухим. 8–15 мс обычно норм.""",
    "ex_comp_release_ms": """Восстановление — как долго сжатие держится (150 мс). Коротко — «насос»,
долго — шаги после выстрела глушатся. Настройте в 100–250 мс.""",
    "ex_limiter_release_ms": """Восстановление лимитера (80 мс). 60–120 мс; обычно не трогать.""",
    "ex_low_shelf_freq": """Частота низа — срез начинается ниже этого (180 Гц). Обычно не трогать.""",
    "ex_high_shelf_freq": """Частота верха — срез начинается выше этого (4000 Гц). Глуше — поднимите (напр. 5000).""",
    "ex_auto_makeup": """Авто-компенсация — возвращает громкость, снятую компрессией (вкл.). Держите включённой.""",
    "err_no_device_t": "Устройство не выбрано",
    "err_no_device_b": "Устройством захвата должен быть CABLE Output виртуального кабеля.\n"
                       "Нет в списке? Установите VB-Cable: правый клик по VBCABLE\\VBCABLE_Setup_x64.exe → "
                       "запуск от администратора → перезагрузка → [Обновить].",
    "err_out_cable_t": "Вывод не может быть виртуальным кабелем",
    "err_out_cable_b": "Возврат обработанного звука в кабель создаст петлю (вой).\n"
                       "Выберите наушники/колонки в «Вывод».",
    "ask_input_t": "Подтвердите устройство захвата",
    "ask_input_b": "Выбран не CABLE Output, а:\n\"{name}\"\n\nПрограмма рассчитана на захват звука PUBG из "
                   "виртуального кабеля; микрофон = вы услышите себя.\nПродолжить?",
    "err_start_t": "Ошибка запуска",
    "err_start_b": "{e}\n\nЕсли CABLE Output отсутствует — сначала установите VB-Cable.",
    "err_start_out_b": "Поток вывода не запустился: {e}",
    "err_no_cable_in_t": "Нет виртуального кабеля (VB-Cable не установлен)",
    "err_no_cable_in_b": "Как работает [Тест звука]: сигнал играет В CABLE Input → программа захватывает и "
                         "обрабатывает → играет в наушниках.\nНужен именно CABLE Input, а не выбранные "
                         "наушники.\n\nЕго нет — драйвер VB-Cable не установлен:\n"
                         "1. Откройте VBCABLE\\VBCABLE_Setup_x64.exe\n2. Правый клик → от администратора → Install\n"
                         "3. Перезагрузка\n4. [Обновить], затем [Пуск]\n\n"
                         "Текущие устройства вывода:\n{list}",
    "info_need_start": "Сначала [Пуск], потом [Тест звука].",
    "err_test_t": "Тест не удался",
    "err_test_b": "{e}",
    "err_installer_t": "Установщик не найден",
    "err_installer_b": "Отсутствует:\n{path}",
    "err_launch_t": "Не удалось запустить установщик",
    "err_launch_b": "{e}",
    "info_install_t": "Установка VB-Cable (два подтверждения)",
    "info_install_b": "1. Появится окно UAC → [Да]\n2. Окно установщика VB-Cable → [Install Driver]\n\n"
                      "Затем [Обновить]; если CABLE Output не появился — перезагрузите ПК.",
}

# ======================================================================
# Español
# ======================================================================
STRINGS["es_ES"] = {
    "title_suffix": "Panel de ajustes",
    "devices": " Dispositivos ",
    "source_label": "Captura (dispositivo de grabación):",
    "out_label": "Salida (auriculares):",
    "refresh": "Actualizar",
    "install_vbcable": "Instalar VB-Cable",
    "hint_found": "CABLE Output encontrado ✓ (arriba de la lista 'Captura') — siguiente: Iniciar → Probar sonido",
    "hint_hijack": "CABLE Output encontrado ✓ pero ⚠ el cable virtual quedó como dispositivo predeterminado "
                   "de entrada/salida (se configura solo al instalar) — devuelve la salida predeterminada a "
                   "tus auriculares y la entrada a tu micrófono en la configuración de sonido de Windows, "
                   "o el audio de otras apps y tu micrófono irán al cable",
    "hint_missing": "No se encontró CABLE Output. Ver solo micrófonos en 'Captura' es normal: CABLE Output "
                    "también es un dispositivo de grabación (graba lo que se reproduce en el cable virtual) "
                    "y aparecerá arriba de esa lista cuando el driver esté instalado. Pulsa [Instalar "
                    "VB-Cable] → UAC 'Sí' → en el instalador 'Install Driver' → luego [Actualizar] "
                    "(si no aparece, reinicia)",
    "meters": " Medidores ",
    "m_in": "Entrada", "m_out": "Salida", "m_comp": "Compresión", "m_lim": "Limitador",
    "main_params": " Parámetros principales ",
    "adv_params": " Avanzados (no tocar normalmente) ",
    "btn_start": "Iniciar", "btn_stop": "Detener", "btn_test": "Probar sonido",
    "chk_bypass": "Comparar (bypass)", "btn_save": "Guardar", "btn_reset": "Predeterminados",
    "btn_help": "? Ayuda",
    "preset_label": "Preajustes:",
    "preset_light": "Suave · mantiene distancia",
    "preset_balanced": "Equilibrado",
    "preset_strong": "Fuerte · modo noche",
    "status_stopped": "Detenido",
    "status_priming": "Llenando búfer…",
    "status_running": "Activo | búfer {q} | subruns {u} descartes {d} overruns {o}",
    "status_bypass": " | [BYPASS: audio original]",
    "overview": """Cómo usar:
1. Pulsa [Iniciar] (necesita VB-Cable instalado; si no, pulsa [Instalar VB-Cable])
2. En el juego: Configuración de Windows → Sistema → Sonido → Mezclador de volumen → PUBG →
   dispositivo de salida = CABLE Input
3. Dispara / corre, mira los medidores, ajusta los deslizadores, pulsa [Guardar]
4. Verifica: [Probar sonido] (una señal sintética de 'pasos + disparo' pasa por toda la cadena,
   volumen bajo; baja antes el volumen del sistema a ~30%) o alterna [Comparar (bypass)]
5. Al final baja el volumen general del sistema — eso es la protección auditiva

[¿Por qué en 'Captura' solo hay micrófonos si se necesita CABLE Output?]
El cable virtual es un PAR de dispositivos nombrados desde el punto de vista del cable:
  · CABLE Input  = lado de reproducción → PUBG reproduce HACIA él (lista de salida)
  · CABLE Output = lado de grabación → esta app toma el audio DESDE él (lista de grabación)
Como un taquillero: PUBG deposita en la ranura de entrada (Input) y la app recoge por la de
salida (Output). Por eso la 'entrada' de la app se llama Output.

Pasa el ratón por un parámetro para ver su explicación; [? Ayuda] vuelve a esta página.""",
    "lbl_pre_gain_db": "Pre-ganancia",
    "lbl_comp_threshold_db": "Umbral",
    "lbl_comp_ratio": "Ratio",
    "lbl_low_shelf_gain_db": "Corte graves",
    "lbl_high_shelf_gain_db": "Corte agudos",
    "lbl_limiter_ceiling_db": "Techo limitador",
    "lbl_comp_attack_ms": "Ataque",
    "lbl_comp_release_ms": "Release",
    "lbl_limiter_release_ms": "Release limit.",
    "lbl_low_shelf_freq": "Frec. graves",
    "lbl_high_shelf_freq": "Frec. agudos",
    "chk_makeup": "Auto-maquillaje (nivel estable)",
    "ex_pre_gain_db": """Pre-ganancia — nivel general antes de procesar (+3 dB). Eleva los sonidos suaves
(pasos, recargas) antes del compresor. Demasiado → siseo y sonido apagado; reduce 1–2 dB.""",
    "ex_comp_threshold_db": """Umbral — línea de volumen donde empieza la compresión (-18 dBFS). Por encima se
reduce; por debajo (pasos) no se toca. Disparos aún fuertes → bajar; no distancias tiros → subir.""",
    "ex_comp_ratio": """Ratio — cuánto del exceso se reduce (2.5:1). Más alto = más 'modo noche' pero peor
percepción de distancia. Suave 2:1, fuerte 4:1.""",
    "ex_low_shelf_gain_db": """Corte de graves — cuánto del 'golpe sordo' se elimina (-8 dB). Granadas, explosiones
y motores concentran energía en graves; el compresor no cambia el timbre, hace falta EQ.
Granada aún sorda → -12; sonido plano → hacia 0.""",
    "ex_high_shelf_gain_db": """Corte de agudos — cuánta 'aspereza' se domina (-4 dB). El silbido tras la granada es
el efecto de 'tinnitus' intencional de PUBG. Cortar agudos lo embotella. Aún punza → -8; apagado → hacia 0.""",
    "ex_limiter_ceiling_db": """Techo del limitador — línea roja que nada supera (-3 dBFS): la garantía de protección
auditiva. Si el medidor del limitador está siempre lleno, mejora el umbral/ratio en vez de bajar el techo.""",
    "ex_comp_attack_ms": """Ataque — rapidez de reacción del compresor (10 ms). 8–15 ms suele estar bien.""",
    "ex_comp_release_ms": """Release — cuánto tarda en soltar (150 ms). Corto = 'bombeo'; largo = pasos apagados.
Ajusta entre 100–250 ms.""",
    "ex_limiter_release_ms": """Release del limitador (80 ms). 60–120 ms; normalmente no tocar.""",
    "ex_low_shelf_freq": """Frecuencia de graves — el corte empieza por debajo (180 Hz). Normalmente no tocar.""",
    "ex_high_shelf_freq": """Frecuencia de agudos — el corte empieza por encima (4000 Hz). ¿Pasos apagados? Sube (5000).""",
    "ex_auto_makeup": """Auto-maquillaje — recompensa el volumen quitado por la compresión (activado). Déjalo activo.""",
    "err_no_device_t": "Sin dispositivo seleccionado",
    "err_no_device_b": "El dispositivo de captura debe ser CABLE Output del cable virtual.\n"
                       "¿No aparece? Instala VB-Cable: clic derecho en VBCABLE\\VBCABLE_Setup_x64.exe → "
                       "ejecutar como administrador → reiniciar → [Actualizar].",
    "err_out_cable_t": "La salida no puede ser el cable virtual",
    "err_out_cable_b": "Devolver el audio procesado al cable crea un bucle (aullido).\nElige auriculares/altavoces en 'Salida'.",
    "ask_input_t": "Confirma el dispositivo de captura",
    "ask_input_b": "La captura no es CABLE Output sino:\n\"{name}\"\n\nLa app está diseñada para capturar "
                   "el audio de PUBG desde el cable virtual; un micrófono = oirás tu propia voz.\n¿Continuar?",
    "err_start_t": "Error al iniciar",
    "err_start_b": "{e}\n\nSi falta CABLE Output, instala primero VB-Cable.",
    "err_start_out_b": "El flujo de salida no arrancó: {e}",
    "err_no_cable_in_t": "Sin cable virtual (VB-Cable no instalado)",
    "err_no_cable_in_b": "Cómo funciona [Probar sonido]: una señal se reproduce EN CABLE Input → la app la "
                         "captura y procesa → sale por tus auriculares.\nNecesita que exista CABLE Input.\n\n"
                         "No existe: el driver VB-Cable no está instalado.\n1. Abre VBCABLE\\VBCABLE_Setup_x64.exe\n"
                         "2. Clic derecho → como administrador → Install\n3. Reinicia\n"
                         "4. [Actualizar] y luego [Iniciar]\n\nDispositivos de salida visibles:\n{list}",
    "info_need_start": "Pulsa primero [Iniciar] y luego [Probar sonido].",
    "err_test_t": "Prueba fallida",
    "err_test_b": "{e}",
    "err_installer_t": "Instalador no encontrado",
    "err_installer_b": "Falta:\n{path}",
    "err_launch_t": "No se pudo lanzar el instalador",
    "err_launch_b": "{e}",
    "info_install_t": "Instalar VB-Cable (dos confirmaciones)",
    "info_install_b": "1. Aparece UAC → [Sí]\n2. Ventana del instalador → [Install Driver]\n\n"
                      "Luego [Actualizar]; si no aparece CABLE Output, reinicia.",
}

# ======================================================================
# 日本語
# ======================================================================
STRINGS["ja_JP"] = {
    "title_suffix": "チューナー",
    "devices": " デバイス ",
    "source_label": "キャプチャ（録音デバイス）:",
    "out_label": "出力（ヘッドホン）:",
    "refresh": "再読み込み",
    "install_vbcable": "VB-Cable をインストール",
    "hint_found": "CABLE Output を検出 ✓（「キャプチャ」一覧の先頭）— 次: 開始 → テスト音",
    "hint_hijack": "CABLE Output を検出 ✓ ただし ⚠ 仮想ケーブルがシステム既定の入出力になっています"
                   "（インストール時に自動設定）。Windows のサウンド設定で、既定の出力をヘッドホンへ、"
                   "既定の入力をマイクへ戻してください。他アプリの音とマイクがケーブルに吸われます",
    "hint_missing": "CABLE Output が見つかりません。「キャプチャ」一覧にマイクしか無いのは正常です — "
                    "CABLE Output も録音デバイス（仮想ケーブルに入った音を録る側）で、ドライバ導入後は"
                    "同じ一覧の先頭に出ます。【VB-Cable をインストール】→ UAC「はい」→ インストーラの"
                    "「Install Driver」→【再読み込み】（出なければ PC を再起動）",
    "meters": " メーター ",
    "m_in": "入力", "m_out": "出力", "m_comp": "圧縮量", "m_lim": "リミッター",
    "main_params": " 主要パラメータ ",
    "adv_params": " 詳細（普段はそのまま） ",
    "btn_start": "開始", "btn_stop": "停止", "btn_test": "テスト音",
    "chk_bypass": "バイパス比較", "btn_save": "設定を保存", "btn_reset": "初期値",
    "btn_help": "? ヘルプ",
    "preset_label": "プリセット:",
    "preset_light": "軽め・距離感優先",
    "preset_balanced": "バランス（既定）",
    "preset_strong": "強め・ナイトモード",
    "status_stopped": "停止中",
    "status_priming": "バッファ準備中…",
    "status_running": "実行中 | バッファ{q} | アンダーラン{u} ドロップ{d} オーバーラン{o}",
    "status_bypass": " | [バイパス: 原音そのまま]",
    "overview": """使い方:
1.【開始】を押す（VB-Cable が必要。無ければ【VB-Cable をインストール】）
2. ゲーム内: Windows 設定 → システム → サウンド → 音量ミキサー → PUBG → 出力デバイスを CABLE Input に
3. 銃を撃つ/走る、メーターを見ながらスライダー調整、【設定を保存】
4. 確認:【テスト音】（合成した「足音+銃声」が処理チェーンを通る。音量は控えめ。先にシステム音量を
   30% 程度に）や【バイパス比較】で切替
5. 最後にシステム音量を下げる — これが聴力保護の目的

【「キャプチャ」にマイクしか無いのに CABLE Output が必要なのは?】
仮想ケーブルはデバイスのペアで、名前はケーブル側の視点です:
  · CABLE Input  = 再生側 → PUBG がここへ音を「入れる」（出力一覧に出る）
  · CABLE Output = 録音側 → 本アプリがここから音を「取る」（録音一覧に出る）
宅配ロックアーのように、PUBG が投入口(Input)へ入れ、アプリが取出口(Output)から取るイメージ。

パラメータにマウスを載せると説明が出ます。【? ヘルプ】でこのページに戻ります。""",
    "lbl_pre_gain_db": "プリゲイン",
    "lbl_comp_threshold_db": "スレッショルド",
    "lbl_comp_ratio": "レシオ",
    "lbl_low_shelf_gain_db": "低域カット",
    "lbl_high_shelf_gain_db": "高域カット",
    "lbl_limiter_ceiling_db": "リミッター上限",
    "lbl_comp_attack_ms": "アタック",
    "lbl_comp_release_ms": "リリース",
    "lbl_limiter_release_ms": "リリース(リム)",
    "lbl_low_shelf_freq": "低域周波数",
    "lbl_high_shelf_freq": "高域周波数",
    "chk_makeup": "自動メイクアップ（音量安定）",
    "ex_pre_gain_db": """プリゲイン — 処理前の全体音量（既定 +3 dB）。足音などの小さい音を先に持ち上げます。
強すぎるとノイズが目立ち音が濁るので 1〜2 dB 戻す。聴力保護の本体はシステム音量を下げること。""",
    "ex_comp_threshold_db": """スレッショルド — 圧縮が始まる音量の線（既定 -18 dBFS）。線の上は押さえられ、
下（足音）は無傷。銃声がまだ怖い → 下げる。遠近の区別が付かない → 上げる。""",
    "ex_comp_ratio": """レシオ — 超過分をどれだけ押さえるか（2.5:1）。大きいほどナイトモードだが距離感が落ちる。
軽め 2:1、強め 4:1。""",
    "ex_low_shelf_gain_db": """低域カット — 「こもった胸に響く感」をどれだけ削るか（既定 -8 dB）。
グレネード・爆発・車の轟音のエネルギーは低域に集中。コンプレッサーは音量しか変えられず、
音色は EQ で切るしかない。まだ籠もる → -12。音が薄い → 0 へ戻す。""",
    "ex_high_shelf_gain_db": """高域カット — 「キンキン刺す感」をどれだけ抑えるか（既定 -4 dB）。
グレネード後のキーン音は PUBG が意図的に入れた「耳鳴り」演出です。まだ刺さる → -8。
こもって現実感がない → 0 へ戻す。""",
    "ex_limiter_ceiling_db": """リミッター上限 — 何物も越えられない赤線（既定 -3 dBFS）。これが聴力保護の保証。
リミッターメーターが常に満杯なら、上限ではなくスレッショルド/レシオを強めましょう。""",
    "ex_comp_attack_ms": """アタック — 閾値を越えてから圧縮が効くまでの時間（既定 10 ms）。8〜15 ms が無難。""",
    "ex_comp_release_ms": """リリース — 圧縮が緩むまでの時間（既定 150 ms）。短いとポンピング、長いと銃声後の
足音が塞がれる。100〜250 ms で調整。""",
    "ex_limiter_release_ms": """リミッターのリリース（既定 80 ms）。60〜120 ms。普段は触らなくて OK。""",
    "ex_low_shelf_freq": """低域周波数 — これ以下をカット（既定 180 Hz）。普段はそのまま。""",
    "ex_high_shelf_freq": """高域周波数 — これ以上をカット（既定 4000 Hz）。足音が籠もるなら上げる（例 5000）。""",
    "ex_auto_makeup": """自動メイクアップ — 圧縮で失われた音量を自動補完（既定オン）。オン推奨。""",
    "err_no_device_t": "デバイス未選択",
    "err_no_device_b": "キャプチャには仮想ケーブルの CABLE Output が必要です。\n"
                       "一覧に無い場合は先に VB-Cable をインストール: フォルダ内 VBCABLE\\VBCABLE_Setup_x64.exe を"
                       "右クリック→管理者として実行→再起動→【再読み込み】。",
    "err_out_cable_t": "出力に仮想ケーブルは選べません",
    "err_out_cable_b": "処理後の音を仮想ケーブルへ戻すと音のループ（ハウリング）が起きます。\n"
                       "「出力」にはヘッドホン/スピーカーを選んでください。",
    "ask_input_t": "キャプチャデバイスの確認",
    "ask_input_b": "選択されたのは CABLE Output ではなく:\n「{name}」\n\n本アプリは仮想ケーブルから PUBG の音を"
                   "取る設計です。マイクを選ぶと自分の声がヘッドホンから聞こえます。\n続けますか？",
    "err_start_t": "開始に失敗",
    "err_start_b": "{e}\n\nCABLE Output が無いと言われたら、先に VB-Cable をインストールしてください。",
    "err_start_out_b": "出力ストリームの開始に失敗: {e}",
    "err_no_cable_in_t": "仮想ケーブルなし（VB-Cable 未導入）",
    "err_no_cable_in_b": "【テスト音】の仕組み: テスト信号を仮想ケーブルの CABLE Input へ再生 → アプリが"
                         "キャプチャして処理 → ヘッドホンから出る。\n上で選んだヘッドホンは使わず、CABLE Input が"
                         "存在する必要があります。\n\n無い = VB-Cable ドライバ未導入:\n"
                         "1. フォルダ内 VBCABLE\\VBCABLE_Setup_x64.exe を開く\n"
                         "2. 右クリック→管理者として実行→Install\n3. PC 再起動\n"
                         "4.【再読み込み】→ CABLE Output が出たら【開始】\n\n"
                         "現在の出力デバイス:\n{list}",
    "info_need_start": "先に【開始】を押してから【テスト音】をどうぞ。",
    "err_test_t": "テスト失敗",
    "err_test_b": "{e}",
    "err_installer_t": "インストーラが見つかりません",
    "err_installer_b": "不足:\n{path}",
    "err_launch_t": "インストーラを起動できません",
    "err_launch_b": "{e}",
    "info_install_t": "VB-Cable のインストール（確認 2 回）",
    "info_install_b": "1. UAC が出たら【はい】\n2. VB-Cable のインストール画面で【Install Driver】\n\n"
                      "その後【再読み込み】。CABLE Output が出なければ PC を再起動。",
}


def resolve(code):
    """把 "auto" 或近似语言代码解析成受支持的语言。"""
    if code and code != "auto" and code in STRINGS:
        return code
    lang = None
    try:
        import ctypes
        primary = ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0xFF
        lang = {0x04: "zh", 0x09: "en", 0x0a: "es", 0x11: "ja", 0x19: "ru"}.get(primary)
    except Exception:
        try:
            import locale
            lang = (locale.getdefaultlocale()[0] or "")[:2].lower()
        except Exception:
            lang = None
    return {"zh": "zh_CN", "en": "en_US", "ru": "ru_RU", "es": "es_ES", "ja": "ja_JP"}.get(lang, "en_US")


def strings(code):
    """返回该语言的有效字典（缺失键回退 en_US，再回退 zh_CN）。"""
    base = dict(STRINGS["en_US"])
    base.update(STRINGS["zh_CN"])   # 兜底第二层
    if code == "zh_CN":
        return STRINGS["zh_CN"]
    t = dict(base)
    t.update(STRINGS.get(code, {}))
    return t
