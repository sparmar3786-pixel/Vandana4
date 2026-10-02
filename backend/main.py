from fastapi import FastAPI,HTTPException,WebSocket,WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .core import TerminalEngine
from .ui_contract import SCREENS
from .server_ai import ServerSixLayerAI
from .pipeline32 import run32
from .mcp_bridge import NSEMCPBridge
import os,asyncio
app=FastAPI(title="NSE-AI-TERMINAL",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=os.getenv("CORS_ORIGINS","*").split(","),allow_methods=["*"],allow_headers=["*"])
engine=TerminalEngine();server_ai=ServerSixLayerAI();mcp=NSEMCPBridge()
class Manager:
    def __init__(self):self.clients=set()
    async def connect(self,ws):await ws.accept();self.clients.add(ws)
    def remove(self,ws):self.clients.discard(ws)
    async def broadcast(self,data):
        for ws in list(self.clients):
            try:await ws.send_json(data)
            except Exception:self.remove(ws)
manager=Manager()
@app.get("/health")
@app.get("/api/health")
def health():return {"ok":True,"service":"nse-ai-terminal","source":"DEMO","live_orders":False,"strategy_modules":402}
@app.get("/api/config")
def config():return {"indices":engine.INDICES,"advanced":True,"min_trade_plans":5,"min_rr":engine.risk.min_rr,"live_orders":False,"nse_mcp":mcp.enabled,"railway":True,"ai_layers":6,"strategy_modules":402}
@app.get("/api/pipeline")
def pipeline_status(index:str="NIFTY"):return {"parts":run32(engine.snapshot(index.upper()),True)}
@app.get("/api/mcp/health")
async def mcp_health():return {"enabled":mcp.enabled,"configured":bool(mcp.url),"reachable":await mcp.health()}
@app.get("/api/screens")
def screens():return SCREENS
@app.get("/api/indices")
def indices():return engine.INDICES
@app.get("/api/snapshot/{index}")
def snapshot(index:str):
    index=index.upper()
    if index not in engine.INDICES:raise HTTPException(404,"Unknown index")
    return engine.snapshot(index)
@app.get("/api/decision/{index}")
def decision(index:str):
    index=index.upper()
    if index not in engine.INDICES:raise HTTPException(404,"Unknown index")
    return engine.decision(index)
@app.get("/api/strategies")
def strategies(q:str=""):return [x.__dict__ for x in engine.registry.search(q)]
class AIDigest(BaseModel):
    index:str="NIFTY";plans:list[dict]=[];regime:str="UNKNOWN";data_quality:str="UNKNOWN"
@app.post("/api/ai/validate")
async def validate(payload:AIDigest):return await server_ai.validate(payload.model_dump())
@app.post("/api/orders/paper")
def paper_order(payload:dict):return {"accepted":True,"mode":"PAPER","order":payload}
@app.post("/api/orders/live")
def live_order():raise HTTPException(403,"Live orders are disabled in this build")
@app.websocket("/ws")
async def ws(websocket:WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            msg=await websocket.receive_json()
            idx=str(msg.get("index","NIFTY")).upper()
            await websocket.send_json({"type":"state","index":idx,"snapshot":engine.snapshot(idx),"decision":engine.decision(idx)})
    except WebSocketDisconnect:manager.remove(websocket)
