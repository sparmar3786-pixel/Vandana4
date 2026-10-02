from __future__ import annotations
import json,os,time,httpx
from .brokers import AngelOne,DataSourceError
class AngelOneData(AngelOne):
    INSTRUMENT_URL="https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    def __init__(self):
        super().__init__();self.instruments=[];self.by_key={}
    async def load_instruments(self):
        async with httpx.AsyncClient(timeout=30) as c:r=await c.get(self.INSTRUMENT_URL)
        r.raise_for_status();self.instruments=r.json()
        self.by_key={(str(x.get("exch_seg")),str(x.get("symbol"))):x for x in self.instruments}
        return len(self.instruments)
    def resolve(self,exchange,symbol):
        x=self.by_key.get((exchange,symbol))
        return x.get("token") if x else None
    async def connect(self):
        ok=await self.login()
        if ok:
            try:await self.load_instruments()
            except Exception:pass
        return ok
