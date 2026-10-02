import sqlite3,os,threading,json
class StrategyMemory:
    def __init__(self,path='data/strategy_memory.sqlite'):
        os.makedirs(os.path.dirname(path) or '.',exist_ok=True);self.db=path;self.lock=threading.Lock();self._init()
    def _init(self):
        with sqlite3.connect(self.db) as c:c.execute('create table if not exists observations(id integer primary key,strategy_id text,index_name text,regime text,payload text,created_at text default current_timestamp)')
    def record(self,strategy_id,index_name,regime,payload):
        with self.lock,sqlite3.connect(self.db) as c:c.execute('insert into observations(strategy_id,index_name,regime,payload) values(?,?,?,?)',(strategy_id,index_name,regime,json.dumps(payload)))
