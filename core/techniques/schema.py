"""Parameter metadata shared by models, validation and Qt forms.

Ranges come from the linked 600E parameter pages, not the older 600A
macro reference. None is deliberately used for undocumented commands.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Parameter:
    key: str
    label: str
    default: object
    kind: str = "float"
    minimum: float | None = None
    maximum: float | None = None
    command: str | None = None
    choices: tuple = ()  # (stored value, Chinese display, standalone macro)
    optional: bool = False
    help: str = ""
    local: bool = False  # application-only metadata, never a CHI parameter

    def parse(self, value):
        if self.optional and value is None:
            return None
        if self.kind == "choice":
            matches = [item[0] for item in self.choices
                       if item[0] == value and
                       (not isinstance(item[0], bool) and not isinstance(value, bool)
                        or type(item[0]) is type(value))]
            if not matches:
                raise ValueError(f"{self.label}：请选择有效选项。")
            return value
        if isinstance(value, bool):
            raise ValueError(f"{self.label}：请输入数值。")
        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{self.label}：请输入数值，支持 1e-4 等科学计数法。") from None
        if not math.isfinite(number):
            raise ValueError(f"{self.label}：数值必须有限。")
        if self.kind == "int" and not number.is_integer():
            raise ValueError(f"{self.label}：请输入整数。")
        if self.minimum is not None and number < self.minimum:
            raise ValueError(f"{self.label}：不得小于 {self.minimum:g}。")
        if self.maximum is not None and number > self.maximum:
            raise ValueError(f"{self.label}：不得大于 {self.maximum:g}。")
        return int(number) if self.kind == "int" else number


@dataclass(frozen=True)
class Technique:
    code: str
    name: str
    tech: str | None
    source: str
    parameters: tuple[Parameter, ...]
    note: str = ""
    presets: tuple = ()
    summary_keys: tuple = ()

    def normalize(self, values):
        keys = {p.key for p in self.parameters}
        unknown = set(values) - keys
        if unknown:
            raise ValueError(f"{self.code} 未知参数：{', '.join(sorted(unknown))}")
        return {p.key: p.parse(values.get(p.key, p.default)) for p in self.parameters}


def number(key, label, default, minimum, maximum, *, command="same", integer=False,
           optional=False, help="", local=False):
    return Parameter(key, label, default, "int" if integer else "float", minimum,
                     maximum, key if command == "same" else command,
                     optional=optional, help=help, local=local)


def choice(key, label, default, options, *, command=None, optional=False, help="", local=False):
    return Parameter(key, label, default, "choice", command=command,
                     choices=tuple(options), optional=optional, help=help, local=local)


def potential(key="ei", label="初始电位 (V)", default=0):
    return number(key, label, default, -10, 10)


def quiet():
    return number("qt", "静置时间 (s)", 0, 0, 100000)


def sensitivity(auto=True, command="sens", minimum=1e-12):
    options = [(10.0 ** n, f"1e{n} A/V", None) for n in range(-12, 0)
               if 10.0 ** n >= minimum]
    if auto:
        options.insert(0, ("auto", "自动", "autosens"))
    return choice("sens", "灵敏度 (A/V)", 1e-5, options, command=command)


def auxiliary():
    return choice("aux", "记录辅助信号", False,
                  [(False, "关闭", "auxoff"), (True, "开启", "auxon")])


def repeat():
    return number("repeat", "重复测试次数", 1, 1, 9999, integer=True, local=True)


def polarity(label="初始方向"):
    return choice("pn", label, "p", [("p", "正向 / 阳极 (p)", None),
                                      ("n", "负向 / 阴极 (n)", None)], command="pn")


def scales():
    return choice("scales", "运行时显示量程数量", None,
                  [(1, "1", None), (2, "2", None), (3, "3", None)], optional=True,
                  help="CHM 未给出宏命令；启用后需要在配置文件中补充已确认的映射。")


def open_circuit(key="open_circuit", label="开路步骤"):
    return choice(key, label, None, [(False, "恒电位", None), (True, "开路", None)],
                  optional=True, help="CHM 仅描述界面选项，未给出对应宏命令。")


def variant(default, values):
    return choice("variant", "试验形式", default, [(v, label, None) for v, label in values],
                  command="$tech")
