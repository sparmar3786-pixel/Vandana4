from __future__ import annotations
from .catalog import CORE,ADVANCED
class StrategyEngine:
    def __init__(self,advanced=True):self.advanced=advanced
    def evaluate(self,snapshot):
        rows=snapshot.get("chain",[]);results=[]
        for meta in CORE+(ADVANCED if self.advanced else []):
            name=meta.name.lower();score=0.0;side=None;reason=""
            if any(k in name for k in ("put-writing","long buildup","call qualification")):score=.55;side="CALL";reason="positive price/OI family confirmation"
            elif any(k in name for k in ("call-writing","short buildup","put qualification")):score=-.55;side="PUT";reason="negative price/OI family confirmation"
            elif "short covering" in name:score=.35;side="CALL";reason="premium/OI covering confirmation"
            elif "long unwinding" in name:score=-.35;side="PUT";reason="premium/OI unwinding confirmation"
            elif any(k in name for k in ("bull","momentum","breakout","higher high","vwap reclaim")):score=.15;side="CALL";reason="directional momentum confirmation"
            elif any(k in name for k in ("bear","breakdown","lower low","vwap breakdown")):score=-.15;side="PUT";reason="directional weakness confirmation"
            fired=abs(score)>=.08
            results.append({"strategy_id":meta.id,"number":meta.number,"name":meta.name,"family":meta.family,"fired":fired,"side":side,"score":score,"confidence":min(1,abs(score)),"reason":reason,"advanced":meta.advanced})
        return results
    def plans(self,snapshot,results,min_rr=1.8):
        chain=snapshot["chain"];atm=snapshot["atm_strike"];fired=[r for r in results if r["fired"] and r["side"]]
        out=[]
        # Build only candidates backed by >=2 deterministic strategy IDs; never pad.
        for side in ("CALL","PUT"):
            rs=[r for r in fired if r["side"]==side]
            if len(rs)<2:continue
            rs=sorted(rs,key=lambda x:(-x["confidence"],x["number"]))
            for offset in (-2,-1,0,1,2):
                target_strike=atm+offset*50
                row=min(chain,key=lambda x:abs(x["strike"]-target_strike))
                entry=float(row["ce_ltp"] if side=="CALL" else row["pe_ltp"])
                if entry<=0:continue
                sl=round(entry*0.88,2);risk=round(entry-sl,2);target=round(entry+risk*min_rr,2);rr=round((target-entry)/risk,2) if risk>0 else 0
                if rr<min_rr:continue
                evidence=rs[:max(2,3 if offset==0 else 2)]
                out.append({"plan_id":f"{snapshot['index']}-{side}-{int(row['strike'])}","index":snapshot["index"],"side":side,"strike":row["strike"],"entry":round(entry,2),"sl":sl,"targets":[target,round(target+risk*.5,2)],"trailing_sl":sl,"time_exit":"15:15","rr":rr,"position_size":1,"confidence":round(sum(x["confidence"] for x in evidence)/len(evidence),2),"strategy_ids":[x["strategy_id"] for x in evidence],"regime":snapshot.get("regime","UNCERTAIN")})
        return out
