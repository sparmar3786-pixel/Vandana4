from __future__ import annotations
import time,math
from .config import get_settings
from .brokers import AngelOne,DataSourceError
class DemoSource:
    name="demo"
    def __init__(self):self._connected=False
    async def connect(self):self._connected=True;return True
    async def get_snapshot(self,index):
        seeds={'NIFTY':24689.75,'BANKNIFTY':52317.20,'FINNIFTY':23482.10,'MIDCPNIFTY':12345.60,'SENSEX':81742.00,'BANKEX':56210.75}
        spot=seeds[index];step=50 if index not in {'SENSEX','BANKEX'} else 100;atm=round(spot/step)*step;chain=[]
        for i in range(-12,13):
            strike=atm+i*step
            ce=max(.05,100-i*5);pe=max(.05,100+i*5)
            chain.append({'strike':strike,'ce_ltp':round(ce,2),'ce_oi':58000+abs(i)*3200,'ce_chg_oi':round((i*-1.7),2),'ce_vol':12000+abs(i)*400,'pe_ltp':round(pe,2),'pe_oi':42000+abs(i)*3600,'pe_chg_oi':round(i*1.5,2),'pe_vol':10500+abs(i)*350})
        return {'index':index,'spot':spot,'atm_strike':atm,'chain':chain,'timestamp':time.time(),'source':'DEMO','data_quality':'OK','regime':'UNCERTAIN','notes':['DEMO DATA — not live market data']}
class SourceRouter:
    def __init__(self):self.settings=get_settings();self.demo=DemoSource();self.angel=AngelOne();self.active=None
    async def connect(self):
        order=self.settings.fallback_order
        for name in order:
            if name=='angel_one':
                try:
                    await self.angel.login();self.active=self.angel;return
                except Exception:continue
            if name=='demo':
                await self.demo.connect();self.active=self.demo;return
        await self.demo.connect();self.active=self.demo
    async def snapshot(self,index):
        if self.active is None:await self.connect()
        if isinstance(self.active,DemoSource):return await self.active.get_snapshot(index)
        raise DataSourceError("Live Angel option-chain normalization requires instrument master/token mapping")
