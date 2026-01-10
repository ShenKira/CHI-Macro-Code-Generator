from abc import ABC, abstractmethod


class Experiment(ABC):
    def __init__(self, exp_type: str):
        self.exp_type = exp_type

    @abstractmethod
    def to_macro(self, project_name: str) -> str:
        """生成 CHI Macro 代码"""
        pass

    @abstractmethod
    def estimate_time(self) -> float:
        """估算实验耗时（秒）"""
        pass

    @abstractmethod
    def signature(self) -> tuple:
        """用于判断实验是否“参数完全相同”"""
        pass
