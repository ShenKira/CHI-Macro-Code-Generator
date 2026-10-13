"""Validated macro generation, serialization and duration calculation."""
from core.experiment import Experiment
from core.techniques.registry import get_technique
from utils.sensitivity import auto_sensitivity
import math


class MacroMappingError(ValueError):
    pass


class ConfiguredExperiment(Experiment):
    def __init__(self, exp_type, values=None):
        definition = get_technique(exp_type)
        super().__init__(definition.code)
        self.parameters = definition.normalize(values or {})
        self.start_index = 1
        self.index = None
        self.validate()

    @property
    def definition(self):
        return get_technique(self.exp_type)

    def __getattr__(self, name):
        parameters = self.__dict__.get("parameters", {})
        if name in parameters:
            return parameters[name]
        raise AttributeError(name)

    def __setattr__(self, name, value):
        parameters = self.__dict__.get("parameters", {})
        if name in parameters:
            field = next(field for field in self.definition.parameters if field.key == name)
            previous = parameters.copy()
            parameters[name] = field.parse(value)
            try:
                self.validate()
            except ValueError:
                super().__setattr__("parameters", previous)
                raise
        else:
            super().__setattr__(name, value)

    def validate(self):
        self.parameters = self.definition.normalize(self.parameters)
        p = self.parameters
        if "eh" in p and "el" in p and p["eh"] <= p["el"]:
            raise ValueError("电位上限必须大于电位下限。")
        if self.exp_type in ("CV", "CA") and not p["el"] <= p["ei"] <= p["eh"]:
            raise ValueError("初始电位必须位于电位上、下限之间。")
        if self.exp_type == "CV" and not .01 - 1e-12 <= p["eh"] - p["el"] <= 13.1:
            raise ValueError("CV 高、低电位至少相差 0.01 V，最大扫描范围为 13.1 V。")
        if self.exp_type == "CV" and p["final_enable"]:
            if not p["el"] <= p["ef"] <= p["eh"]:
                raise ValueError("终止电位必须位于电位上、下限之间。")
            if p["cl"] == 1:
                target = p["eh"] if p["pn"] == "p" else p["el"]
                if not min(p["ei"], target) <= p["ef"] <= max(p["ei"], target):
                    raise ValueError("单段扫描的终止电位必须位于初始电位和首段目标之间。")
        scan_types = {"LSV", "SCV", "TAFEL", "DPV", "NPV", "DNPV", "SWV", "ACV", "SHACV", "FTACV", "HMV", "IMPE"}
        if self.exp_type in scan_types and abs(p["ei"] - p["ef"]) < .01 - 1e-12:
            raise ValueError("初始电位与终止电位至少相差 0.01 V。")
        if p.get("sens") == "auto" and self.exp_type in ("CV", "LSV", "TAFEL"):
            if not p.get("capacitance") and p["v"] > .01:
                raise ValueError("此方法仅在扫描速率 ≤ 0.01 V/s 时支持仪器自动灵敏度。")
        if self.exp_type == "LSV" and p.get("aux") and p["v"] >= .25:
            raise ValueError("LSV 辅助信号记录要求扫描速率 < 0.25 V/s。")
        if self.exp_type == "CA" and p.get("aux") and p["si"] < .005:
            raise ValueError("CA 辅助信号记录要求采样间隔 ≥ 0.005 s。")
        if self.exp_type == "CP" and p.get("aux") and p["si"] < .0005:
            raise ValueError("CP 辅助信号记录要求数据间隔 ≥ 0.0005 s。")
        if self.exp_type in ("DPV", "NPV"):
            if p["sw"] > p["pw"] / 2 or p["pw"] > p["prod"] / 2:
                raise ValueError("采样宽度不得超过脉冲宽度的一半，脉冲宽度不得超过脉冲周期的一半。")
        if self.exp_type == "DPV" and abs(p["amp"]) < .001:
            raise ValueError("DPV 脉冲幅度的绝对值至少为 0.001 V。")
        if self.exp_type == "DNPV":
            if p["sw"] > min(p["pw1"], p["pw2"]) / 2 or max(p["pw1"], p["pw2"]) > p["prod"] / 2:
                raise ValueError("采样宽度不得超过任一脉冲宽度的一半，脉冲宽度不得超过周期的一半。")
        if self.exp_type == "SCV" and p["sw"] > p["prod"] / 2:
            raise ValueError("阶梯伏安法的采样宽度不得超过阶梯周期的一半。")
        if self.exp_type == "EIS" and p["fh"] <= p["fl"]:
            raise ValueError("最高频率必须大于最低频率。")
        if self.exp_type == "CPCR" and p["ic"] == p["ia"]:
            raise ValueError("变流扫描的初始电流与终止电流不能相同。")
        if self.exp_type == "PSA" and p["depe"] == p["ef"]:
            raise ValueError("沉积电位与终止电位不能相同，否则可能立即结束。")
        if self.exp_type == "HMV" and math.sqrt(p["rpm"]) + math.sqrt(p["modamp"]) > math.sqrt(10000):
            raise ValueError("按 CHM 的平方根调制公式，最大瞬时转速不得超过 10000 rpm。")
        if self.exp_type in ("STEP", "ISTEP") and not any(p[f"st{i}"] > 0 for i in range(1, 13)):
            raise ValueError("至少一个阶跃步骤的时间必须大于 0。")
        if self.exp_type == "TPA" and p["incre"] > 0 and abs(p["pulse_e3"] - p["ef"]) < .01:
            raise ValueError("第三脉冲电位与终止电位至少相差 0.01 V。")

    def signature(self):
        return (self.exp_type, tuple((k, v) for k, v in self.parameters.items() if k != "repeat"))

    def to_dict(self):
        return {"type": self.exp_type, **self.parameters}

    def get_filenames(self, project_name):
        start = self.start_index or 1
        return [f"{project_name}_{self.exp_type}_{start + i}" for i in range(self.repeat)]

    def _field_command(self, field, override):
        value = self.parameters[field.key]
        if value is None or field.local:
            return []
        mapping = override.get("parameters", {}).get(field.key, field.command)
        if isinstance(mapping, dict):
            token = str(value).lower()
            command = mapping.get(token)
            if command is None:
                raise MacroMappingError(f"{self.exp_type}.{field.key} 缺少选项 {token} 的宏映射")
            return [command]
        if field.kind == "choice" and field.key not in override.get("parameters", {}):
            standalone = next(item[2] for item in field.choices if item[0] == value)
            if standalone:
                return [standalone]
        if mapping == "$tech":
            return []
        if mapping is None:
            raise MacroMappingError(f"{self.exp_type}.{field.key}（{field.label}）缺少已确认的宏命令映射")
        if field.key == "sens" and value == "auto":
            raise MacroMappingError(f"{self.exp_type}.sens 自动量程需要独立命令映射")
        if isinstance(value, bool):
            raise MacroMappingError(f"{self.exp_type}.{field.key} 开关参数需要 true/false 独立命令映射")
        return [f"{mapping}={value}"]

    def parameter_commands(self, macro_overrides=None):
        self.validate()
        if macro_overrides:
            from utils.app_config import validate_config
            macro_overrides = validate_config({"macro_overrides": macro_overrides})["macro_overrides"]
        override = (macro_overrides or {}).get(self.exp_type, {})
        tech = override.get("tech") or self.parameters.get("variant") or self.definition.tech
        if tech is None:
            raise MacroMappingError(f"{self.exp_type}：CHM 未给出技术宏名称，请在设置中补充 tech 映射。")
        p = self.parameters
        lines = [f"tech={tech}"]
        for field in self.definition.parameters:
            if self.exp_type == "EIS" and field.key == "ei" and p["use_ocp"]:
                lines.append("eio")
                continue
            if self.exp_type == "CV" and field.key == "sens" and p["sens"] == "auto" and p["capacitance"]:
                lines.append(f"sens={auto_sensitivity(p['capacitance'], p['v'])}")
                continue
            lines.extend(self._field_command(field, override))
        return lines

    def to_macro(self, project_name, macro_overrides=None):
        header = self.parameter_commands(macro_overrides)
        blocks = ["\n".join(header)]
        for name in self.get_filenames(project_name):
            blocks.append(f"run\nsave:{name}\ntsave:{name}")
        return "\n".join(blocks)

    @property
    def time_is_upper_bound(self):
        return (self.exp_type == "CP" and self.priority == "time"
                or self.exp_type in ("CPCR", "ISTEP"))

    def estimate_time(self):
        p, code = self.parameters, self.exp_type
        qt = p.get("qt", 0)
        if code == "CP":
            if p["priority"] == "potential":
                return None
            first, second = (p["cl"] + 1) // 2, p["cl"] // 2
            cathodic, anodic = (first, second) if p["pn"] == "n" else (second, first)
            duration = cathodic * (p["tc"] + p["leht"]) + anodic * (p["ta"] + p["heht"])
        elif code in ("PSA", "BE", "IMPE", "EIS"):
            return None
        elif code in ("IT", "OCPT", "ECN", "IMPT"):
            duration = p["st"] + qt
        elif code == "CPCR":
            duration = abs(p["ia"] - p["ic"]) / p["v"]
        elif code in ("CA", "CC"):
            duration = p["cl"] * p["pw"] + qt
        elif code == "CV":
            first_end = p["eh"] if p["pn"] == "p" else p["el"]
            distance = abs(p["ei"] - first_end) + (p["cl"] - 1) * (p["eh"] - p["el"])
            if p["final_enable"]:
                last_end = first_end if p["cl"] % 2 else (p["el"] if p["pn"] == "p" else p["eh"])
                distance -= abs(last_end - p["ef"])
            duration = distance / p["v"] + qt
        elif code in ("LSV", "TAFEL"):
            duration = abs(p["ef"] - p["ei"]) * p.get("cl", 1) / p["v"] + p.get("ht", 0) + qt
        elif code in ("SCV", "DPV", "NPV", "DNPV", "SWV", "ACV", "SHACV", "HMV"):
            points = math.ceil(abs(p["ef"] - p["ei"]) / p["incre"]) + 1
            period = 1 / p["freq"] if code == "SWV" else p.get("prod", p.get("cl", 1) / p.get("freq", 1))
            duration = points * period * (p["cl"] if code == "SCV" else 1) + qt
        elif code == "FTACV":
            duration = p["total_points"] / p["points_per_sine"] / p["freq"] + qt
        elif code == "SSF":
            duration = sum(abs(p[f"ef{i}"] - p[f"ei{i}"]) / p[f"v{i}"] + p[f"st{i}"] for i in range(1, 7)) + qt
        elif code in ("STEP", "ISTEP"):
            duration = sum(p[f"st{i}"] for i in range(1, 13)) * p["cl"] + qt
        elif code in ("DPA", "DDPA"):
            prefixes = ("",) if code == "DPA" else ("first_", "second_")
            duration = sum(p[prefix + k] for prefix in prefixes for k in ("clean_t", "pulse_t1", "pulse_t2")) * p["cl"] + qt
        elif code == "TPA":
            cycles = p["cl"] if p["incre"] == 0 else math.ceil(abs(p["ef"] - p["pulse_e3"]) / p["incre"]) + 1
            duration = sum(p[f"pulse_t{i}"] for i in range(1, 4)) * cycles + qt
        elif code == "IPAD":
            duration = sum(p[k + "_t"] for k in ("start", "forward", "reverse", "hold", "oxidation", "reduction")) * p["cl"] + qt
        else:
            return None
        return duration * p["repeat"]

    def summary(self):
        definition = self.definition
        keys = definition.summary_keys or tuple(p.key for p in definition.parameters
                                               if not p.local and p.key != "variant")[:4]
        fields = []
        for key in keys:
            value = self.parameters[key]
            if value is None:
                continue
            field = next(p for p in definition.parameters if p.key == key)
            if field.kind == "choice":
                value = next(item[1] for item in field.choices if item[0] == value)
            elif isinstance(value, float):
                value = f"{value:.3g}"
            fields.append(f"{field.label}={value}")
        result = " | ".join(fields)
        if self.repeat > 1:
            result += f" | ×{self.repeat}"
        return result
