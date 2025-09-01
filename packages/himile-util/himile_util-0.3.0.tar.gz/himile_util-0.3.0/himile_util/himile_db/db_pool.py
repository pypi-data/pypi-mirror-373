"""
# Usage Example:
# 1. Define user configuration for the database.
# 2. Create a DBPool instance with the user configuration.
# 3. Perform database operations (insert, delete, update, select) using the DBPool instance.

# User configuration
user_config = {
    "user": "your_username",
    "password": "your_password",
    "host": "your_host",
    "database": "your_database",
    "maxconnections": 10,
    "mincached": 2,
    "maxcached": 5,
    "maxshared": 3,
}
# Create a database operation object
db = DBPool(**user_config)

try:
    # Insert operation
    insert_query = 'INSERT INTO z_dzw_test (id, name, age) VALUES (%s, %s, %s)'
    with db.update([insert_query], [('2', '小明', 22)]):
        pass
    
    # Delete operation
    delete_query = 'DELETE FROM your_table WHERE column1 = %s'
    with db.update([delete_query], [('value1',)]):
        pass

    # Update operation
    update_query = 'UPDATE your_table SET column2 = %s WHERE column1 = %s'
    with db.update([update_query], [('new_value', 'value1')]):
        pass

    # Select operation
    select_query = 'SELECT * FROM your_table WHERE column1 = %s'
    with db.select(select_query, ('value1',)) as results:
        print(results)

except Exception as e:
    print(f"Database operation failed: {e}")
    
异步方法的使用：
async def main():
    user_config = {
        "user": "sy_test",
        "password": "sy82278327",
        "host": "192.168.220.152",
        "database": "sy_test",
        "maxconnections": 10,
        "mincached": 2,
        "maxcached": 5,
        "maxshared": 3,
    }

    # 创建异步数据库操作对象
    db = AsyncDBPool(**user_config)
    await db.init_pool()

    try:
        # # 插入操作
        # insert_query = 'INSERT INTO z_dzw_test (id, name, age) VALUES (%s, %s, %s)'
        # async with await db.update([insert_query, insert_query], [('2', '小明', 22), ('3', '小红', 22)]):
        #     pass

        # # 删除操作
        # delete_query = 'DELETE FROM your_table WHERE column1 = %s'
        # async with await db.update([delete_query], [('value1',)]):
        #     pass

        # # 更新操作
        # update_query = 'UPDATE your_table SET column2 = %s WHERE column1 = %s'
        # async with await db.update([update_query], [('new_value', 'value1')]):
        #     pass

        # # 查询操作
        # select_query = 'SELECT * FROM z_dzw_test WHERE id = %s'
        # async with await db.select(select_query, (1,)) as results:
        #     print(results)

        insert_sql = 'INSERT INTO z_dzw_test (name, age) VALUES (%s, %s)'
        async with await db.insert_and_return_id(insert_sql, ('小明', 22)) as id:
            print(id)

    except Exception as e:
        print(f"Database operation failed: {e}")
    finally:
        await db.close_pool()

asyncio.run(main())

"""
import aiomysql
import mysql.connector

from typing import Optional, Any, Tuple, List
from dbutils.pooled_db import PooledDB


