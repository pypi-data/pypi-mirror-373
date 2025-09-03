from Osdental.Handlers.Instances import db_security, microservice_name
from Osdental.Shared.Enums.Code import Code

class RedisTable:

    @staticmethod
    async def create_redis_key(user_id: str, method_controller: str, key: str) -> None:
        query = """ 
        EXEC SECURITY.spi_InsertRedisTable
        @i_idUser = :user_id,
        @i_microService = :microservice,
        @i_methodController = :method_controller,
        @i_keyName = :key_name
        """
        params = {
            'user_id': user_id,
            'microservice': microservice_name,
            'method_controller': method_controller,
            'key_name': key
        }
        await db_security.execute_query(query, params, Code.PROCESS_SUCCESS_CODE)

    @staticmethod
    async def delete_redis_key(key: str) -> None:
        query = """ 
        EXEC SECURITY.spd_DeleteRedisTable
        @i_keyName = :key_name
        """
        params = {
            'key_name': key
        }
        await db_security.execute_query(query, params, Code.PROCESS_SUCCESS_CODE)