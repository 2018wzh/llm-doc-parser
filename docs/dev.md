# API

## POST /extract

### 描述

解析

### 字段

- source: 文件来源，"minio"或者"raw"
- file: 原始文本内容或minio文件路径
- upload_file: 上传的文件
- schema: 数据库中查到的schema
- provider: 提供商名称
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
	    "description":"描述" // 字段描述
            "field":"exampleField", // 字段名称
            "type":"text", // 可选text,int,float,boolean,date等
            "required": true // 字段是否必填
        }
    ]
}
```

## 示例

### Body

```
source: file
schema: [{"name":"证书名称","field":"certificateName","type":"text","required":true},{"name":"人名","field":"ownerName","type":"text","required":true},{"name":"证书内容","field":"certificateContent","type":"text","required":true},{"name":"证书时间","field":"certificateTime","type":"date","required":true},{"name":"颁发机构","field":"certificateAuthority","type":"text","required":true},{"name":"证书等级","field":"certificateLevel","type":"text","required":false}]
provider: custom
model: ecnu-plus
file: {上传文件}
```

### Schema

```json
{
    [
        {
            "name":"证书名称",
            "field":"certificateName",
            "type":"text",
	    "description":"证书所属比赛的名称"
            "required": true
        },
        {
            "name":"人名",
            "field":"ownerName",
            "type":"text",
            "required": true
        },
        {
            "name":"证书内容",
            "field":"certificateContent",
            "type":"text",
            "required": true
        },
        {
            "name":"证书时间",
            "field":"certificateTime",
            "type":"date",
            "required": true
        },
        {
            "name":"颁发机构",
            "field":"certificateAuthority",
            "type":"text",
            "required": true
        },
        {
            "name":"证书等级",
            "field":"certificateLevel",
            "type":"text",
            "required": false
        },
    ]
}
```
