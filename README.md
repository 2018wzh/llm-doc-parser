# LLM Doc Parser

使用unstructed+tesseract结合大语言模型进行结构化数据提取的服务。

## API POST /extract

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

### Schema（TOON 格式，等价支持）

也可以使用 TOON 表格描述 Schema，更适合粘贴/阅读：

```toon
values[3]{name,field,type,required}:
    证书名称,certificateName,text,true
    人名,ownerName,text,true
    证书时间,certificateTime,date,true
```

## 工具接口：JSON Schema 转 TOON

当你手头已有 JSON 版 schema，需要快速得到 TOON 版以便粘贴或调试时，可调用：

- POST `/schema/toon`
    - 支持两种提交方式：
        - JSON Body：`{"schema": [ {name, field, type, required}, ... ] }`
        - FormData：`schema=...`（可为 JSON 数组或 TOON 表格）
    - 返回：`{"toon": "values[N]{name,field,type,required}:\n  ..."}`

示例（JSON Body）：

```json
POST /schema/toon
{
    "schema": [
        {"name":"证书名称","field":"certificateName","type":"text","required":true},
        {"name":"人名","field":"ownerName","type":"text","required":true}
    ]
}
```

响应：

```toon
values[2]{name,field,type,required}:
    证书名称,certificateName,text,true
    人名,ownerName,text,true
```

说明：
- 表头固定为 `values[N]{name,field,type,required}:`，`N` 为行数。
- 每一行对应一个字段，按顺序给出 `name,field,type,required`。
- required 使用 `true/false`。

## 示例

### Body

```
source: file
schema: 可以是 JSON 数组 或 TOON 表格。例如 TOON：

```toon
values[6]{name,field,type,required}:
    证书名称,certificateName,text,true
    人名,ownerName,text,true
    证书内容,certificateContent,text,true
    证书时间,certificateTime,date,true
    颁发机构,certificateAuthority,text,true
    证书等级,certificateLevel,text,false
```

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
