# python-ads-client
### project_summary

A python client for communicating with a Beckhoff PLC via ADS

```python
ams_net_id = "5.109.60.19.1.1"

connection = ADSConnection(
    ams_net_id=ams_net_id, ip_address="10.10.32.24", ams_net_port=851
)

with connection:
    data = {
        "MAIN.nVar1": 100,
        "MAIN.nVar2": 200,
        "MAIN.nVar3": 300,
        "MAIN.nVar4": 400,
        "MAIN.bool1": True,
        "MAIN.bool2": False,
    }
    connection.write_list_by_name(data)
```
