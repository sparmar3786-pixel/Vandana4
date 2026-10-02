import os,httpx
class NSEMCPBridge:
    def __init__(self):
        self.url=os.getenv('NSE_MCP_URL','https://mcp.nseindia.in/cmmkt/mcp');self.enabled=os.getenv('MCP_ENABLED','on').lower() in {'1','on','true','yes'};self.session_id=None
    async def _post(self,payload):
        if not self.enabled or not self.url:return None
        headers={'Accept':'application/json, text/event-stream','Content-Type':'application/json'}
        if self.session_id:headers['Mcp-Session-Id']=self.session_id
        try:
            async with httpx.AsyncClient(timeout=12) as c:
                r=await c.post(self.url,headers=headers,json=payload)
                sid=r.headers.get('Mcp-Session-Id')
                if sid:self.session_id=sid
                if r.status_code>=400:return None
                return r.json() if 'application/json' in r.headers.get('content-type','') else {'raw':r.text}
        except Exception:return None
    async def initialize(self):
        return await self._post({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'nse-ai-terminal','version':'0.1.0'}}})
    async def tools_list(self):
        return await self._post({'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}})
    async def call_tool(self,name,arguments=None):
        return await self._post({'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':name,'arguments':arguments or {}}})
    async def health(self):
        if not self.enabled or not self.url:return False
        await self.initialize()
        return (await self.tools_list()) is not None
