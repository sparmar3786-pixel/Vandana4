import os,asyncio
from openai import AsyncOpenAI
from .ai import sanitize
MODELS=[('L1','OPENAI_API_KEY','gpt-5.6-luna','https://api.openai.com/v1'),('L2','ANTHROPIC_API_KEY','claude-sonnet-4.6','anthropic'),('L3','OPENAI_API_KEY','gpt-5.6-sol','https://api.openai.com/v1'),('L4','DEEPSEEK_API_KEY','deepseek-flash','https://api.deepseek.com'),('L5','GOOGLE_API_KEY','gemini-2.5-flash','https://generativelanguage.googleapis.com/v1beta/openai/'),('L6','XAI_API_KEY','grok-4','https://api.x.ai/v1')]
SYSTEM='Validation only. Never invent strike, entry, stop-loss, target or position size. Confidence is not probability or win rate. Return JSON only with agrees, confidence, concerns, verdict_recommendation, notes.'
class ServerSixLayerAI:
    def _prompt(self,d):return SYSTEM+'\\nEngine data:\\n'+str(d)
    async def one(self,item,digest):
        lid,key,model,base=item
        if not os.getenv(key):return {'layer':lid,'model':model,'available':False,'agrees':False,'confidence':0,'concerns':['provider key not configured']}
        try:
            if base=='anthropic':
                import httpx
                h={'x-api-key':os.environ[key],'anthropic-version':'2023-06-01','content-type':'application/json'}
                body={'model':model,'max_tokens':700,'system':SYSTEM,'messages':[{'role':'user','content':str(digest)}]}
                async with httpx.AsyncClient(timeout=20) as c:r=await c.post('https://api.anthropic.com/v1/messages',headers=h,json=body);text=r.json().get('content',[{'text':''}])[0].get('text','')
            else:
                client=AsyncOpenAI(api_key=os.environ[key],base_url=base)
                r=await client.chat.completions.create(model=model,messages=[{'role':'system','content':SYSTEM},{'role':'user','content':str(digest)}],temperature=.1,max_tokens=700)
                text=r.choices[0].message.content or ''
            return sanitize({'layer':lid,'agrees':True,'confidence':.5,'concerns':[],'notes':text})|{'model':model,'available':True}
        except Exception as e:return {'layer':lid,'model':model,'available':True,'agrees':False,'confidence':0,'concerns':[str(e)[:300]]}
    async def validate(self,digest):
        layers=await asyncio.gather(*[self.one(x,digest) for x in MODELS]);wait=sum(1 for x in layers if x.get('verdict_recommendation')=='WAIT')>=3
        return {'layers':layers,'wait_override':wait,'guarded':True,'transport':'server'}
