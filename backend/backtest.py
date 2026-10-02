from statistics import mean
class BacktestEngine:
    def metrics(self,trades):
        if not trades:return {'n':0,'win_rate':None,'avg_r':None,'expectancy':None,'profit_factor':None,'max_drawdown':0}
        rs=[float(t.get('r',0)) for t in trades];wins=[r for r in rs if r>0];loss=[r for r in rs if r<=0]
        gross_win=sum(wins);gross_loss=abs(sum(loss));equity=peak=dd=0
        for r in rs:
            equity+=r;peak=max(peak,equity);dd=max(dd,peak-equity)
        return {'n':len(rs),'win_rate':len(wins)/len(rs),'avg_r':mean(rs),'expectancy':mean(rs),'profit_factor':gross_win/gross_loss if gross_loss else None,'max_drawdown':dd}
    def walk_forward(self,trades,folds=5):
        if len(trades)<folds:return []
        size=len(trades)//folds;return [self.metrics(trades[i*size:(i+1)*size]) for i in range(folds)]
