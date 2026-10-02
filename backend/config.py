from __future__ import annotations
import os
from functools import lru_cache
from dataclasses import dataclass
@dataclass(frozen=True)
class Settings:
    data_source:str=os.getenv("DATA_SOURCE","demo")
    fallback_order:tuple=tuple(os.getenv("DATA_FALLBACK_ORDER","angel_one,mcp,nse_public,demo").split(","))
    advanced_engine:bool=os.getenv("ADVANCED_ENGINE","on").lower() in {"1","on","true","yes"}
    min_trade_plans:int=int(os.getenv("MIN_TRADE_PLANS","5"))
    min_rr:float=float(os.getenv("MIN_RR","1.8"))
    max_risk_per_trade:float=float(os.getenv("MAX_RISK_PER_TRADE","0.01"))
    max_total_risk:float=float(os.getenv("MAX_TOTAL_RISK","0.04"))
    max_tick_age_sec:float=float(os.getenv("MAX_TICK_AGE_SEC","5"))
    max_snapshot_age_sec:float=float(os.getenv("MAX_SNAPSHOT_AGE_SEC","10"))
    rate_limit_rps:float=float(os.getenv("RATE_LIMIT_RPS","8"))
    ai_enabled:bool=os.getenv("AI_ENABLED","on").lower() in {"1","on","true","yes"}
    mcp_enabled:bool=os.getenv("MCP_ENABLED","on").lower() in {"1","on","true","yes"}
    enable_live_orders:bool=os.getenv("ENABLE_LIVE_ORDERS","0").lower() in {"1","on","true","yes"}
    require_human_confirm:bool=os.getenv("REQUIRE_HUMAN_CONFIRM","1").lower() in {"1","on","true","yes"}
    indices:tuple=tuple(os.getenv("INDICES","NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY,SENSEX,BANKEX").split(","))
    @property
    def live_orders_on(self): return self.enable_live_orders
@lru_cache
def get_settings(): return Settings()
