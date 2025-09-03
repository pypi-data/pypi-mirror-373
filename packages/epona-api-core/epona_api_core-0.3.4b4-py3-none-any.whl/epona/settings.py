import os

import asyncpg

db_settings = {
    "db_host": os.getenv("DB_HOST", "localhost"),
    "db_port": os.getenv("DB_PORT", "5433"),
    "db_user": os.getenv("DB_USER", "postgres"),
    "db_pass": os.getenv("DB_PASSWORD", "postgres"),
    "db_name": os.getenv("DB_NAME", "core"),
}
TOKEN_DURATION = int(
    60 * 24 * float(os.getenv("TOKEN_DURATION", 0.5))
)  # days -> minutes


class Database:
    def __init__(self):
        self.host = db_settings["db_host"]
        self.port = db_settings["db_port"]
        self.user = db_settings["db_user"]
        self.password = db_settings["db_pass"]
        self.database = db_settings["db_name"]
        self._cursor = None

        self._connection_pool = None
        self.conn = None

    async def close(self) -> None:
        await self._connection_pool.close()

    async def connect(self) -> None:
        if not self._connection_pool:
            try:
                self._connection_pool = await asyncpg.create_pool(
                    min_size=1,
                    max_size=10,
                    command_timeout=300,
                    host=db_settings["db_host"],
                    port=db_settings["db_port"],
                    user=db_settings["db_user"],
                    password=db_settings["db_pass"],
                    database=db_settings["db_name"],
                )
            except Exception as ex:
                raise ex

    async def fetch_rows(self, query: str, params=None) -> asyncpg.Record:
        if not self._connection_pool:
            await self.connect()
        try:
            self.conn = await self._connection_pool.acquire()
            if params:
                # query, params = pyformat2psql(query, params)
                result = await self.conn.fetch(query, *params)
            else:
                result = await self.conn.fetch(query)
            return result
        except asyncpg.exceptions.PostgresError as err:
            raise err
        except Exception as ex:
            raise ex
        finally:
            await self._connection_pool.release(self.conn)

    async def execute(self, query: str, params=None) -> None:
        if not self._connection_pool:
            await self.connect()
        try:
            self.conn = await self._connection_pool.acquire()
            if params:
                # query, params = pyformat2psql(query, params)
                result = await self.conn.execute(query, *params)
            else:
                result = await self.conn.execute(query)
            return result
        except asyncpg.exceptions.PostgresError as err:
            raise err
        except Exception as ex:
            raise ex
        finally:
            await self._connection_pool.release(self.conn)


conn = Database()
