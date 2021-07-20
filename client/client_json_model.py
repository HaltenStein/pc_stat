from pydantic import BaseModel
from pydantic.types import JsonMeta
from typing import Union, List


class CPU_stat(BaseModel):
    """
    CPU BaseModel
    """
    cpu_percent: float
    full_memory: int
    used_memory: int
    temperature: Union[tuple, None]


class GPU_stat(BaseModel):
    """
    GPU BaseModel
    """

    id: str
    name: str
    GPU_temp: str
    GPU_util: str
    mem_total: str
    mem_used: str


class StatisticsPC(BaseModel):
    """
    Objects of the received json from the computer
    """
    PC: List[CPU_stat]
    GPU: List[GPU_stat]
    ip: str

    @staticmethod
    def example() -> JsonMeta:
        return """{
            "PC": [{"cpu_percent": 0, "full_memory": 0, "used_memory": 0, "temperature": []}],
            "GPU": [{"id": "","name": "", "GPU_temp": "", "GPU_util": "", "mem_total": "", "mem_used": ""}],
            "ip":""}"""
