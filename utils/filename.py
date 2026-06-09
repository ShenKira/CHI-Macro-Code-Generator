# -*- coding: utf-8 -*-
"""
文件名格式化工具：将数值和单位转换为文件名友好的格式

规则：
- 小数点：3.0V -> 3V, 3.5V -> 3dot5V
- 科学记数法：1.0e-5 -> 1e-5, 2.5e-5 -> 2dot5e-5
- 单位：V/s -> Vps
"""


def format_number(value) -> str:
    """
    将数字格式化为文件名友好的字符串。
    
    整数部分和小数部分相同（如 3.0）-> 返回整数部分
    否则小数点替换为 'dot'（如 3.5 -> 3dot5）
    
    Args:
        value: 数值（float 或 int）
    
    Returns:
        str: 格式化后的字符串
    """
    if isinstance(value, (int, float)):
        # 如果值等于其整数部分，直接返回整数（去掉 .0）
        if value == int(value):
            return str(int(value))
        else:
            # 否则将小数点替换为 'dot'
            return str(value).replace(".", "dot")
    return str(value)


def format_scientific(value_str: str) -> str:
    """
    格式化科学记数法字符串，使其文件名友好。
    
    1.0e-5 -> 1e-5
    2.5e-5 -> 2dot5e-5
    1e-04 -> 1e-4（去掉前导零）
    2.5000000000e-04 -> 2dot5e-4（去掉尾部零）
    
    Args:
        value_str: 科学记数法字符串（如 '1.0e-5'）
    
    Returns:
        str: 格式化后的字符串
    """
    value_str = str(value_str).lower()
    
    # 分离系数和指数部分
    if 'e' in value_str:
        parts = value_str.split('e')
        coeff = parts[0]
        exp_part = parts[1]
        
        # 格式化系数部分：先转换为浮点再处理
        try:
            coeff_val = float(coeff)
            if coeff_val == int(coeff_val):
                coeff = str(int(coeff_val))
            else:
                # 将小数点替换为 'dot'
                # 但先去掉尾部的零
                coeff_str = f"{coeff_val:.10f}".rstrip('0').rstrip('.')
                coeff = coeff_str.replace(".", "dot")
        except ValueError:
            # 如果转换失败，直接替换小数点
            coeff = coeff.replace(".", "dot")
        
        # 格式化指数部分：去掉前导零和加号
        # e-04 -> e-4, e+05 -> e5
        exp_part = exp_part.lstrip('+')
        # 处理 e-0X 格式
        if exp_part.startswith('-0'):
            # -04 -> -4
            exp_part = '-' + exp_part[2:].lstrip('0')
        elif exp_part.startswith('-'):
            # -05 -> -5
            exp_part = '-' + exp_part[1:].lstrip('0')
        else:
            # 05 -> 5
            exp_part = exp_part.lstrip('0') or '0'
        
        return coeff + 'e' + exp_part
    else:
        # 不是科学记数法，按 format_number 处理
        return format_number(value_str)


def format_unit(unit_str: str) -> str:
    """
    格式化单位字符串，将不适合文件名的符号替换。
    
    V/s -> Vps
    
    Args:
        unit_str: 单位字符串（如 'V/s'）
    
    Returns:
        str: 格式化后的单位字符串
    """
    # 将 / 替换为 p（per 的缩写）
    return unit_str.replace("/", "p")


def sanitize_filename(filename: str) -> str:
    """
    对整个文件名进行健全性检查和修复。
    删除或替换不安全的字符（. 和 /）。
    
    注：此函数是通用的，但主要由各实验类在生成文件名时调用专有方法。
    
    Args:
        filename: 原始文件名
    
    Returns:
        str: 清理后的文件名
    """
    # 此处仅作为后备，主要转换应在实验类的 get_filenames 和 to_macro 中完成
    return filename.replace(".", "dot").replace("/", "p")


def validate_project_name(name: str) -> bool:
    """
    验证项目名是否合法（不包含 . 和 /）。
    
    Args:
        name: 项目名
    
    Returns:
        bool: True 如果合法，False 如果包含非法字符
    """
    return "." not in name and "/" not in name
