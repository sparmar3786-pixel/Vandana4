from typing import Any
VERDICTS={'CALL BUY','PUT BUY','WAIT','NO QUALIFYING TRADE'}
MODELS=[('L1','GPT-5.6 Luna'),('L2','Claude Sonnet 4.6'),('L3','GPT-5.6 Sol'),('L4','DeepSeek Chat'),('L5','Gemini 2.5 Flash'),('L6','Grok 4')]
def sanitize(obj:dict[str,Any]):
    v=str(obj.get('verdict_recommendation','')).upper();return {'layer':obj.get('layer','?'),'agrees':bool(obj.get('agrees',False)),'confidence':max(0,min(1,float(obj.get('confidence',.5)))),'concerns':[str(x) for x in obj.get('concerns',[])][:10],'verdict_recommendation':v if v in VERDICTS else None,'notes':str(obj.get('notes',''))[:600]}
class SixLayerAI:
    async def validate(self,digest):
        return {'layers':[{'layer':i,'model':m,'agrees':True,'confidence':.5,'concerns':['Validation only; no trade parameters invented.'],'verdict_recommendation':None,'notes':'Server provider optional; browser Puter path is also available.'} for i,m in MODELS],'wait_override':False,'guarded':True,'transport':'server'}
