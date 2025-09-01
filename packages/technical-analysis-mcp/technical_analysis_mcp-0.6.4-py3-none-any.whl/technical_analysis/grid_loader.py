import json
from datetime import datetime, timedelta
from typing import Dict, Any

class OverFlowError(Exception): ...

class GridLoader:
    """
    网格策略参数加载器
    """
    
    @staticmethod
    def load_from_json(file_path: str) -> Dict[str, Any]:
        """
        从JSON文件加载网格策略参数
        :param file_path: JSON文件路径
        :return: 策略参数字典
        """
        with open(file_path, 'r') as f:
            config = json.load(f)
        return GridLoader._parse_config(config)
    
    @staticmethod
    def load_from_dict(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        从字典直接加载网格策略参数
        :param config: 包含策略参数的字典
        :return: 策略参数字典
        """
        return GridLoader._parse_config(config)
    
    @staticmethod
    def _parse_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析配置字典并返回标准化的策略参数
        :param config: 原始配置字典
        :return: 标准化的策略参数字典
        """
        if not isinstance(config, dict):
            raise ValueError("配置必须是一个字典")
            
        grid_params = config.get('grid_parameters', '')
        price_range = config.get('price_range', '')
        metadata = config.get('metadata', '')
        trigger_conditions = config.get('trigger_conditions', '')
        
        # 参数校验
        if not isinstance(grid_params, dict):
            raise TypeError("grid_parameters必须是一个字典")
        if not isinstance(price_range, dict):
            raise TypeError("price_range必须是一个字典")
        if not isinstance(metadata, dict):
            raise TypeError("metadata必须是一个字典")
        if not isinstance(trigger_conditions, dict):
            raise TypeError("trigger_conditions必须是一个字典")
        if 'asset' not in metadata:
            if 'symbol' in metadata:
                metadata['asset'] = metadata['symbol']
            else:
                raise KeyError("metadata中必须包含asset字段")
        if len(metadata.get('asset', '')) != 6:
            raise ValueError("asset字段必须是6位股票代码")
        if 'strategy_start_date' in metadata:
            metadata['start_date'] = metadata['strategy_start_date']
        if 'start_date' not in metadata:
            raise KeyError("metadata中必须包含start_date字段")
        else:
            start_date = datetime.strptime(metadata.get('start_date', '20000101'), '%Y%m%d').date() if len(metadata.get('start_date', '')) == 8 else datetime.strptime(metadata.get('start_date', '2000-01-01'), '%Y-%m-%d').date()
        if 'end_date' not in metadata:
            end_date = start_date + timedelta(days=14)
        else:
            end_date = datetime.strptime(metadata.get('end_date', '20000101'), '%Y%m%d').date() if len(metadata.get('end_date', '')) == 8 else datetime.strptime(metadata.get('end_date', '2000-01-01'), '%Y-%m-%d').date()
        if start_date >= end_date:
            raise ValueError("start_date必须在end_date之前")
        if 'zones' not in grid_params and ('buy_zones' not in grid_params or 'sell_zones' not in grid_params):
            raise ValueError("grid_parameters中必须包含zones or buy_zones和sell_zones字段")
        
        #If date ranges are invalid (not between 14-30 days), raise an error
        if (end_date - start_date).days < 5 or (end_date - start_date).days > 30:
            raise ValueError("日期范围必须在14-30天之间")
        min_price = float(price_range.get('min', 3.8))
        max_price = float(price_range.get('max', 4.2))
        if min_price >= max_price:
            raise ValueError("price_range中的min价格必须小于max价格")
        
        # 从买卖区域提取价格水平构建网格层级
        # 将买卖价格与对应的position_size组合成网格层级列表
        levels = grid_params.get('levels', 0)
        buy_zones = grid_params.get('buy_zones', [])
        sell_zones = grid_params.get('sell_zones', [])

        zones = grid_params.get('zones', [])
        
        def parse_zone(zone, default_price, total_zones):
            default_size = grid_params.get('position_size', 1.5 / total_zones)
            if isinstance(zone, float):
                return {'price': zone, 'size': default_size}
            return {
                'price': zone.get('price_level', zone.get('price', default_price)),
                'size': abs(zone.get('position_size', zone.get('position_size_change', zone.get('size', default_size))))
            }

        # 创建包含价格和position_size的网格层级列表
        grid_levels = []
        
        # 处理zones
        for zone in zones:
            grid_levels.append(parse_zone(zone, min_price, len(zones)))
        
        # 处理buy_zones和sell_zones
        total_buy_sell_zones = len(buy_zones) + len(sell_zones)
        for zone in buy_zones:
            grid_levels.append(parse_zone(zone, min_price, total_buy_sell_zones))
        for zone in sell_zones:
            grid_levels.append(parse_zone(zone, max_price, total_buy_sell_zones))

        # 检查grid_levels中的size只在0-1之间
        for level in grid_levels:
            if level['size'] < 0 or level['size'] > 1:
                raise OverflowError("网格层级中的size必须在0-1之间")

        # 按价格排序网格层级并去重
        grid_levels = sorted(grid_levels, key=lambda x: x['price'])
        # 使用dict.fromkeys()去重，保留第一个出现的price值
        seen_prices = {}
        grid_levels = [seen_prices.setdefault(level['price'], level) for level in grid_levels 
                      if level['price'] not in seen_prices]
        
        rsi_thresholds = grid_params.get('rsi_thresholds', [30, 70])
        
        if levels>0 and levels != len(grid_levels):
            raise ValueError("网格层级数量不一致")
            
        return {
            'metadata': metadata,  # 保留原始的metadata字段
            'asset': str(metadata.get('asset', '')),
            'start_date': start_date,
            'end_date': end_date,
            'grid_parameters': grid_params,
            'trigger_conditions': trigger_conditions,
            'min_price': float(price_range.get('min', 3.8)),
            'max_price': float(price_range.get('max', 4.2)),
            'buy_rsi_threshold': int(grid_params.get('grid_parameters', rsi_thresholds[1])),
            'sell_rsi_threshold': int(grid_params.get('sell_rsi_threshold', rsi_thresholds[0])),
            'grid_levels': grid_levels,
        }
