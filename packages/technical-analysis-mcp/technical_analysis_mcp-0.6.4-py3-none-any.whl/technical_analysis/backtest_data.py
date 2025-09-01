from dataclasses import dataclass
from datetime import date
from typing import List, Dict, Any

@dataclass
class BacktestData:
    """回测数据类"""
    strategy_name: str
    asset: str
    start_date: date
    end_date: date
    benchmark_return: float
    strategy_return: float
    excess_return: float
    reward: float
    trade_count: int
    max_drawdown: float
    trade_log: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """将对象转换为字典"""
        return {
            'strategy_name': self.strategy_name,
            'asset': self.asset,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'benchmark_return': self.benchmark_return,
            'strategy_return': self.strategy_return,
            'excess_return': self.excess_return,
            'reward': self.reward,
            'trade_count': self.trade_count,
            'max_drawdown': self.max_drawdown,
            'trade_log': self.trade_log
        }
