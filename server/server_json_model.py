from pydantic import BaseModel
from typing import Union, List


class CPU_stat(BaseModel):
    """data model CPU statistics"""
    cpu_percent: float
    full_memory: int
    used_memory: int
    temperature: Union[tuple, None]


class GPU_stat(BaseModel):
    """data model GPU statistics"""
    id: str
    name: str
    GPU_temp: str
    GPU_util: str
    mem_total: str
    mem_used: str


class StatisticsPC(BaseModel):
    """unified data model CPU and GPU"""
    PC: List[CPU_stat]
    GPU: List[GPU_stat]
    ip: str
