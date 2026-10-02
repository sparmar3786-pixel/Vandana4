from __future__ import annotations
import os,time,httpx,pyotp
class DataSourceError(RuntimeError):pass
class BrokerBase:
    name="base"
    async def connect(self):return True
    async def close(self):return None
class AngelOne(BrokerBase):
    name="angel_one"
    base=os.getenv("ANGEL_BASE_URL","https://apiconnect.angelbroking.com")
    def __init__(self):self.jwt=os.getenv("ANGEL_JWT","");self.refresh=os.getenv("ANGEL_REFRESH_TOKEN","")
    async def login(self):
        key=os.getenv("ANGEL_API_KEY");client=os.getenv("ANGEL_CLIENT_ID");pin=os.getenv("ANGEL_PIN");totp=os.getenv("ANGEL_TOTP_SECRET")
        if not all([key,client,pin,totp]):raise DataSourceError("Angel credentials not configured")
        code=pyotp.TOTP(totp).now()
        async with httpx.AsyncClient(timeout=15) as c:
            r=await c.post(self.base+"/rest/auth/angelbroking/user/v1/loginByPassword",headers={"X-PrivateKey":key,"Content-Type":"application/json"},json={"clientcode":client,"password":pin,"totp":code})
        if r.status_code>=400:raise DataSourceError(f"Angel login HTTP {r.status_code}")
        data=r.json().get("data") or {}
        self.jwt=data.get("jwtToken","");self.refresh=data.get("refreshToken",self.refresh);return bool(self.jwt)
    async def quote(self,exchange,token):
        if not self.jwt and not await self.login():raise DataSourceError("Angel authentication failed")
        key=os.getenv("ANGEL_API_KEY")
        async with httpx.AsyncClient(timeout=10) as c:
            r=await c.post(self.base+"/rest/secure/angelbroking/market/v1/quote/",headers={"Authorization":"Bearer "+self.jwt,"X-PrivateKey":key,"Content-Type":"application/json"},json={"mode":"FULL","exchangeTokens":{exchange:[token]}})
        if r.status_code>=400:raise DataSourceError(f"Angel quote HTTP {r.status_code}")
        return r.json()
