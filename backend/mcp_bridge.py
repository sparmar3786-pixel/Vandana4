import os,httpx
class NSEMCPBridge:
    def __init__(self):self.url=os.getenv('NSE_MCP_URL','');self.enabled=os.getenv('MCP_ENABLED','on').lower() in {'1','on','true','yes'}
    async def health(self):
        if not self.enabled or not self.url:return False
        try:
            async with httpx.AsyncClient(timeout=5) as c:r=await c.get(self.url);return r.status_code<500
        except Exception:return False
