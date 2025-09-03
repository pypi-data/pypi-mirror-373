from Osdental.Handlers.Instances import db_connection
from Osdental.Models.CDataIntegration import CdataIntegration, CdataInfo

class DBConnectionQuery:

    @staticmethod
    async def get_cdata_integration_data() -> CdataIntegration:
        data = await db_connection.execute_query_return_data('EXEC CONNECT.sps_GetCDataCredentials', fetchone=True)
        return CdataIntegration.from_db(data)

    @staticmethod
    async def get_cdata_integration_catalog_data() -> CdataInfo:
        data = await db_connection.execute_query_return_data('EXEC CATALOG.sps_GetCDataInfoFromCatalog')
        catalog = {}
        for el in data:
            catalog[el.get('name')] = el.get('value') 
        return CdataInfo.from_db(catalog)
