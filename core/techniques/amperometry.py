"""Potential steps and amperometric methods."""
from core.techniques.schema import (Technique, number as N, potential as E, quiet as Q,
                                    sensitivity as S, auxiliary as A, polarity as P,
                                    repeat as R, scales, open_circuit, choice)


CA = Technique("CA", "计时电流法", "ca", "hidd_dialog_par_ca6c.htm", (
    E(), E("eh", "电位上限 (V)", 1), E("el", "电位下限 (V)"), P(),
    N("cl", "电位阶跃数", 2, 1, 320, integer=True),
    N("pw", "脉冲宽度 (s)", 1, 1e-4, 1000),
    N("si", "采样间隔 (s)", .01, 1e-6, 10), Q(), S(False), A(), R()))
CC = Technique("CC", "计时库仑法", "cc", "hidd_dialog_par_cc6c.htm", (
    E(), E("ef", "终止电位 (V)", 1),
    N("cl", "电位阶跃数", 2, 1, 320, integer=True),
    N("pw", "脉冲宽度 (s)", 1, 1e-4, 1000),
    N("si", "采样间隔 (s)", .01, 1e-6, 10), Q(), S(False), R()))
IT = Technique("IT", "电流—时间曲线", "i-t", "hidd_dialog_par_it6c.htm", (
    E(default=1), N("si", "采样间隔 (s)", .1, 1e-6, 50),
    N("st", "运行时间 (s)", 60, .001, 500000), Q(), scales(), S(False), A(), R()),
    summary_keys=("ei", "st", "qt", "sens"))
STEP_FIELDS = []
for i in range(1, 13):
    STEP_FIELDS.extend((E(f"es{i}", f"步骤 {i}：电位 (V)", 1 if i == 1 else 0),
                        N(f"st{i}", f"步骤 {i}：时间 (s)", 1 if i == 1 else 0, 0, 10000)))
STEP = Technique("STEP", "多电位阶跃", "step", "hidd_dialog_par_step6c.htm", (
    E(), N("cl", "循环次数", 1, 1, 10000, integer=True),
    N("si", "采样间隔 (s)", .01, 1e-4, 1), Q(), S(False), *STEP_FIELDS,
    # E1 on/off is documented as a multipotentiostat command only.
    choice("e1_on", "工作电极 1 开关（需对应仪器支持）", None,
           [(False, "关闭", None), (True, "开启", None)], optional=True), R()))
BE = Technique("BE", "控制电位电解库仑法", "be", "hidd_dialog_par_be6c.htm", (
    E(label="电解电位 (V)", default=1),
    N("iratio", "终止电流比例 (%)", 1, 0, 100),
    N("si", "数据存储间隔 (s)", 1, .01, 100),
    E("bepe", "预电解电位 (V)"), N("bept", "预电解时间 (s)", 0, 0, 1000000), R()),
    "达到终止电流比例时结束，耗时无法由设置值确定。")

UNMAPPED_NOTE = "CHM 未列出此方法的专用宏命令；参数可以保存，导出前需在设置中补充经 CHI 软件确认的映射。"


def pulse_fields(prefix="", label=""):
    return (N(prefix + "clean_e", label + "清洗电位 (V)", 0, -10, 10, command=None),
            N(prefix + "clean_t", label + "清洗时间 (s)", 0, 0, 32, command=None),
            N(prefix + "pulse_e1", label + "第一脉冲电位 (V)", .1, -10, 10, command=None),
            N(prefix + "pulse_t1", label + "第一脉冲时间 (s)", .1, .01, 32, command=None),
            N(prefix + "pulse_e2", label + "第二脉冲电位 (V)", .2, -10, 10, command=None),
            N(prefix + "pulse_t2", label + "第二脉冲时间 (s)", .1, .01, 32, command=None),
            open_circuit(prefix + "open_clean", label + "清洗步骤开路"))


DPA = Technique("DPA", "差分脉冲安培法", None, "hidd_dialog_par_dpa6c.htm", (
    E(), *pulse_fields(), N("cl", "循环次数", 10, 10, 100000, integer=True, command=None),
    Q(), scales(), S(False), R()), UNMAPPED_NOTE)
DDPA = Technique("DDPA", "双差分脉冲安培法", None, "hidd_dialog_par_ddpa6c.htm", (
    E(), *pulse_fields("first_", "第一组："), *pulse_fields("second_", "第二组："),
    N("cl", "循环次数", 10, 10, 100000, integer=True, command=None),
    Q(), scales(), S(False), R()), UNMAPPED_NOTE)
TPA = Technique("TPA", "三脉冲安培法", None, "hidd_dialog_par_tpa6c.htm", (
    E(), E("ef", "终止电位 (V)", 1),
    N("pulse_e1", "第一脉冲电位 (V)", 0, -10, 10, command=None),
    N("pulse_t1", "第一脉冲时间 (s)", 0, 0, 32, command=None),
    open_circuit(label="第一步开路"),
    N("pulse_e2", "第二脉冲电位 (V)", 0, -10, 10, command=None),
    N("pulse_t2", "第二脉冲时间 (s)", 0, 0, 32, command=None),
    N("pulse_e3", "第三脉冲电位 (V)", .1, -10, 10, command=None),
    N("pulse_t3", "第三脉冲时间 (s)", .1, .01, 32, command=None),
    N("incre", "第三脉冲电位增量 (V)", 0, 0, .02, command=None),
    N("cl", "循环次数", 10, 10, 100000, integer=True, command=None),
    Q(), scales(), S(False), R()), UNMAPPED_NOTE)
IPAD_FIELDS = []
for key, label, tmin, potential in (
        ("start", "步骤 1：起始", .05, 0), ("forward", "步骤 2：正向扫描", .15, .1),
        ("reverse", "步骤 3：反向扫描", .15, 0), ("hold", "步骤 4：保持", .05, 0),
        ("oxidation", "步骤 5：氧化", .05, .5), ("reduction", "步骤 6：还原", .05, -.5)):
    IPAD_FIELDS.extend((N(key + "_e", label + "电位 (V)", potential, -3.276, 3.276, command=None),
                        N(key + "_t", label + "时间 (s)", tmin, tmin, 1, command=None)))
IPAD = Technique("IPAD", "积分脉冲安培检测", None, "hidd_dialog_par_ipad6c.htm", (
    *IPAD_FIELDS, N("cl", "循环次数", 5, 5, 65535, integer=True, command=None), Q(), S(False), R()),
    UNMAPPED_NOTE)

TECHNIQUES = (CA, CC, IT, DPA, DDPA, TPA, IPAD, BE, STEP)
