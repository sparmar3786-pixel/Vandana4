from __future__ import annotations
import httpx
class NSEPublic:
    name="nse_public"
    BASE="https://www.nseindia.com"
    async def option_chain(self,index):
        symbol={"NIFTY":"NIFTY","BANKNIFTY":"BANKNIFTY","FINNIFTY":"FINNIFTY","MIDCPNIFTY":"MIDCPNIFTY"}.get(index)
        if not symbol:raise ValueError("NSE public fallback does not cover this index")
        h={"User-Agent":"Mozilla/5.0","Accept":"application/json,text/plain,*/*","Referer":self.BASE+"/"}
        async with httpx.AsyncClient(headers=h,timeout=15) as c:
            await c.get(self.BASE+"/")
            r=await c.get(self.BASE+f"/api/option-chain-indices?symbol={symbol}")
            r.raise_for_status();return r.json()
