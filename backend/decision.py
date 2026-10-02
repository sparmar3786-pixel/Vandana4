from __future__ import annotations
from .core import DecisionEngine,RiskGate
class FinalDecision:
    def __init__(self,min_rr=1.8):self.engine=DecisionEngine(5,RiskGate(min_rr))
    def run(self,plans,regime="UNCERTAIN",data_quality="OK",ai_wait=False):
        if data_quality!="OK":return {"verdict":"NO QUALIFYING TRADE","plans":[],"plans_qualifying":0,"plans_suppressed":len(plans),"suppression_reasons":["DATA_GAP"],"data_quality":data_quality,"regime":regime,"ai_wait_override":False}
        ai=type("AI",(),{"wait_override":ai_wait})()
        d=self.engine.build(plans,ai)
        d.data_quality=data_quality;d.regime=regime
        return d.asdict()
