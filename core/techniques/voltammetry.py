"""Voltammetry definitions, traced to chi660e.chm."""
from core.techniques.schema import (Technique, number as N, potential as E, quiet as Q,
                                    sensitivity as S, auxiliary as A, polarity as P,
                                    repeat as R, choice, variant, open_circuit)


def increment(maximum=.05):
    return N("incre", "电位增量 (V)", .005, .001, maximum)


def scan(maximum=20000):
    return N("v", "扫描速率 (V/s)", .1 if maximum >= .1 else .001, 1e-6, maximum)


def endpoint():
    return (E(), E("ef", "终止电位 (V)", 1))


CV = Technique("CV", "循环伏安法", "cv", "hidd_dialog_par_cv900c.htm", (
    E(), E("eh", "电位上限 (V)", 1), E("el", "电位下限 (V)", 0),
    E("ef", "终止电位 (V)", 0), P(), scan(10000),
    N("cl", "扫描段数（每段半个周期）", 2, 1, 1000000, integer=True),
    N("si", "采样电位间隔 (V)", .001, .001, .064), Q(), S(),
    choice("final_enable", "在终止电位结束", False,
           [(False, "关闭", "efoff"), (True, "开启", "efon")]), A(),
    N("capacitance", "用于估算灵敏度的电容量 (F)", None, 1e-18, 1e12,
      optional=True, local=True, help="选择自动灵敏度时，按已有电容量算法估算量程。"), R()),
    "扫描段数为半周期数。自动灵敏度切换仅适用于扫描速率 ≤ 0.01 V/s；提供电容量时使用本软件估算量程。",
    summary_keys=("ei", "eh", "v", "cl"))

LSV = Technique("LSV", "线性扫描伏安法", "lsv", "hidd_dialog_par_lsv6c.htm", (
    variant("lsv", [("lsv", "线性扫描伏安"), ("lssv", "线性扫描溶出伏安")]),
    *endpoint(), scan(), N("si", "采样电位间隔 (V)", .001, 1e-6, .064), Q(), S(), A(), R()))
SCV = Technique("SCV", "阶梯伏安法", "scv", "hidd_dialog_par_scv6c.htm", (
    variant("scv", [("scv", "阶梯伏安"), ("scp", "阶梯极谱"), ("scsv", "阶梯溶出伏安")]),
    *endpoint(), increment(), N("cl", "扫描段数", 1, 1, 1000, integer=True),
    N("sw", "采样宽度 (s)", .01, 1e-4, 50),
    N("prod", "阶梯周期 (s)", .1, .001, 50), Q(), S(False), R()))
TAFEL = Technique("TAFEL", "塔菲尔曲线", "tafel", "hidd_dialog_par_tafel6c.htm", (
    *endpoint(), increment(), N("cl", "扫描段数", 1, 1, 2, integer=True), scan(.01),
    N("ht", "终止电位保持时间 (s)", 0, 0, 100000), Q(), S(), R()))


def pulsed(code, name, aliases, fields):
    return Technique(code, name, code.lower(), f"hidd_dialog_par_{code.lower()}6c.htm", (
        variant(code.lower(), aliases), *endpoint(), increment(), *fields, Q(), S(False), R()))


DPV = pulsed("DPV", "差分脉冲伏安法", [("dpv", "差分脉冲伏安"), ("dpp", "差分脉冲极谱"),
             ("dpsv", "差分脉冲溶出伏安")], (
    N("amp", "脉冲幅度 (V)", .05, -.5, .5, help="幅度绝对值不得小于 0.001 V。"),
    N("pw", "脉冲宽度 (s)", .05, .001, 10), N("sw", "采样宽度 (s)", .01, 1e-4, 10),
    N("prod", "脉冲周期 (s)", .2, .01, 50)))
NPV = pulsed("NPV", "常规脉冲伏安法", [("npv", "常规脉冲伏安"), ("npp", "常规脉冲极谱"),
             ("npsv", "常规脉冲溶出伏安")], (
    N("pw", "脉冲宽度 (s)", .05, .001, 10), N("sw", "采样宽度 (s)", .01, 1e-4, 10),
    N("prod", "脉冲周期 (s)", .2, .01, 50)))
