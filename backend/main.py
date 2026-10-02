from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .core import TerminalEngine,AIValidation
from .ui_contract import SCREENS
from .ai import SixLayerAI
from .pipeline import Pipeline
from .mcp_bridge import NSEMCPBridge
import os
app=FastAPI(title='NSE-AI-TERMINAL',version='0.1.0')
app.add_middleware(CORSMiddleware,allow_origins=os.getenv('CORS_ORIGINS','*').split(','),allow_methods=['*'],allow_headers=['*'])
engine=TerminalEngine();ai=SixLayerAI();pipeline=Pipeline(advanced=True);mcp=NSEMCPBridge()
@app.get('/health')
@app.get('/api/health')
def health():return {'ok':True,'service':'nse-ai-terminal','source':'DEMO','live_orders':False}
@app.get('/api/config')
def config():return {'indices':engine.INDICES,'advanced':True,'min_trade_plans':5,'min_rr':1.8,'live_orders':False,'nse_mcp':True,'railway':True,'ai_layers':6}
@app.get('/api/pipeline')
def pipeline_status(index:str='NIFTY'):
    snap=engine.snapshot(index.upper())
    return {'parts':pipeline.run(snap)}
@app.get('/api/mcp/health')
async def mcp_health(): return {'enabled':mcp.enabled,'configured':bool(mcp.url),'reachable':await mcp.health()}
@app.get('/api/screens')
def screens():return SCREENS
@app.get('/api/indices')
def indices():return engine.INDICES
@app.get('/api/snapshot/{index}')
def snapshot(index:str):
    index=index.upper()
    if index not in engine.INDICES:raise HTTPException(404,'Unknown index')
    return engine.snapshot(index)
@app.get('/api/decision/{index}')
def decision(index:str):return engine.decision(index).__dict__
@app.get('/api/strategies')
def strategies(q:str=''):return [x.__dict__ for x in engine.registry.search(q)]
class AIDigest(BaseModel):index:str='NIFTY';plans:list[dict]=[];regime:str='UNKNOWN';data_quality:str='UNKNOWN'
@app.post('/api/ai/validate')
async def validate(payload:AIDigest):return await ai.validate(payload.model_dump())
@app.post('/api/orders/paper')
def paper_order(payload:dict):return {'accepted':True,'mode':'PAPER','order':payload}
@app.post('/api/orders/live')
def live_order():raise HTTPException(403,'Live orders are disabled in this build')
