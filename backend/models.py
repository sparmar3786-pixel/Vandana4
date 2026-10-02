from __future__ import annotations
from dataclasses import dataclass,field,asdict
from typing import Any
@dataclass
class Tick:
    symbol:str; ltp:float; timestamp:float; exchange:str="NSE"; token:str=""; volume:float=0; oi:float=0; source:str="unknown"; data_quality:str="OK"
@dataclass
class StrikeSnapshot:
    strike:float
    ce_ltp:float=0;pe_ltp:float=0;ce_oi:float=0;pe_oi:float=0;ce_chg_oi:float=0;pe_chg_oi:float=0;ce_vol:float=0;pe_vol:float=0
    ce_iv:float|None=None;pe_iv:float|None=None
@dataclass
class Snapshot:
    index:str;spot:float;atm_strike:float;chain:list[dict];timestamp:float;source:str;data_quality:str="OK";regime:str="UNCERTAIN";oi_bias:str="NEUTRAL";notes:list[str]=field(default_factory=list)
@dataclass
class TradePlan:
    plan_id:str;index:str;side:str;strike:float;entry:float;sl:float;targets:list[float];trailing_sl:float;time_exit:str;rr:float;position_size:int;confidence:float;strategy_ids:list[str];regime:str
    def asdict(self): return asdict(self)
@dataclass
class Decision:
    verdict:str;plans:list[dict];plans_qualifying:int;plans_suppressed:int;suppression_reasons:list[str];data_quality:str;regime:str;ai_wait_override:bool=False;notes:list[str]=field(default_factory=list)
    def asdict(self): return asdict(self)
