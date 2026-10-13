"""Current-controlled experiments, PSA, noise and open circuit."""
from core.techniques.schema import (Technique, number as N, potential as E, quiet as Q,
                                    auxiliary as A, polarity as P, repeat as R,
                                    choice, sensitivity as S)


CP = Technique("CP", "计时电位法（恒流充放电）", "cp", "hidd_dialog_par_cp6c.htm", (
    N("ic", "阴极电流幅值 (A)", 1e-4, 0, .25),
    N("ia", "阳极电流幅值 (A)", 1e-4, 0, .25),
    E("eh", "电位上限 (V)", 1), N("heht", "上限电位保持时间 (s)", 0, 0, 100000),
    E("el", "电位下限 (V)", 0), N("leht", "下限电位保持时间 (s)", 0, 0, 100000),
    N("tc", "阴极段时间 (s)", 10, .005, 100000),
    N("ta", "阳极段时间 (s)", 10, .005, 100000), P("首段电流极性"),
    N("si", "数据存储间隔 (s)", .0025, .0001, 500),
    N("cl", "段数（每段半个周期）", 1, 1, 1000000, integer=True),
    choice("priority", "电流切换优先条件", "potential", [
        ("potential", "电位优先", "prioe"), ("time", "时间优先", "priot")]), A(), R()),
    "电流可以为 0。零电流段适合观察电压衰减，但 CHM 未确认其对电极断开。时间优先时仍会在触及电位边界后切换。"
    "电流幅值按 600E 无外接电流放大器的宏范围限制为 0–0.25 A；超过 400 段仅保存前 400 段数据。",
    presets=(("零电流观察预设", dict(ic=0, ia=0, eh=1.1, el=-.1, heht=0, leht=0,
                 tc=3600, ta=3600, pn="n", si=1, cl=1, priority="time", aux=False, repeat=1)),),
    summary_keys=("ic", "ia", "priority", "cl"))
CPCR = Technique("CPCR", "线性变流计时电位法", "cpcr", "hidd_dialog_par_cpcr9c.htm", (
    N("ic", "初始电流 (A)", 0, 0, .25), N("ia", "终止电流 (A)", .001, 0, .25),
    N("v", "电流扫描速率 (A/s)", 1e-4, 1e-12, .1),
    E("eh", "电位上限 (V)", 1), E("el", "电位下限 (V)", 0),
    N("si", "数据存储间隔 (s)", .0025, .0001, 500), R()),
    "电流范围采用本文件宏表中适用于无外接电流放大器的 0–0.25 A 范围。")
ISTEP_FIELDS = []
for i in range(1, 13):
    ISTEP_FIELDS.extend((N(f"is{i}", f"步骤 {i}：电流 (A)", 1e-4 if i == 1 else 0, -.25, .25),
                         N(f"st{i}", f"步骤 {i}：时间 (s)", 10 if i == 1 else 0, 0, 10000)))
ISTEP = Technique("ISTEP", "多电流阶跃", "istep", "hidd_dialog_par_cpcs9c.htm", (
    E("eh", "电位上限 (V)", 1), E("el", "电位下限 (V)", 0),
    N("si", "采样间隔 (s)", .01, 1e-5, 1),
    N("cl", "循环次数", 1, 1, 10000, integer=True), *ISTEP_FIELDS, R()),
    "界面方法名为 Multi-Current Steps，宏技术名为 istep。无外接电流放大器时电流限制为 ±0.25 A。")
PSA = Technique("PSA", "电位溶出分析", "psa", "hidd_dialog_par_psa6b.htm", (
    E("depe", "沉积／预充电电位 (V)", 1),
    N("dept", "沉积／预充电时间 (s)", 60, 0, 1000000),
    E("ef", "终止电位 (V)", .1), N("i", "剥离电流 (A)", 0, 0, .25),
    N("si", "采样间隔 (s)", 1, .0001, 50), Q(), R()),
    "剥离电流设为 0 时对电极断开，可用于预充电后开路自放电。到达终止电位时结束。充电设定值不保证开路首点恰好相同。")
ECN = Technique("ECN", "电化学噪声", "ecn", "hidd_dialog_par_ecn6c.htm", (
    N("si", "采样间隔 (s)", .1, .1, 10),
    N("st", "运行时间 (s)", 60, 10, 100000), Q(), S(False, minimum=1e-9),
    choice("gain", "电位增益", 1, [(v, str(v), f"ecngain{v}") for v in (1, 10, 100, 1000)]),
    choice("mode", "测量信号", "both", [("current", "电流", "ecni"),
          ("potential", "电位", "ecne"), ("both", "电流与电位", "ecn2")]), R()))
OCPT = Technique("OCPT", "开路电位—时间曲线", "ocpt", "hidd_dialog_par_ocpt6a.htm", (
    N("st", "运行时间 (s)", 3600, 1, 500000),
    N("si", "采样间隔 (s)", 1, .0025, 50),
    E("eh", "电位上限 (V)", 1.1), E("el", "电位下限 (V)", -.1), R()),
    "对电极断开，记录工作与参比电极的电位差。无预充电参数；到达电位上／下限时提示警告，不是自动停止条件。")

TECHNIQUES = (CP, CPCR, ISTEP, PSA, ECN, OCPT)
