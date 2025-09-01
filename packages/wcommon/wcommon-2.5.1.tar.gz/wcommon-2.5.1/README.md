# This is my common Python tool classes.
# Main page is https://pypi.org/project/wcommon/ .


### /data/apps/public/conf.ini content like:
```
[mysql]
host=example.com
port=3306
user=username
passwd=password
database=test
charset=utf8mb4
```

### Find the localhost internal network ip:
```python
from wcommon import *
ip = getLocalIp()
hostname = getLocalHostname()
```

### Decode unusual json string:
```python
from wcommon import *
line = """
{
    name:'java',
    system:'linux'
}
"""
result = dejson(line)
# output result
{"name":"java","system":"linux"}
```

```python
# check the reuquirement list
check_requirement(['requests','flask'])
```

### Operate mysql data:
```python
mysql = Mysql(configuraion_file="/data/apps/public/conf.ini", section="mysql")
```
```python
# query
rows = mysql.query("select * from example_table where status = %s order by id desc limit %s",(1,10))
for row in rows:
    print(row)
```

```python
# bulk_insert
mysql.bulk_insert("test.person",["name","age"],[["mahuateng",40],["liyanhong",39]])
```

```python
# bulk_insert
mysql.bulk_insert2("test.person",[{"name":"ma2","age":40},{"name":"liyanhong2","age":39},{"name":"ren"}] )
```


## Feature

### 1.3.8
可以通过check_requirement方法检测依赖包是否已经安装，如果没有安装，则提示安装。

### 1.6.5 
为`Elasticsearch`增加`query`方法

### 1.8.0.0
增加 AppleScriptTool 类。此类只在Mac上有效

### 2.0.0
增加MqServer和MqProducer类，这两个类是对zeromq的包装

### 2.0.5
增加MqConsumer类


