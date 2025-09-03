import grpc
import json
import os
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 确保可以导入生成的gRPC模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .generated import datasource_pb2, datasource_pb2_grpc

# 尝试导入pandas，如果没有安装则使用None
try:
    import pandas as pd
    import pyarrow.dataset as ds
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    PANDAS_AVAILABLE = False

# 列数据类型常量类
class ColumnType:
    """数据列类型常量定义"""
    STRING = "STRING"       # 字符串类型
    TEXT = "TEXT"           # 长文本类型
    INTEGER = "INT"         # 32位整数
    BIGINT = "BIGINT"       # 64位整数
    FLOAT = "FLOAT"         # 单精度浮点数
    DOUBLE = "DOUBLE"       # 双精度浮点数
    DECIMAL = "DECIMAL"     # 高精度数值
    BOOLEAN = "BOOL"        # 布尔值
    DATE = "DATE"           # 日期
    DATETIME = "DATETIME"   # 日期时间
    TIMESTAMP = "TIMESTAMP" # 时间戳
    JSON = "JSON"           # JSON数据
    SYMBOL = "SYMBOL"       # 符号/枚举

# 添加分类结构类
class Category:
    """分类名称类，用于表示数据分类路径"""
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name

class StockCategory:
    """股票相关分类"""
    def __init__(self, prefix):
        self.prefix = prefix
        self.News = Category(f"{prefix}.Stock.News")
        self.Quotes = Category(f"{prefix}.Stock.Quotes")
        self.Hot = Category(f"{prefix}.Stock.Hot")
        self.Transactions = Category(f"{prefix}.Stock.Transactions")
        self.Analysis = Category(f"{prefix}.Stock.Analysis")
        self.Config = Category(f"{prefix}.Stock.Config")
        self.Finance = Category(f"{prefix}.Stock.Finance")
        self.Company = Category(f"{prefix}.Stock.Company")
        self.Insider = Category(f"{prefix}.Stock.Insider")
        self.Notice = Category(f"{prefix}.Stock.Notice")
        self.Special = Category(f"{prefix}.Stock.Special")
        self.FinancePlatform = Category(f"{prefix}.Stock.FinancePlatform")
        self.OtherMarket = Category(f"{prefix}.Stock.OtherMarket")
        self.QuotesHis = Category(f"{prefix}.Stock.QuotesHis")

class ZTDataCategory:
    """ZTData顶层分类"""
    def __init__(self, prefix="ZTData"):
        self.prefix = prefix
        self.Stock = StockCategory(prefix)
    
    def __str__(self):
        return self.prefix

# 全局变量，直接导入即可使用
ZTData = ZTDataCategory()

