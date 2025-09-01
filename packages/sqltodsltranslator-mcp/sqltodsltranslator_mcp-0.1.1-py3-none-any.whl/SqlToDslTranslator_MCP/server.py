#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL SQL到Elasticsearch DSL转换器
支持版本: Elasticsearch 7.17
"""

from mcp.server.fastmcp import FastMCP  # 使用工具期望的路径
import re
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass


mcp = FastMCP("SqlToDslTranslatorService")

@dataclass
class SQLColumn:
    """SQL列信息"""
    name: str
    alias: Optional[str] = None
    function: Optional[str] = None
    table: Optional[str] = None
    args: Optional[List[str]] = None  # 函数参数
    distinct: bool = False  # 是否DISTINCT
    case_when: Optional[Dict[str, Any]] = None  # CASE WHEN表达式
    if_expr: Optional[Dict[str, Any]] = None  # IF表达式


@dataclass
class SQLCondition:
    """SQL条件信息"""
    field: str
    operator: str
    value: Any
    logical_op: str = "AND"
    case_when: Optional[Dict[str, Any]] = None  # CASE WHEN条件
    parentheses: bool = False  # 是否在括号内
    sub_conditions: Optional[List['SQLCondition']] = None  # 子条件


@dataclass
class SQLGroupBy:
    """GROUP BY信息"""
    field: str
    alias: Optional[str] = None
    table: Optional[str] = None


@dataclass
class SQLHaving:
    """HAVING条件信息"""
    field: str
    operator: str
    value: Any
    logical_op: str = "AND"


@dataclass
class SQLJoin:
    """JOIN信息"""
    table: str
    alias: Optional[str] = None
    join_type: str = "INNER"  # INNER, LEFT, RIGHT, FULL
    condition: Optional[str] = None


class SQLToESDSLConverter:
    """MySQL SQL到Elasticsearch DSL转换器"""
    
    def __init__(self):
        self.es_version = "7.17"
        self.default_index = "_all"
        
        # 支持的SQL函数映射到Elasticsearch
        self.function_mapping = {
            'count': 'value_count',
            'min': 'min',
            'max': 'max',
            'avg': 'avg',
            'sum': 'sum',
            'stats': 'stats',
            'extended_stats': 'extended_stats',
            'percentiles': 'percentiles',
            'floor': 'floor',
            'log': 'log',
            'log10': 'log10',
            'sqrt': 'sqrt',
            'round': 'round',
            'trim': 'trim',
            'substring': 'substring',
            'concat_ws': 'concat_ws'
        }

    def convert(self, sql: str) -> Dict[str, Any]:
        """
        转换SQL语句为Elasticsearch DSL
        
        Args:
            sql: MySQL SQL语句
            
        Returns:
            Elasticsearch DSL字典
        """
        # 保存原始SQL用于解析字段名
        original_sql = sql
        sql_upper = sql.strip().upper()
        
        # 解析SQL语句
        if sql_upper.startswith("SELECT"):
            return self._convert_select(original_sql)
        elif sql_upper.startswith("DELETE"):
            return self._convert_delete(original_sql)
        elif sql_upper.startswith("UNION"):
            return self._convert_union(original_sql)
        elif sql_upper.startswith("MINUS"):
            return self._convert_minus(original_sql)
        else:
            raise ValueError(f"不支持的SQL语句类型: {sql}")
    
    def _convert_select(self, sql: str) -> Dict[str, Any]:
        """转换SELECT语句"""
        # 解析SELECT部分
        select_match = re.search(r"SELECT\s+(.+?)\s+FROM", sql, re.IGNORECASE)
        if not select_match:
            raise ValueError("无法解析SELECT子句")
        
        columns = self._parse_columns(select_match.group(1))
        
        # 解析FROM部分
        from_match = re.search(r"FROM\s+(\w+)", sql, re.IGNORECASE)
        index = from_match.group(1) if from_match else self.default_index
        
        # 解析WHERE部分
        where_match = re.search(r"WHERE\s+(.+?)(?:\s+ORDER\s+BY|\s+GROUP\s+BY|\s+HAVING|\s+LIMIT|$)", sql, re.IGNORECASE)
        conditions = []
        if where_match:
            conditions = self._parse_where(where_match.group(1))
        
        # 解析GROUP BY部分
        group_by_match = re.search(r"GROUP\s+BY\s+(.+?)(?:\s+HAVING|\s+ORDER\s+BY|\s+LIMIT|$)", sql, re.IGNORECASE)
        group_by = []
        if group_by_match:
            group_by = self._parse_group_by(group_by_match.group(1))
        
        # 解析HAVING部分
        having_match = re.search(r"HAVING\s+(.+?)(?:\s+ORDER\s+BY|\s+LIMIT|$)", sql, re.IGNORECASE)
        having_conditions = []
        if having_match:
            having_conditions = self._parse_having(having_match.group(1))
        
        # 解析ORDER BY部分
        order_by_match = re.search(r"ORDER\s+BY\s+(.+?)(?:\s+LIMIT|$)", sql, re.IGNORECASE)
        sort = []
        if order_by_match:
            sort = self._parse_order_by(order_by_match.group(1))
        
        # 解析LIMIT部分
        limit_match = re.search(r"LIMIT\s+(\d+)(?:\s*,\s*(\d+))?", sql, re.IGNORECASE)
        size = 10
        from_offset = 0
        bucket_size = None
        if limit_match:
            if limit_match.group(2):
                from_offset = int(limit_match.group(1))
                size = int(limit_match.group(2))
            else:
                size = int(limit_match.group(1))
                bucket_size = size
        
        # 构建Elasticsearch DSL
        dsl = {
            "query": {
                "bool": {}
            },
            "size": size,
            "from": from_offset
        }
        
        # 根据条件类型构建查询
        if conditions:
            dsl["query"]["bool"] = self._build_bool_query(conditions)
        
        # 添加聚合
        if group_by:
            dsl["aggs"] = self._build_aggregations(columns, group_by, having_conditions, bucket_size)
            # 如果有聚合，设置size为0
            dsl["size"] = 0
        
        # 添加排序
        if sort:
            dsl["sort"] = sort
        
        # 添加_source字段
        if columns:
            dsl["_source"] = self._build_source(columns)
        
        return dsl
    
    def _convert_delete(self, sql: str) -> Dict[str, Any]:
        """转换DELETE语句"""
        # 解析FROM部分
        from_match = re.search(r"FROM\s+(\w+)", sql, re.IGNORECASE)
        index = from_match.group(1) if from_match else self.default_index
        
        # 解析WHERE部分
        where_match = re.search(r"WHERE\s+(.+?)(?:\s+ORDER\s+BY|\s+LIMIT|$)", sql, re.IGNORECASE)
        conditions = []
        if where_match:
            conditions = self._parse_where(where_match.group(1))
        
        # 构建Elasticsearch DSL (用于查询要删除的文档)
        dsl = {
            "query": {
                "bool": {}
            }
        }
        
        # 根据条件类型构建查询
        if conditions:
            dsl["query"]["bool"] = self._build_bool_query(conditions)
        
        return dsl
    
    def _parse_columns(self, columns_str: str) -> List[SQLColumn]:
        """解析SELECT列"""
        columns = []
        for col in columns_str.split(','):
            col = col.strip()
            
            # 处理CASE WHEN表达式
            if col.upper().startswith("CASE"):
                case_column = self._parse_case_when(col)
                if case_column:
                    columns.append(case_column)
                    continue
            
            # 处理IF表达式
            if col.upper().startswith("IF("):
                if_column = self._parse_if_expression(col)
                if if_column:
                    columns.append(if_column)
                    continue
            
            # 处理函数调用
            if '(' in col and ')' in col:
                func_column = self._parse_function_call(col)
                if func_column:
                    columns.append(func_column)
                    continue
            
            # 处理普通列
            parts = col.split('.')
            if len(parts) == 2:
                table, field = parts
                alias_match = re.search(r"AS\s+(\w+)", col, re.IGNORECASE)
                alias = alias_match.group(1) if alias_match else None
                
                columns.append(SQLColumn(
                    name=field.strip(),
                    table=table.strip(),
                    alias=alias
                ))
            else:
                field = parts[0]
                alias_match = re.search(r"AS\s+(\w+)", col, re.IGNORECASE)
                alias = alias_match.group(1) if alias_match else None
                
                columns.append(SQLColumn(
                    name=field.strip(),
                    alias=alias
                ))
        
        return columns
    
    def _parse_case_when(self, case_str: str) -> Optional[SQLColumn]:
        """解析CASE WHEN表达式"""
        # 提取CASE WHEN结构
        case_match = re.search(r'CASE\s+(.+?)\s+END(?:\s+AS\s+(\w+))?', case_str, re.IGNORECASE | re.DOTALL)
        if not case_match:
            return None
        
        case_body = case_match.group(1)
        alias = case_match.group(2)
        
        # 解析WHEN条件
        when_conditions = []
        when_parts = re.split(r'\s+WHEN\s+', case_body, re.IGNORECASE)
        
        for i, part in enumerate(when_parts):
            if i == 0:  # 跳过第一个空部分
                continue
            
            # 分离WHEN条件和THEN值
            when_then = part.split(' THEN ')
            if len(when_then) == 2:
                when_condition = when_then[0].strip()
                then_value = when_then[1].strip()
                
                when_conditions.append({
                    'condition': when_condition,
                    'result': then_value
                })
        
        # 解析ELSE部分
        else_match = re.search(r'\s+ELSE\s+(.+?)(?:\s+END|$)', case_body, re.IGNORECASE)
        else_value = else_match.group(1).strip() if else_match else None
        
        return SQLColumn(
            name="case_when",
            alias=alias,
            case_when={
                'conditions': when_conditions,
                'else_value': else_value
            }
        )
    
    def _parse_if_expression(self, if_str: str) -> Optional[SQLColumn]:
        """解析IF表达式"""
        # 提取IF参数: IF(condition, true_value, false_value)
        if_match = re.search(r'IF\s*\(\s*(.+?)\s*,\s*(.+?)\s*,\s*(.+?)\s*\)(?:\s+AS\s+(\w+))?', if_str, re.IGNORECASE)
        if not if_match:
            return None
        
        condition = if_match.group(1).strip()
        true_value = if_match.group(2).strip()
        false_value = if_match.group(3).strip()
        alias = if_match.group(4)
        
        return SQLColumn(
            name="if_expr",
            alias=alias,
            if_expr={
                'condition': condition,
                'true_value': true_value,
                'false_value': false_value
            }
        )
    
    def _parse_function_call(self, col: str) -> Optional[SQLColumn]:
        """解析函数调用"""
        # 处理DISTINCT
        distinct = False
        if 'DISTINCT' in col.upper():
            distinct = True
            col = col.replace('DISTINCT', '').replace('distinct', '')
        
        func_match = re.search(r"(\w+)\s*\((.+?)\)", col)
        if func_match:
            func_name = func_match.group(1)
            func_args = func_match.group(2).strip()
            
            # 处理别名
            alias_match = re.search(r"AS\s+(\w+)", col, re.IGNORECASE)
            alias = alias_match.group(1) if alias_match else None
            
            # 解析函数参数
            args = []
            if func_args != '*':
                args = [arg.strip() for arg in func_args.split(',')]
            
            return SQLColumn(
                name=func_args,
                function=func_name,
                alias=alias,
                args=args,
                distinct=distinct
            )
        
        return None
    
    def _parse_where(self, where_str: str) -> List[SQLCondition]:
        """解析WHERE条件"""
        conditions = []
        
        # 处理括号表达式
        if '(' in where_str and ')' in where_str:
            conditions = self._parse_parentheses_expression(where_str)
        else:
            # 简单的分割方法：按AND/OR分割，然后重新组合
            # 先找到所有的AND/OR位置
            and_positions = [m.start() for m in re.finditer(r'\s+AND\s+', where_str, re.IGNORECASE)]
            or_positions = [m.start() for m in re.finditer(r'\s+OR\s+', where_str, re.IGNORECASE)]
            
            # 合并所有位置并排序
            all_positions = [(pos, 'AND') for pos in and_positions] + [(pos, 'OR') for pos in or_positions]
            all_positions.sort(key=lambda x: x[0])
            
            if not all_positions:
                # 只有一个条件
                condition = self._parse_single_condition(where_str)
                if condition:
                    condition.logical_op = "AND"
                    conditions.append(condition)
            else:
                # 第一个条件 - 操作符应该是下一个操作符
                first_condition = where_str[:all_positions[0][0]].strip()
                condition = self._parse_single_condition(first_condition)
                if condition:
                    condition.logical_op = all_positions[0][1]  # 使用第一个操作符
                    conditions.append(condition)
                
                # 后续条件
                for i, (pos, logical_op) in enumerate(all_positions):
                    if i + 1 < len(all_positions):
                        next_pos = all_positions[i + 1][0]
                        condition_str = where_str[pos + len(logical_op) + 1:next_pos].strip()
                    else:
                        condition_str = where_str[pos + len(logical_op) + 1:].strip()
                    
                    condition = self._parse_single_condition(condition_str)
                    if condition:
                        condition.logical_op = logical_op
                        conditions.append(condition)
        
        return conditions
    
    def _parse_parentheses_expression(self, where_str: str) -> List[SQLCondition]:
        """解析带括号的表达式"""
        conditions = []
        
        # 找到最外层的括号
        start = where_str.find('(')
        end = where_str.rfind(')')
        
        if start != -1 and end != -1 and end > start:
            # 提取括号外的内容（字段名和操作符）
            before_paren = where_str[:start].strip()
            after_paren = where_str[end + 1:].strip()
            
            # 检查是否是IN条件：field IN (...)
            if before_paren and 'IN' in before_paren.upper():
                # 这是一个IN条件，需要特殊处理
                field_part = before_paren.replace('IN', '').strip()
                inner_content = where_str[start + 1:end].strip()
                
                # 解析值列表
                values = []
                for val in inner_content.split(','):
                    val = val.strip()
                    if val.startswith("'") and val.endswith("'"):
                        values.append(val[1:-1])
                    else:
                        values.append(val)
                
                # 创建IN条件
                field = field_part
                if '.' in field:
                    field = field.split('.')[-1]
                if field.lower() == 'id':
                    field = 'doc_id'
                
                condition = SQLCondition(field, 'terms', values)
                condition.logical_op = "AND"
                conditions.append(condition)
                
            elif before_paren and after_paren:
                # 例如: (a=1 OR b=1) AND c=1
                # 这里需要更复杂的逻辑来处理
                pass
            else:
                # 递归解析括号内的内容
                inner_content = where_str[start + 1:end].strip()
                inner_conditions = self._parse_where(inner_content)
                
                for condition in inner_conditions:
                    condition.parentheses = True
                    conditions.append(condition)
        
        return conditions
    
    def _parse_single_condition(self, condition_str: str) -> Optional[SQLCondition]:
        """解析单个条件"""
        
        # 处理各种操作符
        operators = [
            ('IS NOT NULL', 'not_exists'),  # 先匹配较长的操作符
            ('IS NULL', 'exists'),
            ('NOT LIKE', 'not_wildcard'),
            ('IN', 'terms'),  # 先匹配IN，避免NOT IN干扰
            ('NOT IN', 'not_terms'),
            ('BETWEEN', 'between'),
            ('NOT BETWEEN', 'not_between'),
            ('!=', 'ne'),
            ('<>', 'ne'),
            ('>=', 'gte'),
            ('<=', 'lte'),
            ('>', 'gt'),
            ('<', 'lt'),
            ('=', 'eq'),
            ('LIKE', 'wildcard')
        ]
        
        for op, es_op in operators:
            # 对于IS NULL和IS NOT NULL，使用特殊的正则表达式
            if es_op in ['exists', 'not_exists']:
                pattern = rf'(.+?)\s*{re.escape(op)}'
                match = re.match(pattern, condition_str, re.IGNORECASE)
                if match:
                    field = match.group(1).strip()
                    
                    # 处理字段名中的表前缀
                    if '.' in field:
                        field = field.split('.')[-1]
                    
                    # 特殊处理id字段
                    if field.lower() == 'id':
                        field = 'doc_id'
                    
                    return SQLCondition(field, es_op, None)
            elif es_op in ['between', 'not_between']:
                # 处理BETWEEN: field BETWEEN value1 AND value2
                pattern = rf'(.+?)\s*{re.escape(op)}\s*(.+?)\s+AND\s+(.+)'
                match = re.match(pattern, condition_str, re.IGNORECASE)
                if match:
                    field = match.group(1).strip()
                    value1 = match.group(2).strip()
                    value2 = match.group(3).strip()
                    
                    # 处理字段名中的表前缀
                    if '.' in field:
                        field = field.split('.')[-1]
                    
                    # 特殊处理id字段
                    if field.lower() == 'id':
                        field = 'doc_id'
                    
                    # 处理值
                    if value1.startswith("'") and value1.endswith("'"):
                        value1 = value1[1:-1]
                    if value2.startswith("'") and value2.endswith("'"):
                        value2 = value2[1:-1]
                    
                    return SQLCondition(field, es_op, {'min': value1, 'max': value2})
            elif es_op in ['terms', 'not_terms']:
                # 处理IN: field IN (value1, value2, ...)
                # 使用更精确的正则表达式，避免逗号干扰
                pattern = rf'(.+?)\s+{re.escape(op)}\s+(.+)'
                match = re.match(pattern, condition_str, re.IGNORECASE)
                if match:
                    field = match.group(1).strip()
                    value = match.group(2).strip()
                    
                    # 调试信息
                    print(f"DEBUG IN: field='{field}', value='{value}'")
                    
                    # 处理字段名中的表前缀
                    if '.' in field:
                        field = field.split('.')[-1]
                    
                    # 特殊处理id字段
                    if field.lower() == 'id':
                        field = 'doc_id'
                    
                    # 处理IN值列表
                    if value.startswith('(') and value.endswith(')'):
                        # 提取括号内的值
                        values_str = value[1:-1].strip()
                        values = []
                        for val in values_str.split(','):
                            val = val.strip()
                            if val.startswith("'") and val.endswith("'"):
                                values.append(val[1:-1])
                            else:
                                values.append(val)
                        value = values
                        print(f"DEBUG IN: parsed values={value}")
                    
                    return SQLCondition(field, es_op, value)
            else:
                # 使用正则表达式进行精确匹配，避免部分匹配
                pattern = rf'(.+?)\s*{re.escape(op)}\s*(.+)'
                match = re.match(pattern, condition_str, re.IGNORECASE)
                if match:
                    field = match.group(1).strip()
                    value = match.group(2).strip()
                    
                    # 处理字段名中的表前缀
                    if '.' in field:
                        field = field.split('.')[-1]
                    
                    # 特殊处理id字段
                    if field.lower() == 'id':
                        field = 'doc_id'
                    
                    # 处理值
                    if value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                        # 将SQL的LIKE通配符转换为Elasticsearch的wildcard通配符
                        if es_op == 'wildcard' or es_op == 'not_wildcard':
                            value = value.replace('%', '*')
                    elif value.isdigit():
                        value = int(value)
                    elif value.lower() in ('true', 'false'):
                        value = value.lower() == 'true'
                    elif value.lower() == 'null':
                        value = None
                    
                    return SQLCondition(field, es_op, value)
        
        return None
    
    def _parse_order_by(self, order_by_str: str) -> List[Dict[str, str]]:
        """解析ORDER BY子句"""
        sort = []
        for col in order_by_str.split(','):
            col = col.strip()
            direction = "asc"
            
            if col.upper().endswith(" DESC"):
                direction = "desc"
                col = col[:-5].strip()
            elif col.upper().endswith(" ASC"):
                col = col[:-4].strip()
            
            # 处理CASE WHEN表达式
            if col.upper().startswith("CASE"):
                case_sort = self._parse_case_when_order_by(col)
                if case_sort:
                    sort.append(case_sort)
                    continue
            
            # 处理字段名中的表前缀
            if '.' in col:
                col = col.split('.')[-1]
            
            # 特殊处理id字段
            if col.lower() == 'id':
                col = 'doc_id'
            
            sort.append({col: direction})
        
        return sort
    
    def _parse_case_when_order_by(self, case_str: str) -> Optional[Dict[str, Any]]:
        """解析ORDER BY中的CASE WHEN表达式"""
        # 提取CASE WHEN结构
        case_match = re.search(r'CASE\s+(.+?)\s+END(?:\s+(ASC|DESC))?', case_str, re.IGNORECASE | re.DOTALL)
        if not case_match:
            return None
        
        case_body = case_match.group(1)
        direction = case_match.group(2) or "asc"
        
        # 构建CASE WHEN排序
        return {
            "_script": {
                "type": "number",
                "script": self._build_case_when_script(case_body),
                "order": direction.lower()
            }
        }
    
    def _build_case_when_script(self, case_body: str) -> str:
        """构建CASE WHEN脚本"""
        script_parts = []
        
        # 解析WHEN条件
        when_parts = re.split(r'\s+WHEN\s+', case_body, re.IGNORECASE)
        
        for i, part in enumerate(when_parts):
            if i == 0:  # 跳过第一个空部分
                continue
            
            # 分离WHEN条件和THEN值
            when_then = part.split(' THEN ')
            if len(when_then) == 2:
                when_condition = when_then[0].strip()
                then_value = when_then[1].strip()
                
                # 构建条件脚本
                condition_script = self._build_condition_script(when_condition)
                script_parts.append(f"if({condition_script}) {{ return {then_value}; }}")
        
        # 解析ELSE部分
        else_match = re.search(r'\s+ELSE\s+(.+?)(?:\s+END|$)', case_body, re.IGNORECASE)
        else_value = else_match.group(1).strip() if else_match else "0"
        
        script_parts.append(f"return {else_value};")
        
        return " ".join(script_parts)
    
    def _build_condition_script(self, condition: str) -> str:
        """构建条件脚本"""
        # 简单的条件转换
        if '=' in condition:
            field, value = condition.split('=', 1)
            field = field.strip()
            value = value.strip()
            if value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            return f"doc['{field}'].value == '{value}'"
        elif '>' in condition:
            field, value = condition.split('>', 1)
            field = field.strip()
            value = value.strip()
            return f"doc['{field}'].value > {value}"
        elif '<' in condition:
            field, value = condition.split('<', 1)
            field = field.strip()
            value = value.strip()
            return f"doc['{field}'].value < {value}"
        else:
            return condition
    
    def _build_es_query(self, condition: SQLCondition) -> Dict[str, Any]:
        """构建Elasticsearch查询"""
        field = condition.field
        operator = condition.operator
        value = condition.value
        
        if operator == 'eq':
            return {"term": {field: value}}
        elif operator == 'ne':
            return {"bool": {"must_not": [{"term": {field: value}}]}}
        elif operator in ['gt', 'gte', 'lt', 'lte']:
            return {"range": {field: {operator: value}}}
        elif operator == 'wildcard':
            return {"wildcard": {field: value}}
        elif operator == 'not_wildcard':
            return {"bool": {"must_not": [{"wildcard": {field: value}}]}}
        elif operator == 'terms':
            # IN条件已经在解析时转换为列表
            if isinstance(value, list):
                return {"terms": {field: value}}
            elif isinstance(value, str) and value.startswith('(') and value.endswith(')'):
                # 备用解析逻辑
                values = value[1:-1].split(',')
                values = [v.strip().strip("'") for v in values]
                return {"terms": {field: values}}
            else:
                return {"terms": {field: value}}
        elif operator == 'not_terms':
            # NOT IN条件
            if isinstance(value, list):
                return {"bool": {"must_not": [{"terms": {field: value}}]}}
            elif isinstance(value, str) and value.startswith('(') and value.endswith(')'):
                # 备用解析逻辑
                values = value[1:-1].split(',')
                values = [v.strip().strip("'") for v in values]
                return {"bool": {"must_not": [{"terms": {field: value}}]}}
            else:
                return {"bool": {"must_not": [{"terms": {field: value}}]}}
        elif operator == 'exists':
            return {"exists": {"field": field}}
        elif operator == 'not_exists':
            return {"bool": {"must_not": [{"exists": {"field": field}}]}}
        elif operator == 'between':
            return {"range": {field: {"gte": value['min'], "lte": value['max']}}}
        elif operator == 'not_between':
            return {"bool": {"must_not": [{"range": {field: {"gte": value['min'], "lte": value['max']}}}]}}
        else:
            return {"match": {field: value}}
    
    def _build_bool_query(self, conditions: List[SQLCondition]) -> Dict[str, Any]:
        """构建bool查询"""
        bool_query = {}
        
        # 分离AND和OR条件
        must_conditions = []
        should_conditions = []
        
        for condition in conditions:
            if condition.logical_op.upper() == "OR":
                should_conditions.append(self._build_es_query(condition))
            else:  # AND
                must_conditions.append(self._build_es_query(condition))
        
        # 构建bool查询
        if must_conditions:
            bool_query["must"] = must_conditions
        
        if should_conditions:
            bool_query["should"] = should_conditions
            bool_query["minimum_should_match"] = 1
        
        return bool_query
    
    def _build_source(self, columns: List[SQLColumn]) -> List[str]:
        """构建_source字段列表"""
        source_fields = []
        for col in columns:
            if col.function:
                # 对于函数调用，使用原始字段名
                field_name = col.name
            else:
                field_name = col.name
            
            # 特殊处理id字段
            if field_name.lower() == 'id':
                field_name = 'doc_id'
            
            source_fields.append(field_name)
        return source_fields
    
    def _parse_group_by(self, group_by_str: str) -> List[SQLGroupBy]:
        """解析GROUP BY子句"""
        group_by = []
        for col in group_by_str.split(','):
            col = col.strip()
            
            # 处理字段名中的表前缀
            if '.' in col:
                table, field = col.split('.')
                group_by.append(SQLGroupBy(
                    field=field.strip(),
                    table=table.strip()
                ))
            else:
                group_by.append(SQLGroupBy(field=col))
        
        return group_by
    
    def _parse_having(self, having_str: str) -> List[SQLHaving]:
        """解析HAVING子句"""
        # 复用WHERE条件的解析逻辑
        conditions = self._parse_where(having_str)
        having_conditions = []
        
        for condition in conditions:
            having_conditions.append(SQLHaving(
                field=condition.field,
                operator=condition.operator,
                value=condition.value,
                logical_op=condition.logical_op
            ))
        
        return having_conditions
    
    def _build_aggregations(self, columns: List[SQLColumn], group_by: List[SQLGroupBy], 
                           having_conditions: List[SQLHaving], bucket_size: Optional[int]) -> Dict[str, Any]:
        """构建聚合查询"""
        aggs = {}
        
        # 主聚合桶
        main_bucket_name = "group_by_buckets"
        aggs[main_bucket_name] = {
            "terms": {
                "field": group_by[0].field,
                "size": bucket_size or 1000
            }
        }
        
        # 添加shard_size
        if bucket_size:
            aggs[main_bucket_name]["terms"]["shard_size"] = bucket_size * 20
        
        # 添加子聚合
        for col in columns:
            if col.function and col.function.lower() in self.function_mapping:
                es_func = self.function_mapping[col.function.lower()]
                agg_name = col.alias or f"{col.function}_{col.name}"
                
                if col.function.lower() == 'count' and col.distinct:
                    aggs[main_bucket_name]["aggs"] = aggs[main_bucket_name].get("aggs", {})
                    aggs[main_bucket_name]["aggs"][agg_name] = {
                        "cardinality": {"field": col.name}
                    }
                else:
                    aggs[main_bucket_name]["aggs"] = aggs[main_bucket_name].get("aggs", {})
                    aggs[main_bucket_name]["aggs"][agg_name] = {
                        es_func: {"field": col.name}
                    }
        
        # 添加HAVING过滤
        if having_conditions:
            aggs[main_bucket_name]["bucket_selector"] = {
                "buckets_path": {},
                "script": self._build_having_script(having_conditions)
            }
        
        return aggs
    
    def _build_having_script(self, having_conditions: List[SQLHaving]) -> str:
        """构建HAVING脚本"""
        script_parts = []
        
        for condition in having_conditions:
            if condition.operator == 'gt':
                script_parts.append(f"doc['{condition.field}'].value > {condition.value}")
            elif condition.operator == 'gte':
                script_parts.append(f"doc['{condition.field}'].value >= {condition.value}")
            elif condition.operator == 'lt':
                script_parts.append(f"doc['{condition.field}'].value < {condition.value}")
            elif condition.operator == 'lte':
                script_parts.append(f"doc['{condition.field}'].value <= {condition.value}")
            elif condition.operator == 'eq':
                script_parts.append(f"doc['{condition.field}'].value == {condition.value}")
            elif condition.operator == 'ne':
                script_parts.append(f"doc['{condition.field}'].value != {condition.value}")
        
        if len(script_parts) > 1:
            return " && ".join(script_parts)
        elif len(script_parts) == 1:
            return script_parts[0]
        else:
            return "true"
    
    def _convert_union(self, sql: str) -> Dict[str, Any]:
        """转换UNION语句"""
        # 解析UNION的两个查询
        union_parts = re.split(r'\s+UNION\s+', sql, re.IGNORECASE)
        
        if len(union_parts) != 2:
            raise ValueError("UNION语句必须包含两个查询")
        
        # 转换两个查询
        query1 = self.convert(union_parts[0].strip())
        query2 = self.convert(union_parts[1].strip())
        
        # 构建UNION DSL
        return {
            "query": {
                "bool": {
                    "should": [
                        query1["query"],
                        query2["query"]
                    ],
                    "minimum_should_match": 1
                }
            }
        }
    
    def _convert_minus(self, sql: str) -> Dict[str, Any]:
        """转换MINUS语句"""
        # 解析MINUS的两个查询
        minus_parts = re.split(r'\s+MINUS\s+', sql, re.IGNORECASE)
        
        if len(minus_parts) != 2:
            raise ValueError("MINUS语句必须包含两个查询")
        
        # 转换两个查询
        query1 = self.convert(minus_parts[0].strip())
        query2 = self.convert(minus_parts[1].strip())
        
        # 构建MINUS DSL (使用must_not)
        return {
            "query": {
                "bool": {
                    "must": [query1["query"]],
                    "must_not": [query2["query"]]
                }
            }
        }

converter = SQLToESDSLConverter()


@mcp.tool()
def convert(sql: str) -> Dict[str, Any]:
    return converter.convert(sql)

if __name__ == "__main__":
    mcp.run(transport="stdio")
