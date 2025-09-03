#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ZTQuant WebSocket客户端模块 - 用于实时行情数据订阅"""

import json
import websocket
import threading
import time
import logging
from typing import List, Dict, Union, Callable, Optional

class WsClient:
    """WebSocket客户端，支持行情数据和新闻订阅"""
    
    # WebSocket服务路径常量
    PATH_STOCK = "/ws/stock"    # 股票行情路径
    PATH_NEWS = "/ws/news"      # 新闻订阅路径
    
    def __init__(self, 
                 host: str = "182.131.21.179", 
                 port: int = 37123,
                 log_level: int = logging.INFO):
        """
        初始化WebSocket客户端
        
        参数:
            host: WebSocket服务器主机
            port: WebSocket服务器端口  
            log_level: 日志级别
        """
        self.host = host
        self.port = port
        self.base_url = f"ws://{host}:{port}"
        
        # 股票连接相关
        self.stock_ws = None
        self.stock_running = False
        self.on_stock_callback = None
        
        # 新闻连接相关  
        self.news_ws = None
        self.news_running = False
        self.on_news_callback = None
        
        # 设置日志
        self.logger = logging.getLogger("WsClient")
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
    def _on_stock_message(self, ws, message):
        """处理股票消息"""
        try:
            data = json.loads(message)
                
            # 如果有股票回调函数，则调用回调函数处理原始数据
            if self.on_stock_callback:
                self.on_stock_callback(data)
                
            # 记录日志
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"收到股票数据: {data.get('security_id', '')}, {data.get('security_name', '')}")
                
        except json.JSONDecodeError:
            self.logger.error(f"解析股票消息失败: {message}")
        except Exception as e:
            self.logger.error(f"处理股票消息错误: {e}")

    def _parse_news_records(self, message):
        """解析可能包含多条JSON记录的消息"""
        message = message.strip()
        if not message:
            return []
        
        records = []
        
        # 尝试按换行符分割
        lines = message.split('\n')
        if len(lines) > 1:
            for line in lines:
                line = line.strip()
                if line and self._is_valid_json(line):
                    records.append(line)
            if records:
                return records
        
        # 尝试解析为单条JSON记录
        if self._is_valid_json(message):
            return [message]
        
        # 尝试分割连接的JSON记录（查找 "}{"模式）
        parts = message.split('}{')
        if len(parts) > 1:
            for i, part in enumerate(parts):
                if i == 0:
                    # 第一部分，添加结束括号
                    part = part + '}'
                elif i == len(parts) - 1:
                    # 最后一部分，添加开始括号
                    part = '{' + part
                else:
                    # 中间部分，添加开始和结束括号
                    part = '{' + part + '}'
                
                if self._is_valid_json(part):
                    records.append(part)
        
        # 如果所有方法都失败，返回原始消息
        if not records:
            return [message]
        
        return records
    
    def _is_valid_json(self, text):
        """检查字符串是否为有效的JSON"""
        try:
            json.loads(text)
            return True
        except (json.JSONDecodeError, ValueError):
            return False

    def _on_news_message(self, ws, message):
        """处理新闻消息"""
        try:
            # 解析可能包含多条JSON记录的消息
            news_records = self._parse_news_records(message)
            
            for record_str in news_records:
                try:
                    data = json.loads(record_str)
                    
                    # 服务器现在直接返回原始新闻数据，无需验证type字段
                    # 如果有新闻回调函数，则调用回调函数处理原始数据
                    if self.on_news_callback:
                        self.on_news_callback(data)
                        
                    # 记录日志
                    if self.logger.isEnabledFor(logging.DEBUG):
                        # 尝试从不同可能的字段中获取内容预览
                        content_preview = ""
                        if 'row_data' in data:
                            content_preview = str(data.get('row_data', ''))[:50] + "..." if len(str(data.get('row_data', ''))) > 50 else str(data.get('row_data', ''))
                        elif 'content' in data:
                            content_preview = str(data.get('content', ''))[:50] + "..." if len(str(data.get('content', ''))) > 50 else str(data.get('content', ''))
                        else:
                            content_preview = str(data)[:50] + "..." if len(str(data)) > 50 else str(data)
                        
                        self.logger.debug(f"收到新闻数据: {content_preview}")
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"解析单条新闻记录失败: {record_str[:100]}... 错误: {e}")
                except Exception as e:
                    self.logger.error(f"处理单条新闻记录错误: {e}")
                
        except Exception as e:
            self.logger.error(f"处理新闻消息错误: {e}")
            # 如果解析失败，尝试作为原始消息处理
            self.logger.debug(f"原始消息内容: {message[:200]}...")

    def _on_stock_error(self, ws, error):
        """处理股票WebSocket错误"""
        self.logger.error(f"股票WebSocket错误: {error}")

    def _on_stock_close(self, ws, close_status_code, close_msg):
        """处理股票连接关闭"""
        self.logger.info(f"股票WebSocket连接关闭: {close_status_code} - {close_msg}")
        self.stock_running = False

    def _on_stock_open(self, ws):
        """处理股票连接打开"""
        self.logger.info("股票WebSocket连接已建立")
        self._handle_stock_subscription(ws)

    def _on_news_error(self, ws, error):
        """处理新闻WebSocket错误"""
        self.logger.error(f"新闻WebSocket错误: {error}")

    def _on_news_close(self, ws, close_status_code, close_msg):
        """处理新闻连接关闭"""
        self.logger.info(f"新闻WebSocket连接关闭: {close_status_code} - {close_msg}")
        self.news_running = False

    def _on_news_open(self, ws):
        """处理新闻连接打开"""
        self.logger.info("新闻WebSocket连接已建立")
        self._handle_news_subscription(ws)
    
    def _handle_stock_subscription(self, ws):
        """处理股票订阅"""
        # 发送订阅请求
        def run(*args):
            try:
                # 订阅股票
                symbols = self.symbols
                depth = self.depth
                
                subscription = {
                    "symbols": symbols,
                    "depth": depth
                }
                
                self.logger.info(f"股票订阅: {json.dumps(subscription, ensure_ascii=False)}")
                ws.send(json.dumps(subscription))
                
                # 保持连接
                while self.stock_running:
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"发送股票订阅请求错误: {e}")
            finally:
                if self.stock_running:
                    self.logger.info("关闭股票连接...")
                    ws.close()
        
        # 启动订阅线程
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

    def _handle_news_subscription(self, ws):
        """处理新闻订阅"""
        # 新闻WebSocket连接后自动开始接收，无需发送特殊订阅消息
        def run(*args):
            try:
                self.logger.info("新闻订阅已激活，开始接收新闻数据")
                
                # 保持连接
                while self.news_running:
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"新闻订阅处理错误: {e}")
            finally:
                if self.news_running:
                    self.logger.info("关闭新闻连接...")
                    ws.close()
        
        # 启动线程
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

    def _connect_stock(self, params: Dict[str, str] = None) -> bool:
        """
        建立股票WebSocket连接
        
        参数:
            params: URL查询参数
            
        返回:
            bool: 是否成功启动连接
        """
        if self.stock_running:
            self.logger.warning("已经有一个活跃的股票连接，请先停止当前连接")
            return False
        
        self.stock_running = True
        
        # 生成URL
        url = f"{self.base_url}{self.PATH_STOCK}"
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}?{query_string}"
        
        self.logger.info(f"连接到股票WebSocket: {url}")
        
        # 创建股票WebSocket连接
        websocket.enableTrace(False)
        self.stock_ws = websocket.WebSocketApp(url,
                              on_open=self._on_stock_open,
                              on_message=self._on_stock_message,
                              on_error=self._on_stock_error,
                              on_close=self._on_stock_close)
        
        # 启动股票WebSocket客户端线程
        def _run_stock_websocket():
            self.stock_ws.run_forever()
        
        self.stock_websocket_thread = threading.Thread(target=_run_stock_websocket)
        self.stock_websocket_thread.daemon = True
        self.stock_websocket_thread.start()
        
        return True

    def _connect_news(self) -> bool:
        """
        建立新闻WebSocket连接
        
        返回:
            bool: 是否成功启动连接
        """
        if self.news_running:
            self.logger.warning("已经有一个活跃的新闻连接，请先停止当前连接")
            return False
        
        self.news_running = True
        
        # 生成URL
        url = f"{self.base_url}{self.PATH_NEWS}"
        
        self.logger.info(f"连接到新闻WebSocket: {url}")
        
        # 创建新闻WebSocket连接
        websocket.enableTrace(False)
        self.news_ws = websocket.WebSocketApp(url,
                              on_open=self._on_news_open,
                              on_message=self._on_news_message,
                              on_error=self._on_news_error,
                              on_close=self._on_news_close)
        
        # 启动新闻WebSocket客户端线程
        def _run_news_websocket():
            self.news_ws.run_forever()
        
        self.news_websocket_thread = threading.Thread(target=_run_news_websocket)
        self.news_websocket_thread.daemon = True
        self.news_websocket_thread.start()
        
        return True

    def subscribe(self, symbols: List[str], depth: int = 5, on_stock_callback: Optional[Callable] = None) -> bool:
        """
        订阅股票行情数据
        
        参数:
            symbols: 股票代码列表，例如 ["sh601008", "sz002640"]
            depth: 行情深度 1-5
            on_stock_callback: 股票数据回调函数，接收处理后的行情数据
            
        返回:
            bool: 是否成功启动订阅
        """
        self.symbols = symbols
        self.depth = max(1, min(5, depth))  # 确保深度在1-5之间
        self.on_stock_callback = on_stock_callback  # 设置回调函数
        
        # 生成参数
        params = {
            "symbols": ",".join(symbols),
            "depth": str(self.depth)
        }
        
        return self._connect_stock(params)

    def subscribe_news(self, on_news_callback: Optional[Callable] = None) -> bool:
        """
        订阅新闻数据
        
        参数:
            on_news_callback: 新闻数据回调函数，接收新闻数据
                              回调函数将接收到的数据格式: 
                              {
                                  "type": "news",
                                  "content": "新闻内容",
                                  "timestamp": "2024-01-15 14:30:25"
                              }
            
        返回:
            bool: 是否成功启动订阅
        """
        self.on_news_callback = on_news_callback  # 设置新闻回调函数
        
        return self._connect_news()
        
    def stop_stock(self):
        """停止股票WebSocket连接"""
        self.stock_running = False
        if self.stock_ws:
            self.stock_ws.close()
            self.logger.info("股票WebSocket连接已关闭")

    def stop_news(self):
        """停止新闻WebSocket连接"""
        self.news_running = False
        if self.news_ws:
            self.news_ws.close()
            self.logger.info("新闻WebSocket连接已关闭")

    def stop(self):
        """停止所有WebSocket连接"""
        self.stop_stock()
        self.stop_news()

    def is_stock_connected(self) -> bool:
        """检查股票WebSocket连接是否活跃"""
        return self.stock_running and self.stock_ws is not None

    def is_news_connected(self) -> bool:
        """检查新闻WebSocket连接是否活跃"""
        return self.news_running and self.news_ws is not None

    def is_connected(self) -> bool:
        """检查是否有任何WebSocket连接活跃"""
        return self.is_stock_connected() or self.is_news_connected()

    def __del__(self):
        """析构函数，确保资源释放"""
        self.stop() 