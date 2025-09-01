"""
条件构建器模块
~~~~~~~~~~~~

提供了构建查询条件的工具类。
"""

from typing import List, Any

class Condition:
    """条件构建器，用于创建API查询条件"""
    
    @staticmethod
    def eq(field: str, value: Any) -> str:
        """等于条件"""
        return f"eq,{field},{Condition._format_value(value)}"
    
    @staticmethod
    def lt(field: str, value: Any) -> str:
        """小于条件"""
        return f"lt,{field},{Condition._format_value(value)}"
    
    @staticmethod
    def gt(field: str, value: Any) -> str:
        """大于条件"""
        return f"gt,{field},{Condition._format_value(value)}"
    
    @staticmethod
    def le(field: str, value: Any) -> str:
        """小于等于条件"""
        return f"le,{field},{Condition._format_value(value)}"
    
    @staticmethod
    def ge(field: str, value: Any) -> str:
        """大于等于条件"""
        return f"ge,{field},{Condition._format_value(value)}"
    
    @staticmethod
    def begin_with(field: str, value: str) -> str:
        """以...开始条件"""
        return f"beginWith,{field},{Condition._format_value(value)}"
    
    @staticmethod
    def end_with(field: str, value: str) -> str:
        """以...结束条件"""
        return f"endWith,{field},{Condition._format_value(value)}"
    
    @staticmethod
    def contain(field: str, value: str) -> str:
        """包含条件"""
        return f"contain,{field},{Condition._format_value(value)}"
    
    @staticmethod
    def in_list(field: str, values: List[Any]) -> str:
        """在列表中条件"""
        values_str = ';'.join(str(v) for v in values)
        return f"in,{field},'{values_str}'"
    
    @staticmethod
    def or_conditions(*conditions: str) -> str:
        """或条件"""
        formatted_conditions = [c.replace(',', '#') for c in conditions]
        return 'or,' + ','.join(formatted_conditions)
        
    @staticmethod
    def between(field: str, values: List[str]) -> str:
        """在指定区间条件"""
        if len(values) != 2:
            raise ValueError("between条件需要两个值")
        return f"between,{field},{Condition._format_value(values[0])}#{Condition._format_value(values[1])}"
    
    @staticmethod
    def _format_value(value: Any) -> str:
        """格式化值"""
        if isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str) and any(value.startswith(prefix) for prefix in ['>=', '<=', '>', '<', '=']):
            return value
        else:
            return f"'{str(value)}'"
