PART_NAMES=['Data Input','Data Quality Engine','Market Regime','Price Action','Indicators','Option OI Engine','Premium + Volume Engine','Seller Pressure Engine','CE Engine','PE Engine','Opposite-Side Override','Strike Engine','Support / Resistance','Greeks Engine','Volatility Surface','Order Flow','Multi-Leg Options','Expiry Engine','Liquidity Engine','Trap Engine','Cross-Index','Time Engine','Quant Engine','Entry Engine','Risk Engine','Confidence Engine','Strategy Conflict','Signal Quality','Backtest','Strategy Memory','6-AI Validation','Final Decision']
ADVANCED_PARTS={15,16,17,21}
class Pipeline:
    def __init__(self,advanced=True):self.advanced=advanced
    def run(self,snapshot):
        q=snapshot.get('data_quality','DATA_GAP'); results=[]
        for n,name in enumerate(PART_NAMES,1):
            skipped=(n in ADVANCED_PARTS and not self.advanced)
            ok=q=='OK' or n==1
            results.append({'part':n,'name':name,'ok':ok,'data_gap':not ok,'skipped':skipped})
        return results