DNPV = pulsed("DNPV", "差分常规脉冲伏安法", [("dnpv", "差分常规脉冲伏安"), ("dnpp", "差分常规脉冲极谱"),
              ("dnpsv", "差分常规脉冲溶出伏安")], (
    N("amp", "脉冲幅度 (V)", .05, .001, .5),
    N("pw1", "第一脉冲宽度 (s)", .01, .001, .02),
    N("pw2", "第二脉冲宽度 (s)", .01, .001, .02),
    N("sw", "采样宽度 (s)", .005, .001, .5), N("prod", "脉冲周期 (s)", .1, .05, 50),
    open_circuit(label="第一步开路")))
SWV = pulsed("SWV", "方波伏安法", [("swv", "方波伏安"), ("swsv", "方波溶出伏安")], (
    N("amp", "方波幅度（峰峰值的一半）(V)", .025, .001, .5),
    N("freq", "方波频率 (Hz)", 25, 1, 100000)))


def ac(code, name, aliases, maximum):
    return Technique(code, name, code.lower(), f"hidd_dialog_par_{code.lower()}6c.htm", (
        variant(code.lower(), aliases), *endpoint(), increment(),
        N("amp", "交流幅度（峰峰值的一半）(V)", .01, .001, .5),
        N("freq", "交流频率 (Hz)", 10, .1, maximum),
        N("prod", "采样周期 (s)", 1, .1, 50), Q(), S(),
        choice("ibias", "直流偏置", None, [(0, "关闭", None), (1, "range", None), (2, "开启", None)],
               optional=True, help="界面枚举与宏 ibias 数值的对应关系未在 CHM 中说明；需要已确认的映射。"), R()))


ACV = ac("ACV", "交流伏安法", [("acv", "交流伏安"), ("acp", "交流极谱"), ("acsv", "交流溶出伏安")], 10000)
SHACV = ac("SHACV", "二次谐波交流伏安法", [("shacv", "二次谐波交流伏安"), ("shacp", "二次谐波交流极谱"),
             ("shacsv", "二次谐波交流溶出伏安")], 5000)
FTACV = Technique("FTACV", "傅里叶变换交流伏安法", None, "hidd_dialog_par_ftacv.htm", (
    *endpoint(), N("freq", "交流频率 (Hz)", 10, .1, 50, command=None),
    N("amp", "交流幅度 (V)", .01, .001, .5, command=None),
    choice("total_points", "总采样点数", 8192,
           [(v, str(v), None) for v in (8192, 16384, 32768, 65536)]),
    choice("points_per_sine", "每个正弦周期的采样点数", 32,
           [(v, str(v), None) for v in (4, 8, 16, 32, 64, 128, 256)]),
    N("cl", "扫描段数", 1, 1, 2, integer=True, command=None), Q(), S(False), R()),
    "CHM 提供完整参数说明，但未列出本方法的专用宏命令；请在设置中补充经 CHI 软件确认的命令映射。")

SSF_FIELDS = []
for i in range(1, 7):
    SSF_FIELDS.extend((E(f"ei{i}", f"扫描 {i}：起始电位 (V)"),
                       E(f"ef{i}", f"扫描 {i}：终止电位 (V)", 1),
                       N(f"v{i}", f"扫描 {i}：速率 (V/s)", .1, 1e-4, 50),
                       E(f"es{i}", f"阶跃 {i}：电位 (V)"),
                       N(f"st{i}", f"阶跃 {i}：时间 (s)", 0, 0, 10000)))
SSF = Technique("SSF", "扫描阶跃函数", "ssf", "hidd_dialog_par_ssf.htm", (
    E(), N("si", "扫描采样间隔 (V)", .001, .001, .05),
    N("st", "阶跃采样间隔 (s)", .01, .0001, 1), Q(), S(False), *SSF_FIELDS, R()))
HMV = Technique("HMV", "流体动力调制伏安法", "hmv", "hidd_dialog_par_hmv6c.htm", (
    *endpoint(), increment(.02), N("rpm", "中心转速 (rpm)", 1000, 0, 10000),
    N("freq", "调制频率 (Hz)", 1, 1, 5), N("modamp", "转速调制幅度 (rpm)", 100, 0, 3600),
    N("cl", "每个电位的调制周期数", 1, 1, 10, integer=True), Q(), S(False), R()))

TECHNIQUES = (CV, LSV, SCV, TAFEL, DPV, NPV, DNPV, SWV, ACV, SHACV, FTACV, HMV, SSF)
