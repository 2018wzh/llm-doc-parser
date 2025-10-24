# API
## POST /extract
### 描述
解析
### 字段
- source: 文件来源，"minio"或者"raw"
- file: minIO URL或者原始文本内容
- schema: 数据库中查到的schema
- model: LLM模型
### 返回
- 提取的json数据
```json
[
    {
        "field": "exampleField", // 示例字段名称
        "type": "text", // 示例字段类型
        "value": "exampleValue" // 示例字段值
    }
]
```
## Schema
```json
{
    [
        {
            "name":"示例", // 字段详情
            "field":"exampleField", // 字段名称
            "type":"text", // 可选text,int,float,boolean,date等
            "required": true // 字段是否必填
        }
    ]
}