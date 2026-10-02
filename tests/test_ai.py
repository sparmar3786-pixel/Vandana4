import asyncio
from backend.ai import sanitize
from backend.server_ai import ServerSixLayerAI

def test_ai_guard_restricts_verdict_vocabulary_and_trade_fields():
    x=sanitize({'layer':'L1','agrees':True,'confidence':2,'verdict_recommendation':'BUY','strike':25000,'entry':100})
    assert x['confidence']==1
    assert x['verdict_recommendation'] is None
    assert 'strike' not in x and 'entry' not in x

def test_server_ai_returns_six_layers_without_keys():
    r=asyncio.run(ServerSixLayerAI().validate({'plans':[]}))
    assert len(r['layers'])==6
