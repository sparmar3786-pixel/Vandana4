from dataclasses import dataclass,field
from .catalog import CORE,ADVANCED
@dataclass
class GateResult: ok:bool; flags:list[str]=field(default_factory=list); reasons:list[str]=field(default_factory=list)
class DataQualityGate:
    def __init__(self,max_age_seconds=5): self.max_age_seconds=max_age_seconds
    def check(self,age_seconds,has_oi=True,has_volume=True,duplicate=False):
        f=[];r=[]
        if age_seconds>self.max_age_seconds:f+=['STALE'];r+=['stale']
        if not has_oi:f+=['MISSING_OI'];r+=['OI unavailable']
        if not has_volume:f+=['MISSING_VOLUME'];r+=['volume unavailable']
        if duplicate:f+=['DUPLICATE'];r+=['duplicate tick']
        return GateResult(not f,f,r)
class RiskGate:
    def __init__(self,min_rr=1.8):self.min_rr=float(min_rr)
    def passes(self,rr):return rr is not None and float(rr)>=self.min_rr
@dataclass
class AIValidation: wait_override:bool=False; layers:list[dict]=field(default_factory=list)
@dataclass
class Decision: verdict:str; plans:list[dict]; suppressed_count:int=0; suppression_reasons:list[str]=field(default_factory=list); ai_wait_override:bool=False
class DecisionEngine:
    def __init__(self,min_plans=5,risk_gate=None):self.min_plans=min_plans;self.risk_gate=risk_gate or RiskGate()
    def build(self,plans,ai=None):
        ai=ai or AIValidation(); valid=[];sup=[]
        for p in plans:
            if not p.get('strategy_ids'):sup.append('missing exact strategy IDs');continue
            if not self.risk_gate.passes(p.get('rr')):sup.append('R:R below single gate');continue
            valid.append(p)
        if ai.wait_override:return Decision('WAIT',valid,len(sup),sup,True)
        if not valid:return Decision('NO QUALIFYING TRADE',[],len(sup),sup,False)
        sides={p['side'] for p in valid}; verdict='CALL BUY' if sides=={'CALL'} else 'PUT BUY' if sides=={'PUT'} else 'WAIT'
        return Decision(verdict,valid,len(sup),sup,False)
class StrategyRegistry:
    def __init__(self):self._all=CORE+ADVANCED
    def count_core(self):return len(CORE)
    def count_advanced(self):return len(ADVANCED)
    def all(self):return self._all
    def search(self,q=''):
        q=q.lower().strip();return [x for x in self._all if not q or q in x.id.lower() or q in x.name.lower() or q in x.family.lower()]
class TerminalEngine:
    INDICES=['NIFTY','BANKNIFTY','FINNIFTY','MIDCPNIFTY','SENSEX','BANKEX']
    def __init__(self):self.registry=StrategyRegistry();self.risk=RiskGate();self.snapshots={}
    def snapshot(self,index):
        seed={'NIFTY':24689.75,'BANKNIFTY':52317.20,'FINNIFTY':23482.10,'MIDCPNIFTY':12345.60,'SENSEX':81742.00,'BANKEX':56210.75}[index]
        atm=round(seed/50)*50; chain=[]
        for i in range(-5,6):
            s=atm+i*50;chain.append({'strike':s,'ce_ltp':round(max(2,100-i*6),2),'ce_oi':58000+max(i,0)*4300,'ce_chg_oi':round(i*2.1,2),'ce_vol':12000+max(i,0)*500,'pe_ltp':round(max(2,100+i*5),2),'pe_oi':42000+max(-i,0)*3600,'pe_chg_oi':round(-i*1.8,2),'pe_vol':10500+max(-i,0)*400})
        plans=[]
        for j,side in enumerate(['CALL','CALL','PUT','CALL','PUT']):
            entry=100-j*7;sl=entry-18;target=entry+36
            plans.append({'plan_id':f'P{j+1}','index':index,'side':side,'strike':atm+(j-2)*50,'entry':entry,'sl':sl,'targets':[target,target+12],'trailing_sl':sl+5,'time_exit':'15:15','rr':round((target-entry)/(entry-sl),2),'position_size':1,'confidence':0.72,'strategy_ids':[f'S{j+1:03d}'],'regime':'BULLISH'})
        snap={'index':index,'spot':seed,'atm_strike':atm,'chain':chain,'data_quality':'OK','source':'DEMO','regime':'BULLISH','candidate_plans':plans};self.snapshots[index]=snap;return snap
    def decision(self,index,ai=None):return DecisionEngine(5,self.risk).build((self.snapshots.get(index) or self.snapshot(index))['candidate_plans'],ai)
