"""Impedance techniques and explicit macro mappings."""
from core.techniques.schema import (Technique, number as N, potential as E, quiet as Q,
                                    repeat as R, choice, sensitivity)


def bias():
    return choice("ibias", "直流偏置", None,
                  [(0, "关闭", None), (1, "range", None), (2, "开启", None)], optional=True,
                  help="CHM 未明确界面三种选项与宏 ibias 0–4 的对应关系，启用前需补充映射。")


def sens():
    field = sensitivity()
    return choice("sens", "灵敏度", "auto",
                  [("auto", "自动", "impautosens"), *field.choices[1:]], command="sens")


EIS_EXTRA = [choice("mode", "高频测量方式", "ft", [
    ("ft", "傅里叶变换 (FT)", "impft"), ("single", "单频", "impsf"),
    ("galv", "恒流 (Galv.)", None)]),
    N("average_high", "平均因子（1 kHz–1 MHz）", None, .1, 4, command=None, optional=True),
    N("average_low", "平均因子（1–999 Hz）", None, 1, 256, integer=True, command=None, optional=True),
    # The band labels of cl1..cl5 in the legacy macro table differ from the
    # parameter page. Do not silently equate the two lists.
    N("cycles_01_1", "测量周期数（0.1–1 Hz）", None, 1, 25, integer=True, command=None, optional=True),
    N("cycles_001_01", "测量周期数（0.01–0.1 Hz）", None, 1, 25, integer=True, command=None, optional=True),
    N("cycles_0001_001", "测量周期数（0.001–0.01 Hz）", None, 1, 25, integer=True, command=None, optional=True),
    N("cycles_00001_0001", "测量周期数（0.0001–0.001 Hz）", None, 1, 16, integer=True, command=None, optional=True),
    N("cycles_000001_00001", "测量周期数（0.00001–0.0001 Hz）", None, 1, 4, integer=True, command=None, optional=True),
    N("points_per_decade", "每十倍频程点数", None, 0, 100, integer=True, command=None, optional=True), bias()]
for i in range(11):
    EIS_EXTRA.append(N(f"impsens{i}", f"手动灵敏度分段 {i} (A/V)", None, 1e-12, .1,
                       optional=True, help="分段频率范围见 CHM 的 IMP 宏命令页。"))
EIS = Technique("EIS", "交流阻抗谱", "imp", "hidd_dialog_par_imp5a.htm", (
    choice("use_ocp", "直流电位来源", True, [(True, "开路电位", "eio"),
                                              (False, "指定初始电位", None)], local=True),
    E(), N("fh", "最高频率 (Hz)", 1e6, 1e-4, 2e6),
    N("fl", "最低频率 (Hz)", .01, 1e-5, 1e5),
    N("amp", "交流幅度 (V)", .005, 1e-5, .7), Q(), sens(), *EIS_EXTRA, R()),
    "平均因子、频率分段周期数等参数页选项与旧宏表不完全对应；未设置的选项沿用 CHI 软件设置。",
    summary_keys=("fh", "fl", "amp", "use_ocp"))
IMPT = Technique("IMPT", "阻抗—时间曲线", "impt", "hidd_dialog_par_impt6c.htm", (
    E(), N("amp", "交流幅度 (V)", .005, .0001, 1.5),
    N("freq", "交流频率 (Hz)", 10, .0001, 1e6),
    N("si", "采样间隔 (s)", 5, 1, 20000), N("st", "运行时间 (s)", 100, 1, 500000),
    N("cl1", "低于 10 Hz 的测量周期数", 1, 1, 100, integer=True), Q(), sens(), bias(), R()))
IMPE = Technique("IMPE", "阻抗—电位曲线", "impe", "hidd_dialog_par_impe6c.htm", (
    E(), E("ef", "终止电位 (V)", 1), N("incre", "电位增量 (V)", .01, .001, .25),
    N("amp", "交流幅度 (V)", .005, .001, 1.5),
    N("freq", "交流频率 (Hz)", 10, .0001, 1e5),
    N("cl1", "低于 10 Hz 的测量周期数", 1, 1, 100, integer=True), Q(), sens(), bias(), R()))

TECHNIQUES = (EIS, IMPT, IMPE)
