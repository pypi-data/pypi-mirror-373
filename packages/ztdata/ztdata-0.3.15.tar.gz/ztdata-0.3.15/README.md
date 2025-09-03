## 一、安装
```
# 下载whl文件
https://git.ztquant.com/ztData/ztdata/releases/download/v0.3.12/ztdata-0.3.13-py3-none-any.whl
# 用pip安装
pip install ztdata-0.3.13-py3-none-any.whl
```

## 二、实时数据订阅

ZtDataClient提供实时数据订阅功能，支持股票行情和新闻数据的WebSocket连接。

### 1、股票行情订阅示例

```python
from ZTData import WsClient
import time

# 行情数据回调函数
def stock_data_callback(stock):
    # 计算涨跌幅
    change_pct = ""
    if stock.get('pre_close_px') and stock.get('last_px'):
        try:
            pre_close = float(stock['pre_close_px'])
            last = float(stock['last_px'])
            if pre_close > 0:
                change_val = (last - pre_close) / pre_close * 100
                change_pct = f"{change_val:.2f}%"
        except Exception as e:
            print(f"计算涨跌幅错误: {e}")
    
    print(f"股票: {stock['security_id']} {stock['security_name']} 价格: {stock['last_px']} 涨跌幅: {change_pct}")
    
    # 打印买卖档位
    if stock.get('bid') and stock.get('ask'):
        print("  买盘:")
        for i, bid in enumerate(stock['bid']):
            if len(bid) >= 2:
                print(f"    买{i+1}: 价格 {bid[0]}, 数量 {bid[1]}")
        
        print("  卖盘:")
        for i, ask in enumerate(stock['ask']):
            if len(ask) >= 2:
                print(f"    卖{i+1}: 价格 {ask[0]}, 数量 {ask[1]}")

# 初始化客户端
client = WsClient()

# 订阅行情数据
client.subscribe(
    symbols=["sh601008", "sz002640", "sz000821"],  # 股票代码列表
    depth=5,  # 行情深度(1-5)
    on_stock_callback=stock_data_callback  # 股票回调函数
)

# 保持运行30秒
time.sleep(30)

# 停止订阅
client.stop()
```

### 2、新闻数据订阅示例

#### 2.1 使用示例
```python
from ZTData import WsClient
import time

# 新闻数据回调函数
def news_data_callback(news):
    source = news.get("source", "")
    row_data = news.get("row_data", "")

    print(f"📰 新闻来源: {source}")
    print(f"   原始数据: {row_data}")

# 初始化客户端
client = WsClient()

# 订阅新闻数据
client.subscribe_news(on_news_callback=news_data_callback)

# 保持运行30秒
time.sleep(30)

# 停止订阅
client.stop()
```
#### 2.2 新闻数据来源说明
source字段表示新闻数据来源，取值如下：
- `sina-live`：新浪-突发
- `glh-live`：格隆汇-快讯
- `glh-event`：格隆汇-事件
- `jygs-latest-hot`：韭研公社-社群研选（最新热度）
- `jygs-latest-publish`：韭研公社-社群研选（最新发布）

### 3、同时订阅股票和新闻

```python
from ZTData import WsClient
import time

def stock_callback(stock):
    print(f"📈 股票: {stock['security_id']} 价格: {stock['last_px']}")

def news_callback(news):
    print(f"📰 新闻: {news.get('content', '')[:50]}...")

# 初始化客户端
client = WsClient()

# 同时订阅股票和新闻
client.subscribe(["sh000001"], depth=5, on_stock_callback=stock_callback)
client.subscribe_news(on_news_callback=news_callback)

# 保持运行
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client.stop()
```

### 4、API 参考

#### WsClient

**初始化**

```python
WsClient(
    host="182.131.21.179",    # 服务器地址
    port=37123,               # 服务器端口
    log_level=logging.INFO    # 日志级别
)
```

**方法**

- `subscribe(symbols, depth=5, on_stock_callback=None)`: 订阅股票行情数据
  - `symbols`: 股票代码列表
  - `depth`: 行情深度(1-5)
  - `on_stock_callback`: 股票数据回调函数
  - 返回: 布尔值，表示是否成功启动订阅

- `subscribe_news(on_news_callback=None)`: 订阅新闻数据
  - `on_news_callback`: 新闻数据回调函数
  - 返回: 布尔值，表示是否成功启动订阅

- `stop()`: 停止所有WebSocket连接
- `stop_stock()`: 只停止股票连接
- `stop_news()`: 只停止新闻连接

