from backend.strategy_engine import StrategyEngine
def test_strategy_engine_evaluates_all_registered_modules():
    snap={"index":"NIFTY","atm_strike":25000,"regime":"UNCERTAIN","chain":[{"strike":25000,"ce_ltp":100,"pe_ltp":100}]}
    results=StrategyEngine().evaluate(snap)
    assert len(results)==402
    assert all("strategy_id" in x and "confidence" in x for x in results)
def test_plan_engine_requires_exact_strategy_id_and_rr():
    snap={"index":"NIFTY","atm_strike":25000,"regime":"UNCERTAIN","chain":[{"strike":25000,"ce_ltp":100,"pe_ltp":100}]}
    results=StrategyEngine().evaluate(snap)
    plans=StrategyEngine().plans(snap,results,1.8)
    assert all(p["strategy_ids"] and p["rr"]>=1.8 for p in plans)
