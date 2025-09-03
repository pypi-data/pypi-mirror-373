from typing import Dict
from Osdental.Handlers.Instances import db_connection

class DBConnection:
    
    @staticmethod
    async def get_data_credentials(provider_name: str) -> Dict[str,str]:        
        return await db_connection.execute_query_return_data('EXEC CONNECT.sps_GetCDataCredentials @i_providerName = :provider_name', {'provider_name': provider_name}, fetchone=True)