- `is_connected()`: 检查是否有任何连接活跃
- `is_stock_connected()`: 检查股票连接是否活跃
- `is_news_connected()`: 检查新闻连接是否活跃

**回调数据格式**

#### 股票数据格式

股票回调函数会接收到一个字典，包含股票的行情数据：

```json
{
    "security_id": "sh601008",      // 股票代码
    "security_name": "股票名称",     // 股票名称
    "open_px": "12.25",             // 今日开盘价,
    "pre_close_px": "12.10",        // 昨收价
    "last_px": "12.34",             // 最新价格
    "high_px": "12.70",             // 今天最高价
    "low_px": "11.86",              // 今天最高价
    "volume": "70633800",           // 今日成交量
    "amount": "520872627.000",      // 今日成交额度
    "date_time": "2023-04-16 15:30:45",      // 时间
    "bid": [
      [
        "12.33",      // 买一价格
        "50000"       // 买一数量
      ],    
      [
        "12.32", 
        "50000"
      ],    
      [
        "12.31", 
        "50000"
      ],    
      [
        "12.30", 
        "50000"
      ],   
      [
        "12.29", 
        "50000"
      ]
    ],  
    "ask": [
      [
        "12.34",      // 卖一价格
        "50000"       // 卖一数量
      ],    
      [
        "12.35", 
        "50000"
      ],    
      [
        "12.36", 
        "50000"
      ],    
      [
        "12.37", 
        "50000"
      ],   
      [
        "12.38", 
        "50000"
      ]
    ]

}
```

#### 新闻数据格式

新闻回调函数会接收到一个字典，包含新闻数据：

```json
{
    "type": "news",                    // 数据类型，固定为"news"
    "content": "重要财经新闻内容...",    // 新闻内容
    "timestamp": "2024-01-15 14:30:25" // 新闻时间戳
}
```

### 5、完整示例

完整示例请参考 `examples/websocket_example.py`，支持股票和新闻订阅，包含性能测量功能。

#### 运行示例：

```bash
# 只订阅股票行情
python examples/websocket_example.py -m stock -s sh601008 sz002640 -d 3

# 只订阅新闻
python examples/websocket_example.py -m news

# 同时订阅股票和新闻（默认）
python examples/websocket_example.py -m both -s sh000001 sz399001 -d 5

# 查看所有参数
python examples/websocket_example.py --help
```

#### 参数说明：

- `-m, --mode`: 订阅模式 (stock/news/both)
- `-s, --symbols`: 股票代码列表
- `-d, --depth`: 行情深度 (1-5)
- `-H, --host`: 服务器地址
- `-P, --port`: 服务器端口

## 三、ztData Api

### 1、快速开始
以下是一个简单的示例，展示如何使用ztdata客户端创建表并操作数据：

```python
from ZTData import DataClient, ZTData, ColumnType

# 初始化客户端
client = DataClient()

# 使用数据分类方式访问
news_category = ZTData.Stock.News
quotes_category = ZTData.Stock.Quotes

# 创建新闻数据表
table_info = {
    "table_name": "news_table",
    "chinese_name": "新闻数据表",
    "description": "存储股票相关新闻数据",
    "extension": "" # 扩展数据，非必填，将放在建表语句最后分号前面，如questdb的：PARTITION BY DAY WAL DEDUP UPSERT KEYS(security_id, date_time)
}

# 可选：定义表结构
columns = [
    {
        "column_name": "title", 
        "data_type": ColumnType.STRING, 
        "chinese_name": "新闻标题", 
        "description": "新闻的标题",
        "is_primary_key": True
    },
    {
        "column_name": "content", 
        "data_type": ColumnType.TEXT, 
        "chinese_name": "新闻内容", 
        "description": "新闻的详细内容"
    },
    {
        "column_name": "tags", 
        "data_type": ColumnType.JSON, 
        "chinese_name": "标签", 
        "description": "新闻的标签列表"
    }
]

result = client.create_table(news_category, table_info, columns)
print(f"新闻表创建结果: {result}")

# 获取表信息
table_info_result = client.get_table_info(news_category, "news_table")
if table_info_result["code"] == 0 and "data" in table_info_result:
    print(f"表信息: {table_info_result['data']}")

# 插入单条数据
document = {
    "title": "测试新闻标题",
    "content": "这是测试新闻内容",
    "tags": ["测试", "示例"]
}
result = client.insert_one(news_category, "news_table", document)
print(f"数据插入结果: {result}")

# 批量插入数据
batch_documents = [
    {"title": "批量测试标题1", "content": "批量测试内容1", "tags": ["批量", "测试"]},
    {"title": "批量测试标题2", "content": "批量测试内容2", "tags": ["批量", "测试"]}
]
result = client.insert_many(news_category, "news_table", batch_documents)
print(f"批量插入结果: {result}")
```

