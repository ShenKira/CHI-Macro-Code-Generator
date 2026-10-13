"""External user settings, with predictable Nuitka standalone/onefile paths."""
from pathlib import Path
import copy
import json
import os
import re
import sys
import tempfile
from core.techniques.registry import TECHNIQUES, DEFAULT_QUICK, canonical_type

DEFAULTS = {"version": 1, "quick_experiments": list(DEFAULT_QUICK),
            "macro_overrides": {}, "last_parameters": {}}
TOKEN = re.compile(r"[a-z][a-z0-9-]*\Z", re.I)
COMMAND = re.compile(r"[a-z][a-z0-9]*\Z", re.I)
RESERVED = {"run", "save", "tsave", "folder", "forcequit", "for", "next", "end", "tech"}


def application_dir(argv=None, compiled=None):
    if compiled is None:
        compiled = "__compiled__" in globals() or getattr(sys, "frozen", False)
    if compiled:
        return Path((argv or sys.argv)[0]).resolve().parent
    return Path(__file__).resolve().parents[1]


def config_path():
    return application_dir() / "config" / "experiments.json"


def validate_command(value):
    if not isinstance(value, str) or not COMMAND.fullmatch(value) or value.lower() in RESERVED:
        raise ValueError(f"无效的参数宏命令：{value!r}；仅允许单个命令名。")


def validate_config(data):
    if not isinstance(data, dict):
        raise ValueError("设置文件必须为 JSON 对象。")
    unknown = set(data) - set(DEFAULTS)
    if unknown:
        raise ValueError(f"未知设置项：{', '.join(sorted(unknown))}")
    result = copy.deepcopy(DEFAULTS)
    result.update(copy.deepcopy(data))
    if result["version"] != 1:
        raise ValueError("不支持的设置文件版本。")
    quick = result["quick_experiments"]
    if not isinstance(quick, list) or not all(isinstance(code, str) for code in quick):
        raise ValueError("quick_experiments 必须为试验类型列表。")
    quick = [canonical_type(code) for code in quick]
    if len(set(quick)) != len(quick) or any(code not in TECHNIQUES for code in quick):
        raise ValueError("快捷试验列表含重复或未知类型。")
    result["quick_experiments"] = quick
    overrides = result["macro_overrides"]
    if not isinstance(overrides, dict):
        raise ValueError("macro_overrides 必须为对象。")
    for code, override in overrides.items():
        if code not in TECHNIQUES or not isinstance(override, dict):
            raise ValueError(f"未知的宏映射类型：{code}")
        if set(override) - {"tech", "parameters"}:
            raise ValueError(f"{code} 映射仅接受 tech 和 parameters。")
        tech = override.get("tech")
        if tech is not None and (not isinstance(tech, str) or not TOKEN.fullmatch(tech)):
            raise ValueError(f"{code}.tech 不是有效的技术名称。")
        mapping = override.get("parameters", {})
        if not isinstance(mapping, dict):
            raise ValueError(f"{code}.parameters 必须为对象。")
        fields = {p.key: p for p in TECHNIQUES[code].parameters if not p.local and p.command != "$tech"}
        for key, command in mapping.items():
            if key not in fields:
                raise ValueError(f"{code} 中没有可映射的参数 {key}。")
            field = fields[key]
            if isinstance(command, dict):
                expected = {str(item[0]).lower() for item in field.choices}
                if field.kind != "choice" or set(command) != expected:
                    raise ValueError(f"{code}.{key} 必须为每个选项提供独立命令。")
                for token in command.values():
                    validate_command(token)
            else:
                validate_command(command)
                if field.kind == "choice" and any(isinstance(item[0], bool) or item[0] == "auto" for item in field.choices):
                    raise ValueError(f"{code}.{key} 的开关／自动选项需要按选项映射。")
    if not isinstance(result["last_parameters"], dict):
        raise ValueError("last_parameters 必须为对象。")
    for code, values in result["last_parameters"].items():
        if code not in TECHNIQUES or not isinstance(values, dict):
            raise ValueError(f"无效的参数记忆类型：{code}")
        TECHNIQUES[code].normalize(values)
    return result


class AppConfig:
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else config_path()
        self.data = copy.deepcopy(DEFAULTS)
        self.error = None
        if self.path.exists():
            try:
                with self.path.open(encoding="utf-8-sig") as stream:
                    self.data = validate_config(json.load(stream))
            except (ValueError, OSError) as exc:
                self.error = str(exc)

    @property
    def quick_experiments(self):
        return self.data["quick_experiments"]

    @property
    def macro_overrides(self):
        return self.data["macro_overrides"]

    def save(self, data=None):
        validated = validate_config(data if data is not None else self.data)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(prefix="experiments-", suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(validated, stream, ensure_ascii=False, indent=2, allow_nan=False)
                stream.write("\n")
            os.replace(name, self.path)
        finally:
            if os.path.exists(name):
                os.unlink(name)
        self.data = validated
        self.error = None

    def remember(self, experiment):
        if self.error:
            raise ValueError("现有配置文件读取失败，请先在“试验设置”中修正；原文件已保留。")
        data = copy.deepcopy(self.data)
        data["last_parameters"][experiment.exp_type] = experiment.parameters.copy()
        self.save(data)