class DBPool:
    def __init__(self, user: str,
                 password: str,
                 host: str,
                 database: str,
                 maxconnections: int = 5,
                 mincached: int = 2,
                 maxcached: int = 5,
                 maxshared: int = 3,
                 connect_time: int = 60):
        """
        初始化数据库连接池。

        Args:
            user (str): 数据库用户名
            password (str): 数据库密码
            host (str): 数据库主机
            database (str): 数据库名称
            maxconnections (int, optional): 连接池允许的最大连接数。默认值为5。
            mincached (int, optional): 初始化时的最小空闲连接数。默认值为2。
            maxcached (int, optional): 连接池允许的最大空闲连接数。默认值为5。
            maxshared (int, optional): 连接池允许的最大共享连接数。默认值为3。
            connect_time(int, optional): 连接池允许最大超时时间，默认值为60.
        """
        self.pool = PooledDB(
            creator=mysql.connector,
            maxconnections=maxconnections,
            mincached=mincached,
            maxcached=maxcached,
            maxshared=maxshared,
            blocking=True,
            setsession=[],
            ping=0,
            user=user,
            password=password,
            host=host,
            database=database,
            connect_timeout=connect_time
        )

    class Connection:
        def __init__(self, pool):
            self.pool = pool
            self.conn = None
            self.cursor = None

        def __enter__(self):
            self.conn = self.pool.connection()
            self.cursor = self.conn.cursor(dictionary=True)
            return self.cursor

        def __exit__(self, exc_type, exc_value, traceback):
            if exc_type is not None:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.cursor.close()
            self.conn.close()

    class Operation:
        def __init__(self, db, querys: List[str], params: List[Optional[Tuple[Any, ...]]]):
            self.db = db
            self.querys = querys
            self.params = params

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    class InsertAndReturnID:
        def __init__(
            self,
            db,
            query: str,
            params: Optional[Tuple[Any, ...]]):
            self.db = db
            self.query = query
            self.params = params

        def __enter__(self):
            self.inserted_id = None
            with self.db.Connection(self.db.pool) as cursor:
                try:
                    cursor.execute(self.query, self.params)
                    self.inserted_id = cursor.lastrowid
                except Exception as e:
                    raise e
            return self.inserted_id

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    class Select:
        def __init__(
            self,
            db,
            select_sql: str,
            params: Optional[Tuple[Any, ...]]):
            self.db = db
            self.select_sql = select_sql
            self.params = params

        def __enter__(self):
            self.results = []
            with self.db.Connection(self.db.pool) as cursor:
                try:
                    cursor.execute(self.select_sql, self.params)
                    # if self.params:
                    #     cursor.execute(self.select_sql, self.params)
                    # else:
                    #     cursor.execute(self.select_sql)
                    self.results = cursor.fetchall()
                except Exception as e:
                    raise e
            return self.results

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    class UpdateALL(Operation):
        def __enter__(self):
            try:
                with self.db.Connection(self.db.pool) as cursor:
                    for query, param in zip(self.querys, self.params):
                        cursor.execute(query, param)
            except Exception as e:
                raise e

    def select(self, select_sql: str, params: Optional[Tuple[Any, ...]]) -> 'DBPool.Select':
        return self.Select(self, select_sql, params)

    def update(self, querys: List[str], params: List[Optional[Tuple[Any, ...]]]) \
        -> 'DBPool.UpdateALL':
        return self.UpdateALL(self, querys, params)

    def insert_and_return_id(self, query: str, params: Optional[Tuple[Any, ...]]) \
        -> 'DBPool.InsertAndReturnID':
        return self.InsertAndReturnID(self, query, params)


class AsyncDBPool:
    def __init__(self, user: str,
                 password: str,
                 host: str,
                 database: str,
                 maxconnections: int = 5,
                 mincached: int = 2,
                 maxcached: int = 5,
                 maxshared: int = 3):
        """
        初始化异步数据库连接池。
        """
        self.pool = None
        self.user = user
        self.password = password
        self.host = host
        self.database = database
        self.maxconnections = maxconnections
        self.mincached = mincached
        self.maxcached = maxcached
        self.maxshared = maxshared

    async def init_pool(self):
        self.pool = await aiomysql.create_pool(
            maxsize=self.maxconnections,
            minsize=self.mincached,
            host=self.host,
            user=self.user,
            password=self.password,
            db=self.database,
        )

    async def close_pool(self):
        self.pool.close()
        await self.pool.wait_closed()

    class Connection:
        def __init__(self, pool):
            self.pool = pool
            self.conn = None
            self.cursor = None

        async def __aenter__(self):
            self.conn = await self.pool.acquire()
            self.cursor = await self.conn.cursor(aiomysql.DictCursor)
            return self.cursor

        async def __aexit__(self, exc_type, exc_value, traceback):
            if exc_type is not None:
                await self.conn.rollback()
            else:
                await self.conn.commit()
            await self.cursor.close()
            self.pool.release(self.conn)

    class InsertAndReturnID:
        def __init__(self, db, query: str, params: Optional[List[Tuple[Any, ...]]] = None):
            self.db = db
            self.query = query
            self.params = params

        async def __aenter__(self):
            self.inserted_id = None
            async with self.db.Connection(self.db.pool) as cursor:
                try:
                    await cursor.execute(self.query, self.params)
                    self.inserted_id = cursor.lastrowid
                except Exception as e:
                    raise e
            return self.inserted_id

        async def __aexit__(self, exc_type, exc_value, traceback):
            pass

    class Select:
        def __init__(self, db, query: str, params: Optional[List[Tuple[Any, ...]]]):
            self.db = db
            self.query = query
            self.params = params

        async def __aenter__(self):
            self.results = []
            async with self.db.Connection(self.db.pool) as cursor:
                try:
                    await cursor.execute(self.query, self.params)
                    self.results = await cursor.fetchall()
                except Exception as e:
                    raise e
            return self.results

        async def __aexit__(self, exc_type, exc_value, traceback):
            pass

    class Update:
        def __init__(self, db, queries: List[str], params: Optional[List[Tuple[Any, ...]]]):
            self.db = db
            self.queries = queries
            self.params = params

        async def __aenter__(self):
            async with self.db.Connection(self.db.pool) as cursor:
                try:
                    for query, param in zip(self.queries, self.params):
                        await cursor.execute(query, param)
                except Exception as e:
                    raise e
        
        async def __aexit__(self, exc_type, exc_value, traceback):
            pass
    
    async def insert_and_return_id(self, query: str, params: Optional[Tuple[Any, ...]]
                                   ) -> 'AsyncDBPool.InsertAndReturnID':
        await self._ensure_connected()
        return self.InsertAndReturnID(self, query, params)

    async def select(self, query: str, params: Optional[Tuple[Any, ...]]):
        await self._ensure_connected()
        return self.Select(self, query, params)

    async def update(self, queries: List[str], params: Optional[List[Tuple[Any, ...]]]):  
        await self._ensure_connected()
        return self.Update(self, queries, params)
    
    async def _ensure_connected(self):
        if self.pool is None:
            await self.init_pool()

