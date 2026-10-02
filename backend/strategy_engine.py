from __future__ import annotations
from .catalog import CORE,ADVANCED
from .oi import classify_oi
class StrategyEngine:
    def __init__(self,advanced=True):self.advanced=advanced
    def evaluate(self,snapshot):
        rows=snapshot.get("chain",[]);results=[]
        atm=snapshot.get("atm_strike",0)
        for meta in CORE+ (ADVANCED if self.advanced else []):
            score=0.0;side=None;reason=""
            name=meta.name.lower()
            if "put-writing" in name or "long buildup" in name or "call qualification" in name:score=.55;side="CALL"
            elif "call-writing" in name or "short buildup" in name or "put qualification" in name:score=-.55;side="PUT"
            elif "short covering" in name:score=.35;side="CALL"
            elif "long unwinding" in name:score=-.35;side="PUT"
            elif "data-quality" in name or "stale" in name or "missing" in name:score=0
            elif "bull" in name or "momentum" in name or "breakout" in name:score=.15;side="CALL"
            elif "bear" in name or "breakdown" in name or "reversal" in name:score=-.15;side="PUT"
            fired=abs(score)>=.08
            results.append({"strategy_id":meta.id,"number":meta.number,"name":meta.name,"family":meta.family,"fired":fired,"side":side,"score":score,"confidence":min(1,abs(score)),"reason":reason,"advanced":meta.advanced})
        return results
    def plans(self,snapshot,results,min_rr=1.8):
        atm=snapshot["atm_strike"];out=[];seen=set()
        fired=[r for r in results if r["fired"] and r["side"]]
        for i,r in enumerate(fired):
            if r["side"] in seen:continue
            seen.add(r["side"])
            row=min(snapshot["chain"],key=lambda x:abs(x["strike"]-atm))
            entry=float(row["ce_ltp"] if r["side"]=="CALL" else row["pe_ltp"])
            if entry<=0:continue
            sl=entry*0.88;target=entry+(entry-sl)*max(min_rr,1.8);rr=(target-entry)/(entry-sl)
            if rr<min_rr:continue
            out.append({"plan_id":f"{snapshot['index']}-{r['strategy_id']}","index":snapshot["index"],"side":r["side"],"strike":row["strike"],"entry":round(entry,2),"sl":round(sl,2),"targets":[round(target,2),round(target+(target-entry)*.5,2)],"trailing_sl":round(sl,2),"time_exit":"15:15","rr":round(rr,2),"position_size":1,"confidence":round(r["confidence"],2),"strategy_ids":[r["strategy_id"]],"regime":snapshot.get("regime","UNCERTAIN")})
        return out
