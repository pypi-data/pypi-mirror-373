from contextlib import asynccontextmanager
from typing import Dict, List, Tuple, AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from Osdental.Exception.ControlledException import DatabaseException
from Osdental.Shared.Utils.DataUtils import DataUtils
from Osdental.Shared.Enums.Code import Code
from Osdental.Shared.Enums.Message import Message

class Connection:

    _instances: Dict[str, 'Connection'] = {}

    def __new__(cls, db_url: str):
        if db_url not in cls._instances:
            cls._instances[db_url] = super(Connection, cls).__new__(cls)
        return cls._instances[db_url]

    def __init__(self, db_url: str):
        if not hasattr(self, 'initialized'):
            self.engine = create_async_engine(
                db_url,
                pool_size=20,          
                max_overflow=40,       
                pool_timeout=30,       
                pool_recycle=3600     
            )
            self.session_factory = sessionmaker(
                bind=self.engine, 
                class_=AsyncSession, 
                expire_on_commit=False
            )
            self.initialized = True

    def get_session(self) -> AsyncSession:
        return self.session_factory()


    async def execute_query_return_first_value(self, query:str, params:Dict[str,str] = None) -> str:
        try:
            async with self.get_session() as session:
                async with session.begin():
                    result = await session.execute(text(query), params)
                    value = result.scalar()
                    return DataUtils.normalize_uuid_value(value)
        except DatabaseException:
            raise
        except Exception as e:
            raise DatabaseException(message=Message.DATABASE_EXECUTION_ERROR_MSG, error=str(e))


    async def execute_query_return_data(self, query:str, params:Dict[str,str] = None, fetchone=False) -> List[Dict[str,str]] | Dict[str,str]:
        try:
            async with self.get_session() as session:
                async with session.begin():
                    result = await session.execute(text(query), params)
                    keys = result.keys()
                    if fetchone:
                        row = result.fetchone()
                        return DataUtils.normalize_uuids_dict(dict(zip(keys, row))) if row else {}
                    
                    rows = result.fetchall()
                    return [DataUtils.normalize_uuids_dict(dict(zip(keys, row))) for row in rows] if rows else []
        except DatabaseException:
            raise
        except Exception as e:
            raise DatabaseException(message=Message.DATABASE_EXECUTION_ERROR_MSG, error=str(e))


    async def execute_query_return_message(self, query:str, params:Dict[str,str] = None, code:str | Tuple[str,str] = Code.PROCESS_SUCCESS_CODE) -> str:
        try:
            async with self.get_session() as session:
                async with session.begin():
                    result = await session.execute(text(query), params)
                    row = result.fetchone() 
                    if not row:
                        raise DatabaseException(message=Message.NO_RESULTS_FOUND_MSG, error=Message.NO_RESULTS_FOUND_MSG)
                    
                    status_code = (code,) if isinstance(code, str) else code
                    if row.STATUS_CODE not in status_code:
                        raise DatabaseException(message=row.STATUS_MESSAGE, error=row.STATUS_MESSAGE, status_code=row.STATUS_CODE)

                    return row.STATUS_MESSAGE
        except DatabaseException:
            raise
        except Exception as e:
            raise DatabaseException(message=Message.DATABASE_EXECUTION_ERROR_MSG, error=str(e))


    async def execute_query(self, query:str, params:Dict[str,str] = None, code:str | Tuple[str,str] = None) -> None | Dict[str,str]:
        try:
            async with self.get_session() as session:
                async with session.begin():
                    result = await session.execute(text(query), params)
                    if code:
                        row = result.fetchone()
                        if not row:
                            raise DatabaseException(message=Message.NO_RESULTS_FOUND_MSG, error=Message.NO_RESULTS_FOUND_MSG)
                        
                        status_code = (code,) if isinstance(code, str) else code
                        if row.STATUS_CODE not in status_code:
                            raise DatabaseException(message=row.STATUS_MESSAGE, error=row.STATUS_MESSAGE, status_code=row.STATUS_CODE)

                        return DataUtils.normalize_uuids_dict(dict(zip(result.keys(), row)))
                    
                    return None
        except DatabaseException:
            raise
        except Exception as e:
            raise DatabaseException(message=Message.DATABASE_EXECUTION_ERROR_MSG, error=str(e))
            
    
    async def execute_transaction_queries(self, data: List[Dict[str, str]], return_data: bool = False) -> Dict[str, str] | str | None:
        try:
            result_data = None
            async with self.get_session() as session:
                async with session.begin():
                    for item in data:
                        query = item.get('query')
                        params = item.get('params', {})
                        codes = item.get('code', Code.PROCESS_SUCCESS_CODE)

                        if not query:
                            raise DatabaseException(
                                message=Message.QUERY_NOT_PROVIDED_MSG,
                                error=Message.QUERY_NOT_PROVIDED_MSG
                            )

                        result = await session.execute(text(query), params)
                        row = result.fetchone()
                        keys = result.keys()
                        result.close()

                        if not row:
                            raise DatabaseException(
                                message=Message.NO_RESULTS_FOUND_MSG,
                                error=Message.NO_RESULTS_FOUND_MSG
                            )

                        accepted_codes = (codes,) if isinstance(codes, str) else codes
                        if row.STATUS_CODE not in accepted_codes:
                            raise DatabaseException(
                                message=row.STATUS_MESSAGE,
                                error=row.STATUS_MESSAGE,
                                status_code=row.STATUS_CODE
                            )

                        if return_data:
                            result_data = DataUtils.normalize_uuids_dict(dict(zip(keys, row)))
                        else:
                            result_data = row.STATUS_MESSAGE

            return result_data
        except DatabaseException:
            raise
        except Exception as e:
            raise DatabaseException(message=Message.DATABASE_EXECUTION_ERROR_MSG, error=str(e))

    @asynccontextmanager
    async def get_transaction_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Returns a session with active transaction for scope controlled by the caller."""
        async with self.get_session() as session:
            async with session.begin():
                try:
                    yield session
                except Exception:
                    await session.rollback()
                    raise
                else:
                    await session.commit()

    async def execute_with_session(self, session: AsyncSession, query: str, params: Dict[str, str] = None):
        """Executes a query using an already open external session (transaction controlled outside)."""
        result = await session.execute(text(query), params)
        return result
    
    async def close_engine(self) -> None:
        """Dispose of the engine and remove instance."""
        if self.engine:
            await self.engine.dispose() 
        
        if self.db_url in self._instances:
            del self._instances[self.db_url]