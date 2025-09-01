import asyncio

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
import oracledb
from himile_util.himile_log import logger
# 配置日志

import os
os.environ["NLS_LANG"] = "AMERICAN_AMERICA.AL32UTF8"



@dataclass
class PoolConfig:
    """连接池配置类"""
    user: str
    password: str
    dsn: str
    oracle_dll: str
    min_pool_size: int = 5
    max_pool_size: int = 20
    increment: int = 5
    timeout: int = 30
    max_lifetime: int = 3600  # 连接最大生存时间（秒）
    retry_count: int = 3
    retry_delay: float = 1.0



class ConnectionError(Exception):
    """连接异常"""
    pass


class OracleAsyncPool:
    """Oracle异步连接池"""

    def __init__(self, config: PoolConfig):
        self.config = config
        self._pool: Optional[oracledb.ConnectionPool] = None
        self._pool_lock = asyncio.Lock()
        self._connection_semaphore = asyncio.Semaphore(config.max_pool_size)
        self._active_connections = set()

    async def initialize(self):
        """初始化连接池"""
        try:
            # 设置Oracle客户端模式
            oracledb.init_oracle_client(lib_dir=self.config.oracle_dll)

            # 创建连接池
            self._pool = oracledb.create_pool(
                user=self.config.user,
                password=self.config.password,
                dsn=self.config.dsn,
                min=self.config.min_pool_size,
                max=self.config.max_pool_size,
                increment=self.config.increment,
                timeout=self.config.timeout,
                max_lifetime_session=self.config.max_lifetime,
                retry_count=self.config.retry_count,
                retry_delay=self.config.retry_delay
            )

            logger.info(f"连接池初始化成功: min={self.config.min_pool_size}, max={self.config.max_pool_size}")

        except Exception as e:
            logger.error(f"连接池初始化失败: {e}")
            raise ConnectionError(f"Failed to initialize connection pool: {e}")

    async def close(self):
        """关闭连接池"""
        if self._pool:
            try:
                self._pool.close()
                logger.info("连接池已关闭")
            except Exception as e:
                logger.error(f"关闭连接池时出错: {e}")

    @asynccontextmanager
    async def get_connection(self):
        """获取连接的异步上下文管理器"""
        if not self._pool:
            await self.initialize()
            # raise ConnectionError("连接池未初始化")

        # 获取信号量，限制并发连接数
        await self._connection_semaphore.acquire()
        connection = None

        try:
            # 从连接池获取连接
            connection = await asyncio.get_event_loop().run_in_executor(
                None, self._pool.acquire
            )

            self._active_connections.add(connection)
            logger.debug(f"获取连接成功，当前活跃连接数: {len(self._active_connections)}")

            yield connection

        except Exception as e:
            logger.error(f"获取连接失败: {e}")
            raise ConnectionError(f"Failed to acquire connection: {e}")

        finally:
            if connection:
                try:
                    # 归还连接到池
                    await asyncio.get_event_loop().run_in_executor(
                        None, self._pool.release, connection
                    )

                    if connection in self._active_connections:
                        self._active_connections.remove(connection)

                    logger.debug(f"连接已归还，当前活跃连接数: {len(self._active_connections)}")

                except Exception as e:
                    logger.error(f"归还连接时出错: {e}")
                finally:
                    self._connection_semaphore.release()

    async def execute_query(
            self,
            sql: str,
            params: Optional[Union[Dict, Tuple, List]] = None,
            fetch_size: int = 1000
    ) ->    List[Dict[str, Any]]:
        """执行查询操作 (SELECT)"""
        async with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.arraysize = fetch_size

                if params:
                    await asyncio.get_event_loop().run_in_executor(
                        None, cursor.execute, sql, params
                    )
                else:
                    await asyncio.get_event_loop().run_in_executor(
                        None, cursor.execute, sql
                    )

                # 获取列名
                columns = [desc[0] for desc in cursor.description]

                # 获取所有结果
                rows = await asyncio.get_event_loop().run_in_executor(
                    None, cursor.fetchall
                )

                # 转换为字典列表
                result = [dict(zip(columns, row)) for row in rows]

                cursor.close()
                logger.debug(f"查询执行成功，返回 {len(result)} 条记录")

                return result

            except Exception as e:
                logger.error(f"查询执行失败: {sql}, 错误: {e}")
                raise

    async def execute_non_query(
            self,
            sql: str,
            params: Optional[Union[Dict, Tuple, List]] = None,
            auto_commit: bool = True
    ) -> int:
        """执行非查询操作 (INSERT, UPDATE, DELETE)"""
        async with self.get_connection() as conn:
            try:
                cursor = conn.cursor()

                if params:
                    await asyncio.get_event_loop().run_in_executor(
                        None, cursor.execute, sql, params
                    )
                else:
                    await asyncio.get_event_loop().run_in_executor(
                        None, cursor.execute, sql
                    )

                affected_rows = cursor.rowcount

                if auto_commit:
                    await asyncio.get_event_loop().run_in_executor(
                        None, conn.commit
                    )

                cursor.close()
                logger.debug(f"非查询操作执行成功，影响 {affected_rows} 行")

                return affected_rows

            except Exception as e:
                # 回滚事务
                await asyncio.get_event_loop().run_in_executor(
                    None, conn.rollback
                )
                logger.error(f"非查询操作执行失败: {sql}, 错误: {e}")
                raise

    async def execute_many(
            self,
            sql: str,
            params_list: List[Union[Dict, Tuple, List]],
            auto_commit: bool = True,
            batch_size: int = 1000
    ) -> int:
        """批量执行操作"""
        async with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                total_affected = 0

                # 分批处理
                for i in range(0, len(params_list), batch_size):
                    batch_params = params_list[i:i + batch_size]

                    await asyncio.get_event_loop().run_in_executor(
                        None, cursor.executemany, sql, batch_params
                    )

                    total_affected += cursor.rowcount

                if auto_commit:
                    await asyncio.get_event_loop().run_in_executor(
                        None, conn.commit
                    )

                cursor.close()
                logger.debug(f"批量操作执行成功，总计影响 {total_affected} 行")

                return total_affected

            except Exception as e:
                await asyncio.get_event_loop().run_in_executor(
                    None, conn.rollback
                )
                logger.error(f"批量操作执行失败: {sql}, 错误: {e}")
                raise

    async def insert(
            self,
            table: str,
            data: Dict[str, Any],
            return_id: bool = False,
            id_column: str = "ID"
    ) -> Optional[Any]:
        """插入数据"""
        columns = list(data.keys())
        placeholders = [f":{col}" for col in columns]

        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"

        # if return_id:
        #     sql += f" RETURNING {id_column} INTO :new_id"
        #     data['new_id'] = cursor.var(oracledb.NUMBER)

        await self.execute_non_query(sql, data)

        # if return_id:
        #     return data['new_id'].getvalue()[0]

        return None

    async def batch_insert(
            self,
            table: str,
            data_list: List[Dict[str, Any]],
            batch_size: int = 1000
    ) -> int:
        """批量插入数据"""
        if not data_list:
            return 0

        columns = list(data_list[0].keys())
        placeholders = [f":{col}" for col in columns]

        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"

        return await self.execute_many(sql, data_list, batch_size=batch_size)

    async def update(
            self,
            table: str,
            data: Dict[str, Any],
            where_clause: str,
            where_params: Optional[Dict[str, Any]] = None
    ) -> int:
        try:
            """更新数据"""
            set_clauses = [f"{col} = :{col}" for col in data.keys()]
            sql = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {where_clause}"

            # 合并参数
            params = data.copy()
            if where_params:
                params.update(where_params)

            return await self.execute_non_query(sql, params)
        except Exception as e:
            logger.critical(f"更新数据失败: {e}", exc_info=True)
            raise Exception(f"数据库操作失败: {e}")

    async def delete(
            self,
            table: str,
            where_clause: str,
            where_params: Optional[Dict[str, Any]] = None
    ) -> int:
        """删除数据"""
        sql = f"DELETE FROM {table} WHERE {where_clause}"
        return await self.execute_non_query(sql, where_params)

    async def select(
            self,
            table: str,
            columns: str = "*",
            where_clause: Optional[str] = None,
            where_params: Optional[Dict[str, Any]] = None,
            order_by: Optional[str] = None,
            limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """查询数据"""
        sql = f"SELECT {columns} FROM {table}"

        if where_clause:
            sql += f" WHERE {where_clause}"

        if order_by:
            sql += f" ORDER BY {order_by}"

        if limit:
            sql = f"SELECT * FROM ({sql}) WHERE ROWNUM <= {limit}"

        return await self.execute_query(sql, where_params)

    async def get_pool_status(self) -> Dict[str, Any]:
        """获取连接池状态"""
        if not self._pool:
            return {"status": "not_initialized"}

        return {
            "status": "active",
            "opened": self._pool.opened,
            "busy": self._pool.busy,
            "max_pool_size": self.config.max_pool_size,
            "min_pool_size": self.config.min_pool_size,
            "active_connections": len(self._active_connections)
        }
