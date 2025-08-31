# 说明

- 从此告别 SQL 语句，直接调用方法就可以实现`增删改查`
- python3.10+
- 持续更新中...

# 更新历史

- 2025/07/06
  - 一些优化
  - 新增`SQL`对象（快速构建 SQL 语句）
- 2025/06/27
  - kwargs 中解析的`True`值为`is not null`，`False`值为`is null`
- 2025/06/28
  - SQLResponse 统一存在三个属性

# 如何安装？

- `pip install fastdb`

# 拿什么吸引你？

`使用方式简单暴力，不用写SQL就能进行增删改查`

## 连接方式

`支持传统连接、URL连接`

### 插入数据如此贴心

- 自动推导

  - `传入dict是插入一条数据，传入list是插入多条数据`

- 多种插入模式
  - `模式1，插入时，数据冲突则报错`
  - `模式2，插入时，数据冲突则忽略`
  - `模式3，插入时，数据发生冲突，把数据进行更新操作`

# 操练起来

### 连接 MySQL

`数据库对象`

```python
from fastod import MySQL

# 方式1
db = MySQL(host="localhost", port=3306, username="root", password="root@0", db="test")  # 数据库对象

# 方式1
MYSQL_CONF = {
    'host': 'localhost',
    'port': 3306,
    'username': 'root',
    'password': '123456',
    'db': 'test'
}
db = MySQL(**MYSQL_CONF)  # 数据库对象

# 方式2
MYSQL_URL = "mysql://root:123456@localhost:3306/test"
db = MySQL.from_url(MYSQL_URL)  # 数据库对象
```

`表格对象`

```python
student = db['student']
student = db.pick_table('student')
```

### 首先准备测试数据

```python
# 一条龙服务，创建people表并插入测试数据，每次插入一千条，累计插入一万条
db.gen_test_table('people', once=1000, total=10000)
people = db['people']
```

### 插入数据

`单条插入`

```python
data = {'id': 10001, 'name': '小明', 'age': 10, 'gender': '男'}

# 插入一条数据
people.insert_data(data)

# 当插入的数据与表中的数据存在冲突时（唯一索引值），直接调用会报错，如果补充<unique>参数，则不报错
people.insert_data(data, unique='id')

```

`批量插入`

```python
data = [
    {'id': 10002, 'name': '小红', 'age': 12, 'gender': '女'},
    {'id': 10003, 'name': '小强', 'age': 13, 'gender': '男'},
    {'id': 10004, 'name': '小白', 'age': 14, 'gender': '男'}
]

# 插入多条数据
people.insert_data(data)
```

`插入数据时，如果数据冲突则进行更新`

```python
data = {'id': 10001, 'name': '小明', 'age': 10, 'gender': '男'}

# 当数据冲突时，也可以直接进行更新操作，下面是把age更新为11
people.insert_data(data, update='age=age+1')
```

### 删除数据

```python
# delete from people where id=1
people.delete(id=1)

# delete from people where id in (1, 2, 3)
people.delete(id=[1, 2, 3])

# delete from people where age=18 limit 100
people.delete(age=18, limit=100)
```

### 更新数据

```python
# update people set name='tony', job='理发师' where id=1
people.update(new={'name': 'tony', 'job': '理发师'}, id=1)

# update people set job='程序员' where name='thomas' and phone='18959176772'
people.update(new={'job': '程序员'}, name='thomas', phone='18959176772')
```

### 查询数据

```python
# select * from people where id=1
people.query(id=1)

# select name, age from people where id=2
people.query(pick='name, age', id=2)

# select * from people where age=18 and gender in ('男', '女')
people.query(age=18, gender=['男', '女'])

# select name from people where age=18 and gender in ('男', '女') limit 5
people.query(pick='name', age=18, gender=['男', '女'], limit=5)
```

### 随机数据

```python
# 随机返回1条数据<dict>
print(people.random())

# 随机返回5条数据<list>
print(people.random(limit=5))
```

### 遍历表

```python
# 遍历整张表，默认每轮扫描1000条，默认只打印数据
people.scan()


def show(lines):
    for some in enumerate(lines, start=1):
        print('第{}条  {}'.format(*some))


# 限制id范围为101~222，每轮扫描100条，每轮的回调函数为show
people.scan(sort_field='id', start=101, end=222, once=100, dealer=show)

# 限制id范围的基础上，限制age=18
people.scan(sort_field='id', start=101, end=222, once=100, dealer=show, add_cond='age=18')
```