if __name__ == '__main__':
    # user_config = {
    # "user": "sy_test",
    # "password": "sy82278327",
    # "host": "192.168.220.152",
    # "database": "sy_test",
    # "maxconnections": 10,
    # "mincached": 2,
    # "maxcached": 5,
    # "maxshared": 3,
    # }
    # # Create a database operation object
    # db = DBPool(**user_config)

    # try:
    #     # # Insert operation
    #     # insert_query = 'INSERT INTO z_dzw_test (id, name, age) VALUES (%s, %s, %s)'
    #     # with db.create([insert_query, insert_query], [('2', '小明', 22), ('3', '小红', 22)]):
    #     #     pass

    #     # # Delete operation
    #     # delete_query = 'DELETE FROM z_dzw_test WHERE id = %s'
    #     # with db.delete([delete_query, delete_query], [(3,), (2,)]):
    #     #     pass

    #     # Update operation
    #     update_query = 'UPDATE z_dzw_test SET name = %s WHERE id = %s'
    #     with db.update([update_query], [('new_value', '2')]):
    #         pass

    #     # # Select operation
    #     # select_query = 'SELECT * FROM your_table WHERE column1 = %s'
    #     # with db.select(select_query, ('value1',)) as results:
    #     #     print(results)

    # except Exception as e:
    #     print(f"Database operation failed: {e}")
    import asyncio

    async def main():
        user_config = {
            "user": "sy_test",
            "password": "sy82278327",
            "host": "192.168.220.152",
            "database": "sy_test",
            "maxconnections": 10,
            "mincached": 2,
            "maxcached": 5,
            "maxshared": 3,
        }

        # 创建异步数据库操作对象
        db = AsyncDBPool(**user_config)
        await db.init_pool()

        try:
            # 插入操作
            insert_query = 'INSERT INTO z_dzw_test (id, name, age) VALUES (%s, %s, %s)'
            async with await db.update([insert_query, insert_query], [('1', '小明', 22), ('2', '小红', 22)]):
                pass

            # # 删除操作
            # delete_query = 'DELETE FROM your_table WHERE column1 = %s'
            # async with await db.update([delete_query], [('value1',)]):
            #     pass

            # # 更新操作
            # update_query = 'UPDATE z_dzw_test SET name = %s WHERE id = %s'
            # async with await db.update([update_query], [('mm', '2')]):
            #     pass

            # # 查询操作
            # select_query = 'SELECT * FROM z_dzw_test WHERE id = %s'
            # async with await db.select(select_query, (1,)) as results:
            #     print(results)

            # insert_sql = 'INSERT INTO z_dzw_test (name, age) VALUES (%s, %s)'
            # async with await db.insert_and_return_id(insert_sql, ('小明', 22)) as id:
            #     print(id)

        except Exception as e:
            print(f"Database operation failed: {e}")
        finally:
            await db.close_pool()

    asyncio.run(main())


    pass