更多示例请参考`examples/unified_example.py`。

### 2、数据分类

SDK提供了使用`ZTData`对象进行数据分类访问的方式：

- `ZTData.Stock.News` - 股票新闻数据
- `ZTData.Stock.Quotes` - 股票行情数据
- `ZTData.Stock.Finance` - 上市公司财报数据	
- `ZTData.Stock.Company` - 公司动向		
- `ZTData.Stock.Insider` - 内幕交易			
- `ZTData.Stock.Notice` - 公告			
- `ZTData.Stock.Special` - 特色数据				
- `ZTData.Stock.Config` - 配置				
- `ZTData.Stock.FinancePlatform` - 金融平台			
- `ZTData.Stock.OtherMarket` - 外汇、黄金、台湾指数等			

### 3、API参考

#### 插入数据

```python
# 插入单条数据
document = {
    "title": "测试新闻标题",
    "content": "这是测试新闻内容",
    "tags": ["测试", "示例"]
}
result = client.insert_one(ZTData.Stock.News, "news_table", document)
```

#### 批量插入数据

```python
# 批量插入数据
batch_documents = []
for i in range(3):
    batch_documents.append({
        "title": f"批量测试标题 {i+1}",
        "content": f"批量测试内容 {i+1}",
        "tags": ["批量", "测试"],
        "index": i+1
    })
result = client.insert_many(ZTData.Stock.News, "news_table", batch_documents)

```

#### 查询单条数据

```python
# 查询单条数据
filter_dict = {"tags": "测试"}
result = client.find_one(ZTData.Stock.News, "news_table", filter_dict)
```

#### 查询多条数据

```python
# 查询多条数据
filter_dict = {"tags": "测试","date_time":{"$gte":"2025-01-01","$lt":"2025-01-02"}}
result = client.find_many(ZTData.Stock.News, "news_table", filter_dict)

# 带分页的查询
result = client.find_many(
    ZTData.Stock.News, 
    "news_table", 
    filter_dict=filter_dict,
    page=1,
    page_size=10
)
```

#### 执行SQL查询

```python
# 执行SQL查询
sql_query = "SELECT * FROM news_table WHERE tags IN '测试'"
result = client.execute_sql(ZTData.Stock.News, sql_query)
```

#### 加载本地历史数据

`load_local_data` 方法可以高效地从本地parquet文件加载历史K线数据，使用polars进行快速数据处理。

**前置要求**
- 需要安装polars库：`pip install polars`
- 系统配置中需要设置`quotes_history`配置项，指向本地历史数据目录

**使用示例**

```python
from ZTData import DataClient
import time

# 初始化客户端
client = DataClient()

# 加载本地历史数据（组合使用多个参数）
start_time = time.time()
result = client.load_local_data(
    interval="15m",                   # 15分钟K线
    start_dt="2025-01-01",           # 开始日期
    end_dt="2025-01-10",             # 结束日期
    security_ids=["sz000001", "sh600000"],  # 指定股票代码
    max_rows=5000                    # 最多返回5000条数据
)
end_time = time.time()

if result["code"] == 0:
    df = result["data"]  # polars.DataFrame对象
    print(f"查询耗时: {end_time - start_time:.3f} 秒")
    print(f"数据量: {len(df)} 条记录")
    print(f"涉及股票: {df['security_id'].n_unique()} 只")
    print(f"时间范围: {df['date_time'].min()} 到 {df['date_time'].max()}")
    print(df.head())
else:
    print(f"查询失败: {result['message']}")
```

**参数说明**

- `interval` (str, 必填): 时间间隔，支持的格式包括：
  - `"1M"` - 月线
  - `"1w"` - 周线  
  - `"1d"` - 日线
  - `"1h"` - 1小时线
  - `"30m"` - 30分钟线
  - `"15m"` - 15分钟线
  - `"5m"` - 5分钟线
  - `"1m"` - 1分钟线

- `start_dt` (str, 可选): 开始日期，格式为"YYYY-MM-DD"，如"2025-01-01"

- `end_dt` (str, 可选): 结束日期，格式为"YYYY-MM-DD"，如"2025-01-31"

- `security_ids` (list, 可选): 股票代码列表，如["sz000001", "sh600000"]

- `max_rows` (int, 可选): 最大返回行数限制

