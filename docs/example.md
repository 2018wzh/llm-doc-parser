# Example
## Schema
```json
{
    [
        {
            "name":"证书名称",
            "field":"certificateName",
            "type":"text",
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