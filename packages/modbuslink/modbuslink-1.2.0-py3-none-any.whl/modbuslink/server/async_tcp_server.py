"""
ModbusLink 异步TCP服务器实现
提供基于TCP的异步Modbus服务器功能。

ModbusLink Async TCP Server Implementation
Provides TCP-based async Modbus server functionality.
"""

import asyncio
import struct
from typing import Optional, Set
from .async_base_server import AsyncBaseModbusServer
from .data_store import ModbusDataStore
from ..common.exceptions import ConnectionError
from ..utils.logging import get_logger


class AsyncTcpModbusServer(AsyncBaseModbusServer):
    """
    异步TCP Modbus服务器
    实现基于TCP的异步Modbus服务器，支持多客户端并发连接。
    使用MBAP（Modbus Application Protocol）头进行通信。
    
    Async TCP Modbus Server
    Implements TCP-based async Modbus server with support for multiple concurrent client connections.
    Uses MBAP (Modbus Application Protocol) header for communication.
    """

    def __init__(self,
                 host: str = "localhost",
                 port: int = 502,
                 data_store: Optional[ModbusDataStore] = None,
                 slave_id: int = 1,
                 max_connections: int = 10):
        """
        初始化异步TCP Modbus服务器 | Initialize Async TCP Modbus Server
        
        Args:
            host: 服务器绑定地址 | Server bind address
            port: 服务器端口 | Server port
            data_store: 数据存储实例 | Data store instance
            slave_id: 从站地址 | Slave address
            max_connections: 最大并发连接数 | Maximum concurrent connections
        """
        super().__init__(data_store, slave_id)
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self._server: Optional[asyncio.Server] = None
        self._clients: Set[asyncio.StreamWriter] = set()
        self._transaction_id = 0
        self._logger = get_logger("server.tcp")

        self._logger.info(
            f"TCP服务器初始化 | TCP server initialized: {host}:{port}, 最大连接数 | Max connections: {max_connections}")

    async def start(self) -> None:
        """
        启动异步TCP服务器 | Start Async TCP Server
        
        Raises:
            ConnectionError: 当无法启动服务器时 | When server cannot be started
        """
        if self._running:
            self._logger.warning("服务器已在运行 | Server is already running")
            return

        try:
            self._server = await asyncio.start_server(
                self._handle_client,
                self.host,
                self.port,
                limit=self.max_connections
            )

            self._running = True
            self._logger.info(f"TCP服务器启动成功 | TCP server started successfully: {self.host}:{self.port}")

        except Exception as e:
            self._logger.error(f"启动TCP服务器失败 | Failed to start TCP server: {e}")
            raise ConnectionError(f"无法启动TCP服务器 | Cannot start TCP server: {e}")

    async def stop(self) -> None:
        """停止异步TCP服务器 | Stop Async TCP Server"""
        if not self._running:
            self._logger.warning("服务器未运行 | Server is not running")
            return

        self._running = False

        # 关闭所有客户端连接 | Close all client connections
        for writer in list(self._clients):
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                self._logger.warning(f"关闭客户端连接时出错 | Error closing client connection: {e}")

        self._clients.clear()

        # 关闭服务器 | Close server
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

        self._logger.info("TCP服务器已停止 | TCP server stopped")

    async def is_running(self) -> bool:
        """
        检查服务器运行状态 | Check Server Running Status
        
        Returns:
            如果服务器正在运行返回True，否则返回False | True if server is running, False otherwise
        """
        return self._running and self._server is not None

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """
        处理客户端连接 | Handle Client Connection
        
        Args:
            reader: 异步流读取器 | Async stream reader
            writer: 异步流写入器 | Async stream writer
        """
        client_addr = writer.get_extra_info('peername')
        self._logger.info(f"客户端连接 | Client connected: {client_addr}")

        self._clients.add(writer)

        try:
            while self._running:
                try:
                    # 读取MBAP头（7字节） | Read MBAP header (7 bytes)
                    mbap_header = await asyncio.wait_for(reader.read(7), timeout=30.0)

                    if not mbap_header:
                        self._logger.debug(f"客户端断开连接 | Client disconnected: {client_addr}")
                        break

                    if len(mbap_header) != 7:
                        self._logger.warning(f"MBAP头长度不正确 | Invalid MBAP header length: {len(mbap_header)}")
                        break

                    # 解析MBAP头 | Parse MBAP header
                    transaction_id, protocol_id, length, unit_id = struct.unpack(">HHHB", mbap_header)

                    if protocol_id != 0:
                        self._logger.warning(f"无效的协议标识符 | Invalid protocol identifier: {protocol_id}")
                        break

                    if length < 2 or length > 253:
                        self._logger.warning(f"无效的长度字段 | Invalid length field: {length}")
                        break

                    # 读取PDU数据 | Read PDU data
                    pdu_length = length - 1  # 减去单元标识符字节 | Subtract unit identifier byte
                    pdu_data = await asyncio.wait_for(reader.read(pdu_length), timeout=10.0)

                    if len(pdu_data) != pdu_length:
                        self._logger.warning(
                            f"PDU数据长度不匹配 | PDU data length mismatch: expected {pdu_length}, got {len(pdu_data)}")
                        break

                    self._logger.debug(
                        f"接收到请求 | Received request: 事务ID | Transaction ID {transaction_id}, 单元ID | Unit ID {unit_id}, PDU长度 | PDU Length {len(pdu_data)}")

                    # 处理请求 | Process request
                    response_pdu = self.process_request(unit_id, pdu_data)

                    if response_pdu:  # 只有非广播请求才响应 | Only respond to non-broadcast requests
                        # 构建响应MBAP头 | Build response MBAP header
                        response_length = len(response_pdu) + 1  # 加上单元标识符字节 | Add unit identifier byte
                        response_mbap = struct.pack(">HHHB", transaction_id, 0, response_length, unit_id)

                        # 发送响应 | Send response
                        writer.write(response_mbap + response_pdu)
                        await writer.drain()

                        self._logger.debug(
                            f"发送响应 | Sent response: 事务ID | Transaction ID {transaction_id}, 响应长度 | Response Length {len(response_pdu)}")

                except asyncio.TimeoutError:
                    self._logger.debug(f"客户端连接超时 | Client connection timeout: {client_addr}")
                    break
                except Exception as e:
                    self._logger.error(f"处理客户端请求时出错 | Error handling client request: {e}")
                    break

        except Exception as e:
            self._logger.error(f"客户端连接处理异常 | Client connection handling exception: {e}")

        finally:
            # 清理连接 | Cleanup connection
            self._clients.discard(writer)
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                self._logger.warning(f"关闭客户端连接时出错 | Error closing client connection: {e}")

            self._logger.info(f"客户端连接已关闭 | Client connection closed: {client_addr}")

    def get_connected_clients_count(self) -> int:
        """
        获取当前连接的客户端数量 | Get Current Connected Clients Count
        
        Returns:
            当前连接的客户端数量 | Current number of connected clients
        """
        return len(self._clients)

    async def serve_forever(self) -> None:
        """持续运行服务器直到被停止 | Run Server Forever Until Stopped"""
        if not self._running:
            await self.start()

        if self._server:
            try:
                await self._server.serve_forever()
            except asyncio.CancelledError:
                self._logger.info("服务器被取消 | Server cancelled")
            except Exception as e:
                self._logger.error(f"服务器运行异常 | Server running exception: {e}")
                raise
        else:
            raise ConnectionError("服务器未启动 | Server not started")
