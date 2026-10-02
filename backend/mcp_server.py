from __future__ import annotations
from .core import TerminalEngine
try:
    from mcp.server.fastmcp import FastMCP
except Exception:
    FastMCP=None
engine=TerminalEngine()
mcp=FastMCP("nse-ai-terminal") if FastMCP else None
if mcp:
    @mcp.tool()
    def get_indices(): return engine.INDICES
    @mcp.tool()
    def get_snapshot(index:str="NIFTY"): return engine.snapshot(index.upper())
    @mcp.tool()
    def get_option_chain(index:str="NIFTY"): return engine.snapshot(index.upper())["chain"]
    @mcp.tool()
    def get_terminal_verdict(index:str="NIFTY"): return engine.decision(index.upper()).asdict()
    @mcp.tool()
    def get_strategies(query:str=""): return [x.__dict__ for x in engine.registry.search(query)]
    @mcp.tool()
    def place_paper_order(order:dict): return {"accepted":True,"mode":"PAPER","order":order}
    @mcp.tool()
    def place_live_order(order:dict,confirmation:str=""): return {"accepted":False,"reason":"LIVE ORDERS DISABLED"}
def main():
    if not mcp: raise RuntimeError("mcp package is not installed")
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--transport",choices=["stdio","sse"],default="stdio");p.add_argument("--port",type=int,default=8765);a=p.parse_args()
    if a.transport=="sse":mcp.settings.port=a.port;mcp.run(transport="sse")
    else:mcp.run(transport="stdio")
if __name__=="__main__":main()