class DataClient:
    def __init__(self, host="182.131.21.179", port=39123):
        """
        初始化统一数据客户端
        
        参数:
            host (str): gRPC服务器主机地址
            port (int): gRPC服务器端口
        """
        # 创建gRPC通道
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        
        # 初始化ZtData存根
        self.stub = datasource_pb2_grpc.ZtDataStub(self.channel)
        
        # 保存模块引用以便后续使用
        self.datasource_pb2 = datasource_pb2
        
        # 批量插入时的最大批次大小
        self.max_batch_size = 5000

        self.PREFIX = "ZTData."
    
    def _format_source_name(self, category):
        """
        格式化资源名称
        
        参数:
            category (str或Category): 分类名称，如"Stock.News"或ZTData.Stock.News
            
        返回:
            str: 格式化后的资源名称，如"ZTData.Stock.News"
            str: 简化后的分类名，如"Stock.News"
        """
        if isinstance(category, Category):
            full_name = str(category)
            if full_name.startswith(self.PREFIX):
                simple_name = full_name[len(self.PREFIX):]
            else:
                simple_name = full_name
            return full_name, simple_name
        
        if isinstance(category, str):
            if category.startswith(self.PREFIX):
                return category, category[len(self.PREFIX):]
            return f"{self.PREFIX}{category}", category
        
        raise ValueError(f"不支持的分类类型: {type(category)}")
    
    def _get_db_type(self, simple_category):
        """
        根据分类名称获取数据库类型
        
        参数:
            simple_category (str): 简化的分类名称，如"Stock.News"
            
        返回:
            int: 数据库类型常量
        """
        return self.DB_TYPE_MAP.get(simple_category, self.DB_MYSQL)  # 默认为MySQL类型
    
    def create_table(self, category, table_info, columns):
        """
        创建表或集合
        
        参数:
            category (str或Category): 分类名称，如"Stock.News"或ZTData.Stock.News
            table_info (dict): 表信息，必须包含table_name、chinese_name、description 和 extension
            columns (list, optional): 列定义列表，每个列定义必须包含column_name, data_type, chinese_name和description，可选is_primary_key
            
        返回:
            dict: 包含操作状态码和消息的响应
        """
        source_name, simple_category = self._format_source_name(category)
        
        try:
            # 验证table_info必填字段
            if not isinstance(table_info, dict):
                raise ValueError("table_info必须是字典类型")
            
            if "table_name" not in table_info or not table_info["table_name"]:
                raise ValueError("table_info必须包含非空的table_name字段")
            
            if "chinese_name" not in table_info or not table_info["chinese_name"]:
                raise ValueError("table_info必须包含非空的chinese_name字段")
            
            if "description" not in table_info or not table_info["description"]:
                raise ValueError("table_info必须包含非空的description字段")
            

            # 创建table_info请求对象
            req_table_info = self.datasource_pb2.ReqTableInfo(
                table_name=table_info["table_name"],
                chinese_name=table_info["chinese_name"],
                description=table_info["description"],
                extension=table_info.get("extension",'')
            )
            
            # 处理列定义
            req_columns = []
            if columns:
                for i, col in enumerate(columns):
                    # 验证必填字段
                    if "column_name" not in col or not col["column_name"]:
                        raise ValueError(f"第{i+1}列必须包含非空的column_name字段")
                    
                    if "data_type" not in col or not col["data_type"]:
                        raise ValueError(f"第{i+1}列({col.get('column_name', '')})必须包含非空的data_type字段")
                    
                    if "chinese_name" not in col or not col["chinese_name"]:
                        raise ValueError(f"第{i+1}列({col.get('column_name', '')})必须包含非空的chinese_name字段")
                    
                    if "description" not in col or not col["description"]:
                        raise ValueError(f"第{i+1}列({col.get('column_name', '')})必须包含非空的description字段")
                    
                    req_column = self.datasource_pb2.ReqColumnInfo(
                        column_name=col["column_name"],
                        data_type=col["data_type"], 
                        chinese_name=col["chinese_name"],
                        description=col["description"],
                        is_primary_key=col.get("is_primary_key", False)
                    )
                    req_columns.append(req_column)
            
            # 创建请求
            request = self.datasource_pb2.CreateTableRequest(
                source_name=source_name,
                table_info=req_table_info,
                columns=req_columns
            )
            
            # 调用服务
            response = self.stub.CreateTable(request)
            
            # 返回结果
            return {
                "code": response.code,
                "message": response.message
            }
        except ValueError as ve:
            return {
                "code": 1,
                "message": str(ve)
            }
        except Exception as e:
            return {
                "code": 1,
                "message": f"创建表失败: {str(e)}"
            }
    
    def get_table_info(self, category, table_name):
        """
        获取表信息
        
        参数:
            category (str或Category): 分类名称，如"Stock.News"或ZTData.Stock.News
            table_name (str): 表名称
            
        返回:
            dict: 包含表信息的响应，如列定义等
        """
        source_name, _ = self._format_source_name(category)
        
        try:
            # 创建请求
            request = self.datasource_pb2.GetTableInfoRequest(
                source_name=source_name,
                table_name=table_name
            )
            
            # 调用服务
            response = self.stub.GetTableInfo(request)

            # 如果成功，格式化返回数据
            if response.code == 0:
                table_info = {
                    "table_id": response.data.table_id,
                    "table_name": response.data.table_name,
                    "chinese_name": response.data.chinese_name,
                    "description": response.data.description,
                    "columns": []
                }

                # 处理列信息
                for col in response.data.columns:
                    column_info = {
                        "column_name": col.column_name,
                        "data_type": col.data_type,
                        "chinese_name": col.chinese_name,
                        "description": col.description,
                        "is_primary_key": col.is_primary_key
                    }
                    table_info["columns"].append(column_info)

                return {
                    "code": response.code,
                    "message": response.message,
                    "data": table_info
                }
            else:
                return {
                    "code": response.code,
                    "message": response.message
                }
        except Exception as e:
            return {
                "code": 1,
                "message": f"获取表信息失败: {str(e)}"
            }
    
    def delete_table(self, category, table_name):
        """
        删除表或集合
        
        参数:
            category (str或Category): 分类名称，如"Stock.News"或ZTData.Stock.News
            table_name (str): 表名称
            
        返回:
            dict: 包含操作状态码和消息的响应
        """
        source_name, _ = self._format_source_name(category)
        
        try:
            request = self.datasource_pb2.DeleteTableRequest(
                source_name=source_name,
                table_name=table_name
            )
            
            response = self.stub.DeleteTable(request)
            
            return {
                "code": response.code,
                "message": response.message
            }
        except Exception as e:
            return {
                "code": 1,
                "message": f"删除表失败: {str(e)}"
            }
    
    def insert_one(self, category, table_name, data):
        """
        插入单条数据
        
        参数:
            category (str或Category): 分类名称，如"Stock.News"或ZTData.Stock.News
            table_name (str): 表名称
            data (dict): 要插入的数据
            
        返回:
            dict: 包含操作状态码、消息和数据的响应
        """
        source_name, _ = self._format_source_name(category)
        
        try:
            json_data = json.dumps(data).encode('utf-8')
            
            request = self.datasource_pb2.InfoRequest(
                source_name=source_name,
                table_name=table_name,
                data=json_data
            )
            
            response = self.stub.InsertOne(request)
            
            result = {
                "code": response.code,
                "message": response.message
            }
            
            if response.data:
                result["data"] = json.loads(response.data.decode('utf-8'))
                
            return result
        except Exception as e:
            return {
                "code": 1,
                "message": f"插入数据失败: {str(e)}"
            }
    
    def delete_data(self, category, table_name, filter_dict):
        """
        根据条件删除数据
        
        参数:
            category (str或Category): 分类名称，如"Stock.News"或ZTData.Stock.News
            table_name (str): 表名称
            filter_dict (dict): 删除条件
            
        返回:
            dict: 包含操作状态码和消息的响应
        """
        source_name, _ = self._format_source_name(category)
        
        try:
            filter_bytes = json.dumps(filter_dict).encode('utf-8')
            
            request = self.datasource_pb2.DeleteRequest(
                source_name=source_name,
                table_name=table_name,
                filter=filter_bytes
            )
            
            response = self.stub.DeleteData(request)
            
            return {
                "code": response.code,
                "message": response.message
            }
        except Exception as e:
            return {
                "code": 1,
                "message": f"删除数据失败: {str(e)}"
            }
    
    def update_data(self, category, table_name, filter_dict, update_data):
        """
        根据条件更新数据
        
        参数:
            category (str或Category): 分类名称，如"Stock.News"或ZTData.Stock.News
            table_name (str): 表名称
            filter_dict (dict): 更新条件
            update_data (dict): 要更新的数据
            
        返回:
            dict: 包含操作状态码和消息的响应
        """
        source_name, _ = self._format_source_name(category)
        
        try:
            filter_bytes = json.dumps(filter_dict).encode('utf-8')
            data_bytes = json.dumps(update_data).encode('utf-8')
            
            request = self.datasource_pb2.UpdateRequest(
                source_name=source_name,
                table_name=table_name,
                filter=filter_bytes,
                data=data_bytes
            )
            
            response = self.stub.UpdateData(request)
            
            return {
                "code": response.code,
                "message": response.message
            }
        except Exception as e:
            return {
                "code": 1,
                "message": f"更新数据失败: {str(e)}"
            }
    
    def insert_many(self, category, table_name, data_list):
        """
        批量插入多条数据
        
        参数:
            category (str或Category): 分类名称，如"Stock.News"或ZTData.Stock.News
            table_name (str): 表名称
            data_list (list): 要插入的数据列表，每项是一个dict
            
        返回:
            dict: 包含操作状态码、消息和插入结果的响应
        """
        if not data_list:
            return {
                "code": 0,
                "message": "",
                "inserted_count": 0
            }
        
        source_name, _ = self._format_source_name(category)
        total_records = len(data_list)
        inserted_count = 0
        
        # 按批次处理数据
        for batch_start in range(0, total_records, self.max_batch_size):
            batch_end = min(batch_start + self.max_batch_size, total_records)
            batch = data_list[batch_start:batch_end]
            
            try:
                json_data_list = [json.dumps(data).encode('utf-8') for data in batch]
                
                request = self.datasource_pb2.InsertManyRequest(
                    source_name=source_name,
                    table_name=table_name,
                    records=json_data_list
                )
                
                response = self.stub.InsertMany(request)
                
                if response.code == 0:
                    inserted_count += response.inserted_count
                else:
                    # 批量插入失败，直接返回错误
                    return {
                        "code": response.code,
                        "message": response.message,
                        "inserted_count": inserted_count
                    }
            except Exception as e:
                return {
                    "code": 1,
                    "message": f"批量插入失败: {str(e)}",
                    "inserted_count": inserted_count
                }
        
        # 全部成功
        return {
            "code": 0,
            "message": "",
            "inserted_count": inserted_count
        }
    
    def find_one(self, category, table_name, filter_dict=None, sort_conditions=None, projection=None):
        """
        查询单条数据
        
        参数:
            category (str或Category): 分类名称，如"Stock.News"或ZTData.Stock.News
            table_name (str): 表名称
            filter_dict (dict, optional): 过滤条件
            sort_conditions (list, optional): 排序条件，格式为[("field_name", True/False)]，True表示升序
            projection (list, optional): 返回的字段列表
            
        返回:
            dict: 包含操作状态码、消息和数据的响应
        """
        if filter_dict is None:
            filter_dict = {}
        if sort_conditions is None:
            sort_conditions = []
        if projection is None:
            projection = []
        
        source_name, _ = self._format_source_name(category)
        
        try:
            filter_bytes = json.dumps(filter_dict).encode('utf-8')
            
            query = self.datasource_pb2.QueryCondition(
                source_name=source_name,
                table_name=table_name,
                filter=filter_bytes,
                projection=projection
            )
            
            # 添加排序条件
            for field, is_ascending in sort_conditions:
                sort = self.datasource_pb2.SortCondition(field=field, ascending=is_ascending)
                query.sorts.append(sort)
            
            response = self.stub.FindOne(query)
            
            result = {
                "code": response.code,
                "message": response.message
            }
            
            if response.data:
                result["data"] = json.loads(response.data.decode('utf-8'))
                
            return result
        except Exception as e:
            return {
                "code": 1,
                "message": f"查询单条数据失败: {str(e)}"
            }
    
    def find_many(self, category, table_name, filter_dict=None, sort_conditions=None, projection=None, page=1, page_size=None):
        """
        查询多条数据，2000，则分批获取
        
        参数:
            category (str或Category): 分类名称，如"Stock.News"或ZTData.Stock.News
            table_name (str): 表名称
            filter_dict (dict, optional): 过滤条件
            sort_conditions (list, optional): 排序条件，格式为[("field_name", True/False)]，True表示升序
            projection (list, optional): 返回的字段列表
            page (int): 页码，从1开始
            page_size (int, optional): 每页记录数，为None时获取所有数据，大于1000时会分批获取
            
        返回:
            dict: 包含操作状态码、消息和数据的响应
        """
        if filter_dict is None:
            filter_dict = {}
        if sort_conditions is None:
            sort_conditions = []
        if projection is None:
            projection = []

        # 如果page_size为None，获取所有数据
        if page_size is None:
            # 先获取一条数据以获取总条数
            first_result = self._find_many_single_batch(
                category, table_name, filter_dict, sort_conditions,
                projection, 1, 1
            )
            
            if first_result["code"] != 0:
                return first_result
            
            total_records = first_result["total"]
            
            # 如果没有数据，直接返回
            if total_records == 0:
                return {
                    "code": 0,
                    "message": "",
                    "total": 0,
                    "current_page": 1,
                    "results": []
                }
            

            # 将page_size设置为总记录数，让后面的逻辑自然判断
            page_size = total_records

        # 如果page_size > 2000，则分批遍历获取
        if page_size > 2000:
            return self._find_many_large_batch(
                category, table_name, filter_dict, sort_conditions, 
                projection, page, page_size
            )
        
        # 常规查询（page_size <= 2000）
        return self._find_many_single_batch(
            category, table_name, filter_dict, sort_conditions,
            projection, page, page_size
        )
    
    def _find_many_large_batch(self, category, table_name, filter_dict, sort_conditions, projection, page, page_size):
        """
        处理大批量数据查询（page_size > 2000），通过异步分批并发获取
        
        参数:
            category: 分类名称
            table_name: 表名称
            filter_dict: 过滤条件
            sort_conditions: 排序条件
            projection: 返回字段列表
            page: 页码
            page_size: 每页记录数
            
        返回:
            dict: 合并后的查询结果
        """
        batch_size = 2000  # 每批次固定2000条
        max_workers = 10   # 最大并发线程数
        
        # 计算用户真正需要的数据范围
        user_start_index = (page - 1) * page_size
        user_end_index = user_start_index + page_size - 1
        
        try:
            # 首先获取第一页数据以获取总数
            first_result = self._find_many_single_batch(
                category, table_name, filter_dict, sort_conditions,
                projection, 1, batch_size
            )
            
            if first_result["code"] != 0:
                return first_result
            
            total_records = first_result["total"]
            
            # 如果请求的起始位置超过总记录数，返回空结果
            if user_start_index >= total_records:
                return {
                    "code": 0,
                    "message": "",
                    "total": total_records,
                    "current_page": page,
                    "results": []
                }
            
            # 调整结束位置，不超过总记录数
            actual_end_index = min(user_end_index, total_records - 1)
            actual_need_count = actual_end_index - user_start_index + 1
            
            # 规划批次任务
            batch_tasks = []
            current_index = user_start_index
            

            while current_index <= actual_end_index:
                # 计算当前批次对应的page（基于固定的batch_size）
                batch_page = (current_index // batch_size) + 1
                
                # 计算当前批次需要的记录数
                remaining_in_batch = min(batch_size, actual_end_index - current_index + 1)
                
                # 计算在当前批次中的起始偏移量
                offset_in_batch = current_index % batch_size
                

                batch_tasks.append({
                    'page': batch_page,
                    'size': batch_size,  # 固定使用batch_size
                    'start_index': current_index,
                    'offset_in_batch': offset_in_batch,
                    'need_records': remaining_in_batch
                })
                
                current_index += batch_size - offset_in_batch  # 跳到下一个批次的开始


            # 使用线程池并发执行批次任务
            all_results = []
            batch_results = {}  # 存储每个批次的结果，保持顺序
            
            with ThreadPoolExecutor(max_workers=min(max_workers, len(batch_tasks))) as executor:
                # 提交所有任务
                future_to_task = {}
                for i, task in enumerate(batch_tasks):
                    future = executor.submit(
                        self._find_many_single_batch,
                        category, table_name, filter_dict, sort_conditions,
                        projection, task['page'], task['size']
                    )
                    future_to_task[future] = (i, task)
                
                # 等待所有任务完成
                for future in as_completed(future_to_task):
                    task_index, task_info = future_to_task[future]
                    
                    try:
                        batch_result = future.result()
                        
                        if batch_result["code"] != 0:
                            return batch_result
                        
                        # 如果没有数据，跳过
                        if not batch_result["results"]:
                            continue
                        
                        batch_results[task_index] = {
                            'data': batch_result["results"],
                            'task_info': task_info,
                            'actual_count': len(batch_result["results"])
                        }


                    except Exception as e:
                        return {
                            "code": 1,
                            "message": f"批次 {task_info['page']} 查询失败: {str(e)}"
                        }
            
            # 按顺序合并结果并精确截取用户需要的数据
            for i in range(len(batch_tasks)):
                if i not in batch_results:
                    continue
                
                batch_info = batch_results[i]
                batch_data = batch_info['data']
                task_info = batch_info['task_info']
                
                # 计算在当前批次中需要截取的数据范围
                offset_in_batch = task_info['offset_in_batch']
                need_records = task_info['need_records']
                

                # 从批次数据中截取需要的部分
                start_idx = offset_in_batch
                end_idx = min(start_idx + need_records, len(batch_data))
                
                if start_idx < len(batch_data):
                    selected_data = batch_data[start_idx:end_idx]
                    all_results.extend(selected_data)


            # 最终检查，确保不超过用户请求的数量
            if len(all_results) > actual_need_count:
                all_results = all_results[:actual_need_count]

            return {
                "code": 0,
                "message": "",
                "total": total_records,
                "current_page": page,
                "results": all_results
            }
            
        except Exception as e:
            return {
                "code": 1,
                "message": f"异步分批查询多条数据失败: {str(e)}"
            }
    
    def _find_many_single_batch(self, category, table_name, filter_dict, sort_conditions, projection, page, page_size):
        """
        单批次查询数据（page_size <= 1000）
        
        参数:
            category: 分类名称
            table_name: 表名称
            filter_dict: 过滤条件
            sort_conditions: 排序条件
            projection: 返回字段列表
            page: 页码
            page_size: 每页记录数
            
        返回:
            dict: 查询结果
        """
        source_name, _ = self._format_source_name(category)
        
        try:
            filter_bytes = json.dumps(filter_dict).encode('utf-8')
            
            # 构建查询条件
            query = self.datasource_pb2.QueryCondition(
                source_name=source_name,
                table_name=table_name,
                filter=filter_bytes,
                projection=projection
            )
            
            # 添加排序条件
            for field, is_ascending in sort_conditions:
                sort = self.datasource_pb2.SortCondition(field=field, ascending=is_ascending)
                query.sorts.append(sort)
            
            # 构建分页请求
            request = self.datasource_pb2.PaginationRequest(
                query=query,
                page=page,
                page_size=page_size
            )
            
            response = self.stub.FindMany(request)
            
            result = {
                "code": response.code,
                "message": response.message,
                "total": response.total,
                "current_page": response.current_page,
                "results": []
            }
            
            # 解析返回的记录
            for record_bytes in response.results:
                result["results"].append(json.loads(record_bytes.decode('utf-8')))
                
            return result
        except Exception as e:
            return {
                "code": 1,
                "message": f"查询多条数据失败: {str(e)}"
            }
    
    def execute_sql(self, category, sql, params=None):
        """
        执行SQL查询
        
        参数:
            category (str或Category): 分类名称，如"Stock.News"或ZTData.Stock.News
            sql (str): SQL查询语句
            params (dict, optional): 参数
            
        返回:
            dict: 包含操作状态码、消息和结果的响应
        """
        if params is None:
            params = {}
        
        # 确保SQL是SELECT语句
        sql_upper = sql.strip().upper()
        if not sql_upper.startswith("SELECT"):
            return {
                "code": 1,
                "message": "只允许执行SELECT语句"
            }
        
        source_name, _ = self._format_source_name(category)
        
        try:
            params_bytes = json.dumps(params).encode('utf-8') if params else None
            
            request = self.datasource_pb2.SQLRequest(
                source_name=source_name,
                query=sql,
                params=params_bytes
            )
            
            response = self.stub.ExecuteSQL(request)
            
            result = {
                "code": response.code,
                "message": response.message
            }
            
            # 解析结果
            if response.results:
                result["results"] = json.loads(response.results.decode('utf-8'))
                
            return result
        except Exception as e:
            return {
                "code": 1,
                "message": f"执行SQL失败: {str(e)}"
            }

    def load_local_data(self,
                        interval,
                        start_dt=None,
                        end_dt=None,
                        security_ids=None,
                        latest_rows=None):
        """
        从本地parquet文件加载数据，使用pandas进行高效处理，root_path从系统配置中自动获取

        参数:
            interval (str): 时间间隔，如"1M", "1w", "1d", "1h", "30m", "15m", "5m", "1m"等
            start_dt (str, optional): 开始时间，例如"2025-01-01"，默认None
            end_dt (str, optional): 结束时间，例如"2025-01-01"，默认None
            security_ids (list, optional): 证券ID列表，用于过滤特定股票，例如["000001", "600000"]，默认None
            latest_rows (int, optional): 返回最近的行数，例如1000，默认None

        返回:
            dict: 包含操作状态码、消息和数据的响应
                 成功时data字段包含pandas.DataFrame对象
                 包含字段:
                 - date_time (datetime): 交易时间，格式如"2024-01-15 09:30:00"
                 - security_id (str): 证券代码，如"000001"、"600000"
                 - open_px (float): 开盘价，单位为元
                 - high_px (float): 最高价，单位为元
                 - low_px (float): 最低价，单位为元
                 - close_px (float): 收盘价，单位为元
                 - volume (int): 成交量，单位为股
                 - amount (float): 成交额，单位为元
        """
        # 检查pandas是否可用
        if not PANDAS_AVAILABLE:
            return {
                "code": 1,
                "message": "缺少必要依赖：请安装 pandas 和 pyarrow 库"
            }

        # 参数验证
        if not interval or not isinstance(interval, str):
            return {
                "code": 1,
                "message": "interval 参数不能为空且必须是字符串类型"
            }

        # 从系统配置中获取root_path
        config_result = self.find_one(
            category=ZTData.Stock.Config,
            table_name="system_config",
            filter_dict={"skey": "quotes_history"}
        )

        if config_result["code"] != 0:
            return {
                "code": 1,
                "message": f"获取系统配置失败: {config_result['message']}"
            }

        if "data" not in config_result or not config_result["data"]:
            return {
                "code": 1,
                "message": "未找到quotes_history配置项"
            }

        config_data = config_result["data"]
        if "svalue" not in config_data or not config_data["svalue"]:
            return {
                "code": 1,
                "message": "quotes_history配置项的value字段为空"
            }

        root_path = config_data["svalue"]

        try:
            # 1. 使用pyarrow.dataset读取分区数据
            dataset_path = f"{root_path}/kline_qfq/interval={interval}"
            dataset = ds.dataset(dataset_path, format='parquet')
            df = dataset.to_table().to_pandas()
            df = df.sort_values(by='date_time')

            if start_dt is not None:
                start_dt = datetime.strptime(start_dt + " 00:00:00", "%Y-%m-%d %H:%M:%S")
            if end_dt is not None:
                end_dt = datetime.strptime(end_dt + " 23:59:59", "%Y-%m-%d %H:%M:%S")

            # 2. 动态添加"时间范围"过滤条件
            if start_dt and end_dt:
                df = df[
                    (df['date_time'] >= start_dt) &
                    (df['date_time'] <= end_dt)
                ]

            # 3. 如果没有指定时间范围，则获取最新数据
            if start_dt is None and end_dt is None and latest_rows is not None:
                new_start_dt = self._get_start_df_from_offset_rows(interval, end_dt, latest_rows)
                if new_start_dt:
                    df = df[df['date_time'] >= new_start_dt]

            # 3. 动态添加"证券ID"过滤条件
            if security_ids:
                df = df[df['security_id'].isin(security_ids)]

            # 4. 满足 latest_rows 行数的股票数据的最新数据
            if latest_rows:
                df = df.groupby('security_id').tail(latest_rows)

            # 5. 只取股票价格大于0
            df = df[
                df['open_px'] > 0  # 确保价格大于0
            ][['date_time', 'security_id', 'open_px', 'high_px', 'low_px', 'close_px', 'volume', 'amount']]

            return {
                "code": 0,
                "message": "本地数据加载成功",
                "data": df
            }

        except Exception as e:
            return {
                "code": 1,
                "message": f"加载本地数据失败: {str(e)}"
            }

    def _get_start_df_from_offset_rows(self, interval: str, end_dt: datetime, latest_rows: int,
                                       offset_rows=100) -> datetime:
        """ 基于最新数量, 向前多查询100天数据, 防止因短期停牌导致数据不完整, 实盘时可用
        """
        max_rows = latest_rows + offset_rows
        return self._get_start_dt_from_max_rows(interval, end_dt, max_rows)

    def _get_start_dt_from_max_rows(self, interval: str, end_dt: datetime, max_rows: int):
        """
        根据最大行数获取开始时间

        参数:
            interval (str): 时间间隔
            end_dt (datetime): 结束时间
            max_rows (int): 最大行数

        返回:
            datetime: 计算出的开始时间
        """

        def _query_first_trading_date(end_date: str, limit: int):
            # 向前查询交易日历
            condition = {
                'exchange_date': {'$lt': int(end_date)}
            }
            sortconditions = [("exchange_date", False)]
            res = self.find_many(
                category=ZTData.Stock.Config,
                table_name="trading_calendar",
                filter_dict=condition,
                sort_conditions=sortconditions,
                page_size=limit
            )
            new_list = res.get("results", [])

            # 降序查询, 只返回最后一条数据的 exchange_date
            if new_list:
                return new_list[-1]['exchange_date']

        end_date = datetime.strftime(end_dt, "%Y%m%d") if end_dt else datetime.now().strftime("%Y%m%d")
        # A股每日交易时间(4小时)
        TRADING_HOURS_PER_DAY = 4

        try:
            # 计算每个周期的时间长度(考虑A股实际交易时间)
            if interval.endswith('m'):
                counts = int(interval[:-1])
                trading_days = (counts * max_rows) // (60 * TRADING_HOURS_PER_DAY)

            elif interval.endswith('h'):
                counts = int(interval[:-1])
                trading_days = (counts * max_rows) // TRADING_HOURS_PER_DAY

            elif interval.endswith('d'):
                counts = int(interval[:-1])
                trading_days = counts * max_rows

            elif interval.endswith('w'):
                counts = int(interval[:-1])
                trading_days = counts * 5 * max_rows

            elif interval.endswith('M'):
                counts = int(interval[:-1])
                trading_days = counts * 22 * max_rows

            else:
                raise ValueError(f"不支持的K线周期: {interval}")

            days = trading_days + 2
            first_date = _query_first_trading_date(end_date=end_date, limit=days)

            if first_date:
                # 计算起始时间
                start_dt = datetime.strptime(str(first_date), "%Y%m%d")
                return start_dt

        except ValueError as e:
            raise ValueError(f"无效的K线周期格式: {interval} from error: {e}")
        return

    def _get_interval_child_path(self, interval: str) -> str:
        """ 获取 interval 对应的子路径
        :param interval: K 线周期, 如 '1m', '5m', '15m', '30m', '1h', '1d', '1w', '1M'
        """
        if interval == '1w':
            return "year=*/week=*/*.parquet"
        elif interval == '1M':
            return "year=*/month=*/*.parquet"
        else:
            return "year=*/month=*/day=*/*.parquet"