**返回数据格式**

成功时返回包含polars.DataFrame的结果：

```python
{
    "code": 0,
    "message": "本地数据加载成功",
    "data": polars.DataFrame  # polars DataFrame对象
}
```

DataFrame包含以下字段：
- `date_time` (datetime): 交易时间，如"2024-01-15 09:30:00"
- `security_id` (str): 证券代码，如"sz000001"、"sh600000"
- `open_px` (float): 开盘价，单位为元
- `high_px` (float): 最高价，单位为元
- `low_px` (float): 最低价，单位为元
- `close_px` (float): 收盘价，单位为元
- `volume` (int): 成交量，单位为股
- `amount` (float): 成交额，单位为元



### 4、响应格式

所有API方法都返回统一的响应格式：

```python
{
    "code": 0,                # 状态码，0表示成功
    "message": "操作成功",      # 操作消息
    # 可能包含的其他数据...
}
```

根据不同的操作，响应中可能还包含以下字段：

- 数据查询操作: `data`（单条记录）或`results`（多条记录）
- 批量插入操作: `inserted_count`（插入的记录数量）
- 分页查询: `total`（总记录数）、`current_page`（当前页码）

### 5、返回数据示例

#### 创建表响应示例

```python
{
    "code": 0,
    "message": "表创建成功"
}
```

#### 数据插入响应示例

```python
{
    "code": 0,
    "message": "数据插入成功"
}
```

#### 批量插入响应示例

```python
{
    "code": 0,
    "message": "批量插入成功",
    "inserted_count": 3
}
```

#### 查询单条数据响应示例

```python
{
    "code": 0,
    "message": "数据查询成功",
    "data": {
        "title": "测试新闻标题",
        "content": "这是测试新闻内容",
        "tags": ["测试", "示例"]
    }
}
```

#### 查询多条数据响应示例

```python
{
    "code": 0,
    "message": "数据查询成功",
    "total": 5,            # 总记录数
    "current_page": 1,     # 当前页码
    "results": [
        {
            "title": "测试新闻标题1",
            "content": "这是测试新闻内容1",
            "tags": ["测试", "示例"]
        },
        {
            "title": "测试新闻标题2",
            "content": "这是测试新闻内容2",
            "tags": ["测试", "示例"]
        }
        # ... 更多记录
    ]
}
```

#### SQL执行响应示例

```python
{
    "code": 0,
    "message": "SQL执行成功",
    "results": [
        {
            "title": "测试新闻标题",
            "content": "这是测试新闻内容",
            "tags": ["测试", "示例"]
        }
        # ... 更多记录
    ]
}
```

### 6、注意事项

- API返回的状态码0表示操作成功，非0表示操作失败。
- 对于批量数据处理，建议使用批量插入API以提高性能。
- 对于大量数据查询，建议使用分页功能。
- 如果遇到连接问题，请检查服务器地址和端口是否正确。

### 7、数据列类型

ZTData支持多种数据列类型，可通过`ColumnType`常量类访问：

```python
from ZTData import ColumnType

# 字符串类型
ColumnType.STRING      # 普通字符串
ColumnType.TEXT        # 长文本

# 数值类型
ColumnType.INTEGER     # 32位整数 (INT)
ColumnType.BIGINT      # 64位整数
ColumnType.FLOAT       # 单精度浮点数
ColumnType.DOUBLE      # 双精度浮点数
ColumnType.DECIMAL     # 高精度数值

# 布尔类型
ColumnType.BOOLEAN     # 布尔值 (BOOL)

# 日期时间类型
ColumnType.DATE        # 日期
ColumnType.DATETIME    # 日期时间
ColumnType.TIMESTAMP   # 时间戳

# 特殊类型
ColumnType.JSON        # JSON数据（如数组、对象）
ColumnType.SYMBOL      # 符号/枚举
```

使用示例：

```python
columns = [
    {
        "column_name": "user_id",
        "data_type": ColumnType.INTEGER,
        "chinese_name": "用户ID",
        "description": "用户唯一标识",
        "is_primary_key": True
    },
    {
        "column_name": "user_name",
        "data_type": ColumnType.STRING,
        "chinese_name": "用户名",
        "description": "用户名称"
    },
    {
        "column_name": "profile",
        "data_type": ColumnType.JSON,
        "chinese_name": "个人资料",
        "description": "用户的详细资料，JSON格式"
    },
    {
        "column_name": "register_time",
        "data_type": ColumnType.DATETIME,
        "chinese_name": "注册时间",
        "description": "用户的注册时间"
    }
]
```


