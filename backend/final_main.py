from __future__ import annotations

import os
import time
import json
import httpx
from fastapi import HTTPException
from pydantic import BaseModel
from .main import app, mcp

ANGEL_BASE="https://apiconnect.angelone.in"
INSTRUMENT_URL="https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
ANGEL_RUNTIME={"connected":False,"client_id":"","jwt":"","feed_token":""}
EQUITY_CACHE={"at":0.0,"rows":[]}

class AngelConnect(BaseModel):
    client_id:str=""
    access_token:str=""
    mpin:str=""
    totp:str=""

@app.get("/readyz")
async def readyz():
    return {"ok":True,"service":"nse-ai-terminal","paper_mode":True,"live_orders":False}

@app.post("/api/angel/connect")
async def angel_connect(payload:AngelConnect):
    client_id=payload.client_id.strip()
    if not client_id:
        raise HTTPException(400,"Client ID is required")
    api_key=os.getenv("ANGEL_API_KEY","").strip()
    if not api_key:
        raise HTTPException(503,"ANGEL_API_KEY is not configured on the Render backend")
    headers={
        "Accept":"application/json","Content-Type":"application/json",
        "X-UserType":"USER","X-SourceID":"WEB","X-PrivateKey":api_key
    }
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            if payload.access_token.strip():
                token=payload.access_token.strip()
                r=await c.get(
                    ANGEL_BASE+"/rest/secure/angelbroking/user/v1/getProfile",
                    headers={**headers,"Authorization":"Bearer "+token}
                )
                data=r.json() if r.headers.get("content-type","").startswith("application/json") else {}
                if r.status_code>=400 or not data.get("status",False):
                    raise HTTPException(r.status_code or 401,data.get("message","Access token rejected"))
                ANGEL_RUNTIME.update({"connected":True,"client_id":client_id,"jwt":token,"feed_token":""})
                return {"status":"CONNECTED","message":"Angel One access token verified. Credentials are held only in backend memory.","profile":data.get("data") or {}}
            if not payload.mpin or not payload.totp:
                raise HTTPException(400,"Provide MPIN and current TOTP, or a valid access token")
            r=await c.post(
                ANGEL_BASE+"/rest/auth/angelbroking/user/v1/loginByPassword",
                headers=headers,
                json={"clientcode":client_id,"password":payload.mpin,"totp":payload.totp}
            )
            data=r.json()
            if r.status_code>=400 or not data.get("status",False):
                raise HTTPException(r.status_code or 401,data.get("message","Angel One login failed"))
            d=data.get("data") or {}
            ANGEL_RUNTIME.update({"connected":True,"client_id":client_id,"jwt":d.get("jwtToken",""),"feed_token":d.get("feedToken","")})
            return {"status":"CONNECTED","message":"Angel One login verified. Session tokens remain backend-side.","profile":{}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(502,"Angel One connection error: "+str(e)[:180])

@app.post("/api/mcp/connect")
async def mcp_connect():
    if not mcp.enabled:
        raise HTTPException(503,"NSE MCP is disabled")
    init=await mcp.initialize()
    tools=await mcp.tools_list()
    if init is None or tools is None:
        raise HTTPException(502,"NSE MCP did not respond")
    names=[]
    raw=tools.get("result",tools) if isinstance(tools,dict) else {}
    for item in (raw.get("tools",[]) if isinstance(raw,dict) else []):
        if isinstance(item,dict) and item.get("name"): names.append(str(item["name"]))
    return {"connected":True,"message":"NSE MCP initialized and tools/list completed.","tools":names[:100]}

@app.get("/api/equities")
async def equities(board:str="NSE",q:str=""):
    board=board.upper()
    if board not in {"NSE","BSE"}:
        raise HTTPException(400,"board must be NSE or BSE")
    now=time.time()
    if now-EQUITY_CACHE["at"]>3600:
        try:
            async with httpx.AsyncClient(timeout=25) as c:
                r=await c.get(INSTRUMENT_URL)
                r.raise_for_status()
                rows=r.json()
                EQUITY_CACHE["rows"]=[
                    {"symbol":x.get("symbol"),"name":x.get("name"),"exchange":"NSE" if x.get("exch_seg")=="nse_cm" else "BSE"}
                    for x in rows if x.get("exch_seg") in {"nse_cm","bse_cm"} and x.get("symbol")
                ]
                EQUITY_CACHE["at"]=now
        except Exception as e:
            raise HTTPException(503,"Equity master unavailable: "+str(e)[:160])
    needle=q.strip().lower()
    want=[x for x in EQUITY_CACHE["rows"] if x["exchange"]==board and (not needle or needle in str(x["symbol"]).lower() or needle in str(x["name"]).lower())]
    return want[:500]

@app.get("/api/angel/status")
async def angel_status():
    return {"connected":ANGEL_RUNTIME["connected"],"client_id":ANGEL_RUNTIME["client_id"] if ANGEL_RUNTIME["connected"] else ""}
