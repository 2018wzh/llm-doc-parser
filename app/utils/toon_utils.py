"""
TOON 工具函数
"""
from __future__ import annotations
import re
from typing import Any, Dict, List, Optional
from toon import decode as toon_decode  # type: ignore


def extract_toon_block(text: str) -> str:
    """
    从文本中提取 TOON 代码块。如果找不到代码块，返回原文本。
    优先匹配 ```toon ... ```，其次匹配首个通用 ``` ``` 块。
    """
    if not isinstance(text, str):
        return ""

    # 优先匹配带语言标记的 toon 代码块
    m = re.search(r"```toon\s*\n(.*?)\n```", text, flags=re.S | re.I)
    if m:
        return m.group(1).strip()

    # 退回到第一个通用代码块
    m = re.search(r"```\s*\n(.*?)\n```", text, flags=re.S)
    if m:
        return m.group(1).strip()

    return text.strip()


def encode_toon(value: Any) -> str:
    """将任意可 JSON 序列化的值编码为 TOON 字符串。"""
    try:
        from toon import encode as toon_encode  # type: ignore
    except Exception as e:  # pragma: no cover
        raise ImportError("python-toon 未安装，无法编码为 TOON。请安装依赖 python-toon。") from e
    return toon_encode(value)


def extract_values_list(parsed: Any) -> List[Dict[str, Any]]:
    """
    从解码后的结构中提取 `values` 列表（每项包含 field/type/value）。
    兼容以下几种可能：
    - 顶层就是 list
    - 顶层为 dict，包含 'values' 键
    - 顶层为 dict，只有一个键且该值为 list
    其他情况返回空列表。
    """
    if isinstance(parsed, list):
        # 假定每项是对象 {field, type, value}
        return [x for x in parsed if isinstance(x, dict)]

    if isinstance(parsed, dict):
        if isinstance(parsed.get("values"), list):
            return [x for x in parsed["values"] if isinstance(x, dict)]
        # 只有一个 key 的 dict，取该 key 的值
        if len(parsed) == 1:
            key = next(iter(parsed.keys()))
            val = parsed[key]
            if isinstance(val, list):
                return [x for x in val if isinstance(x, dict)]

    return []


def extract_schema_list(parsed: Any) -> List[Dict[str, Any]]:
    """
    从解码后的结构中提取 schema 列表（每项包含 name, field, type, required）。
    支持：
    - 顶层 list
    - 顶层 dict 且包含 'schema' 或 'fields'
    - 顶层 dict 且仅一个键，值为 list
    其他情况返回空列表。
    """
    if isinstance(parsed, list):
        return [x for x in parsed if isinstance(x, dict)]

    if isinstance(parsed, dict):
        for key in ("schema", "fields", "items", "values"):
            val = parsed.get(key)
            if isinstance(val, list):
                return [x for x in val if isinstance(x, dict)]
        if len(parsed) == 1:
            key = next(iter(parsed.keys()))
            val = parsed[key]
            if isinstance(val, list):
                return [x for x in val if isinstance(x, dict)]

    return []


def schema_to_toon(schema: List[Dict[str, Any]]) -> str:
    """
    将 schema（list[dict]，包含 name/field/type/required）编码为标准 TOON 表格：
    values[N]{name,field,type,required}:
      人名,name,text,true
    """
    rows: List[str] = []
    for item in schema:
        name = str(item.get("name", ""))
        field = str(item.get("field", ""))
        ftype = str(item.get("type", "text"))
        req = item.get("required", True)
        req_str = "true" if bool(req) else "false"
        rows.append(f"  {name},{field},{ftype},{req_str}")
    header = f"values[{len(rows)}]{{name,field,type,required}}:"
    return header + ("\n" + "\n".join(rows) if rows else "\n")
