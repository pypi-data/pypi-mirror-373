import os
import sys
import subprocess
import platform
import click
from Osdental.Shared.Logger import logger
from Osdental.Shared.Enums.Message import Message
from Osdental.Shared.Utils.CaseConverter import CaseConverter

SRC_PATH = 'src'
APP_PATH = os.path.join(SRC_PATH, 'Application')
DOMAIN_PATH = os.path.join(SRC_PATH, 'Domain')
INFRA_PATH = os.path.join(SRC_PATH, 'Infrastructure')
GRAPHQL_PATH = os.path.join(INFRA_PATH, 'Graphql')
GRPC_PATH = os.path.join(INFRA_PATH, 'Grpc')
RESOLVERS_PATH = os.path.join(GRAPHQL_PATH, 'Resolvers')
SCHEMAS_PATH = os.path.join(GRAPHQL_PATH, 'Schemas')

@click.group()
def cli():
    """Comandos personalizados para gestionar el proyecto."""
    pass

@cli.command()
def clean():
    """Borrar todos los __pycache__."""
    if platform.system() == 'Windows':
        subprocess.run('for /d /r . %d in (__pycache__) do @if exist "%d" rd /s/q "%d"', shell=True)
    else:
        subprocess.run("find . -name '__pycache__' -type d -exec rm -rf {} +", shell=True)

    logger.info(Message.PYCACHE_CLEANUP_SUCCESS_MSG)


@cli.command(name='start-app')
@click.argument('app')
def start_app(app: str):
    """Crear un servicio con estructura hexagonal y CRUD básico."""
    app = CaseConverter.snake_to_pascal(app)
    app_upper = app.upper()
    if '-' in app:
        part_one, part_two = tuple(app.split('-'))
        app = part_one + part_two
        app_upper = f'{part_one}_{part_two}'.upper()

    name_method = CaseConverter.case_to_snake(app)
    data = 'data: Dict[str,str]'
    token = 'token: AuthToken'
    api_type_response = 'Response!'
    
    directories = [
        os.path.join(SRC_PATH),
        os.path.join(APP_PATH, 'UseCases'),
        os.path.join(APP_PATH, 'Interfaces'),
        os.path.join(DOMAIN_PATH, 'Interfaces'),
        os.path.join(DOMAIN_PATH, 'Models'),
        os.path.join(RESOLVERS_PATH),
        os.path.join(SCHEMAS_PATH),
        os.path.join(SCHEMAS_PATH, app),
        os.path.join(GRPC_PATH, 'Proto'),
        os.path.join(GRPC_PATH, 'Generated'),
        os.path.join(GRPC_PATH, 'Server'),
        os.path.join(GRPC_PATH, 'Client'),
        os.path.join(INFRA_PATH, 'Repositories', app)
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    # Contenidos CRUD
    use_case_interface_name = f'{app}UseCaseInterface'
    use_case_interface_content = f'''
from abc import ABC, abstractmethod
from typing import Dict
from Osdental.Models.Token import AuthToken

class {use_case_interface_name}(ABC):

    @abstractmethod
    async def get_all_{name_method}(self, {token}, {data}) -> str: ...

    @abstractmethod
    async def get_{name_method}_by_id(self, {token}, {data}) -> str: ...

    @abstractmethod
    async def create_{name_method}(self, {token}, {data}) -> str: ...

    @abstractmethod
    async def update_{name_method}(self, {token}, {data}) -> str: ...

    @abstractmethod
    async def delete_{name_method}(self, {token}, {data}) -> str: ...
    '''


    use_case_content = f'''
from typing import Dict
from Osdental.Decorators.DecryptedData import process_encrypted_data
from Osdental.Models.Token import AuthToken
from ..Interfaces.{use_case_interface_name} import {use_case_interface_name}
from src.Domain.Interfaces.{app}RepositoryInterface import {app}RepositoryInterface

class {app}UseCase({use_case_interface_name}):

    def __init__(self, repository: {app}RepositoryInterface):
        self.repository = repository
        
    @process_encrypted_data()
    async def get_all_{name_method}(self, {token}, {data}) -> str: pass

    @process_encrypted_data()        
    async def get_{name_method}_by_id(self, {token}, {data}) -> str: pass
        
    @process_encrypted_data()    
    async def create_{name_method}(self, {token}, {data}) -> str: pass

    @process_encrypted_data()
    async def update_{name_method}(self, {token}, {data}) -> str: pass

    @process_encrypted_data()
    async def delete_{name_method}(self, {token}, {data}) -> str: pass
    '''


    repository_interface_name = f'{app}RepositoryInterface'
    repository_interface_content = f'''
from abc import ABC, abstractmethod
from sqlalchemy import text, RowMapping
from typing import List

class {repository_interface_name}(ABC):

    @abstractmethod
    async def get_all_{name_method}(self, {data}) -> List[RowMapping]: ...

    @abstractmethod
    async def get_{name_method}_by_id(self, id: str) -> RowMapping: ...

    @abstractmethod
    async def create_{name_method}(self, {data}) -> str: ...

    @abstractmethod
    async def update_{name_method}(self, id: str, {data}) -> str: ...
    
    @abstractmethod
    async def delete_{name_method}(self, id: str) -> str: ...
    '''


    repository_content = f'''
from typing import List
from sqlalchemy import text, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from src.Domain.Interfaces.{repository_interface_name} import {repository_interface_name}

class {app}Repository({repository_interface_name}):
    
    def __init__(self, session: AsyncSession):
        self.session = session    

    async def get_all_{name_method}(self, {data}) -> List[RowMapping]: pass
    
    async def get_{name_method}_by_id(self, id: str) -> RowMapping: pass

    async def create_{name_method}(self, {data}) -> str: pass
            
    async def update_{name_method}(self, id: str, {data}) -> str: pass
        
    async def delete_{name_method}(self, id: str) -> str: pass
    '''


    query_graphql = f'''type Query {{
    getAll{app}(data: String!): {api_type_response}
    get{app}ById(data: String!): {api_type_response}
}}
    '''

    mutation_graphql = f'''type Mutation {{
    create{app}(data: String!): {api_type_response}
    update{app}(data: String!): {api_type_response}
    delete{app}(data: String!): {api_type_response}
}}
    '''

    resolver_content_init = f"""
from .{app}Resolver import {app}Resolver

{name_method}_query_resolvers = {{
    'getAll{app}': {app}Resolver.resolve_get_all_{name_method},
    'get{app}ById': {app}Resolver.resolve_get_{name_method}_by_id
}}

{name_method}_mutation_resolvers = {{
    'create{app}': {app}Resolver.resolve_create_{name_method},
    'update{app}': {app}Resolver.resolve_update_{name_method},
    'delete{app}': {app}Resolver.resolve_delete_{name_method}
}}
    """

    resolver_content = f'''
from Osdental.Decorators.AuditLog import handle_audit_and_exception
from src.Application.UseCases.{app}UseCase import {app}UseCase
from src.Infrastructure.Repositories.{app}.{app}Repository import {app}Repository

use_case = {app}UseCase({app}Repository)

class {app}Resolver:
        
    @staticmethod
    @handle_audit_and_exception()
    async def resolve_get_all_{name_method}(_, info, data):
        return await use_case.get_all_{name_method}(info=info, aes_data=data)

    @staticmethod
    @handle_audit_and_exception()
    async def resolve_get_{name_method}_by_id(_, info, data):
        return await use_case.get_{name_method}_by_id(info=info, aes_data=data)

    @staticmethod
    @handle_audit_and_exception()
    async def resolve_create_{name_method}(_, info, data):
        return await use_case.create_{name_method}(info=info, aes_data=data)

    @staticmethod
    @handle_audit_and_exception()
    async def resolve_update_{name_method}(_, info, data):
        return await use_case.update_{name_method}(info=info, aes_data=data)
    
    @staticmethod
    @handle_audit_and_exception()
    async def resolve_delete_{name_method}(_, info, data):
        return await use_case.delete_{name_method}(info=info, aes_data=data)
    '''

    graphql_content_init = f'''
from ariadne import gql
from ariadne import QueryType, MutationType
from ariadne import make_executable_schema
from pathlib import Path
from ..Graphql.Resolvers.{app} import {name_method}_query_resolvers, {name_method}_mutation_resolvers

def load_schemas():
    schema_dir = Path(__file__).parent / 'Schemas'
    schemas = [schema.read_text() for schema in schema_dir.rglob('*.graphql')]
    return gql('\\n'.join(schemas))

type_defs = load_schemas()

query_resolvers = {{
    **{name_method}_query_resolvers,
}}

mutation_resolvers = {{
    **{name_method}_mutation_resolvers,
}}

query = QueryType()
mutation = MutationType()

for field, resolver in query_resolvers.items():
    query.set_field(field, resolver)

for field, resolver in mutation_resolvers.items():
    mutation.set_field(field, resolver)

# Executable Schema
schema = make_executable_schema(type_defs, query, mutation)
    '''


    response_content = '''
type Response {
    status: String
    message: String
    data: String
}
    '''

    init_file = '__init__.py'
    
    repository_init_content = f"""
from enum import StrEnum 

class {app}Query(StrEnum):
    GET_ALL_{app_upper} = ''' EXEC '''

    GET_{app_upper}_BY_ID = ''' EXEC '''

    CREATE_{app_upper} = ''' EXEC ''' 

    UPDATE_{app_upper} = ''' EXEC ''' 

    DELETE_{app_upper} = ''' EXEC ''' 
    """

    proto_app_content = f'''
syntax = "proto3";

package {app.lower()};

import "Common.proto";

// gRPC Service
    '''

    common_proto = '''
syntax = "proto3";

package common;

message Request { bytes data = 1; }
message Response { string status=1; string message=2; bytes data=3; }https://chatgpt.com/c/68a35293-1a34-832b-9bec-09e0513a52e3
message Empty {}
'''
    server = '''
from grpc.experimental import aio


async def serve():
    server = aio.server()

    # Register each service
    # Code Here ...

    # Single port exposed
    server.add_insecure_port("[::]:50051")

    await server.start()
    await server.wait_for_termination()
'''

    grpc_client = f'''
import grpc
from Osdental.Models.Response import Response

class {app}Client:

    def __init__(self, host="localhost", port=50051):
        # Connecting to the gRPC server
        self.channel = grpc.aio.insecure_channel(f"{{host}}:{{port}}")
        self.stub = 'Connects your client to the gRPC server via the channel and gives you access to all the service methods.'

    # Implement your RPC methods to consume

'''
    files = {
        os.path.join(APP_PATH, 'UseCases', f'{app}UseCase.py'): use_case_content,
        os.path.join(APP_PATH, 'Interfaces', f'{app}UseCaseInterface.py'): use_case_interface_content,
        os.path.join(DOMAIN_PATH, 'Interfaces', f'{app}RepositoryInterface.py'): repository_interface_content,
        os.path.join(RESOLVERS_PATH, app, init_file): resolver_content_init,
        os.path.join(RESOLVERS_PATH, app, f'{app}Resolver.py'): resolver_content,
        os.path.join(GRAPHQL_PATH, init_file): graphql_content_init, 
        os.path.join(SCHEMAS_PATH, app, 'Query.graphql'): query_graphql,
        os.path.join(SCHEMAS_PATH, app, 'Mutation.graphql'): mutation_graphql,
        os.path.join(SCHEMAS_PATH, 'Response.graphql'): response_content,
        os.path.join(INFRA_PATH, 'Repositories', app, init_file): repository_init_content,
        os.path.join(INFRA_PATH, 'Repositories', app, f'{app}Repository.py'): repository_content,
        os.path.join(GRPC_PATH, 'Proto', 'Common.proto'): common_proto,
        os.path.join(GRPC_PATH, 'Proto', f'{app}Service.proto'): proto_app_content,
        os.path.join(GRPC_PATH, 'Server', 'Server.py'): server,
        os.path.join(GRPC_PATH, 'Client', f'{app}Client.py'): grpc_client
    }
    for file_path in files:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    for file_path, content in files.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(content)

    logger.info(Message.HEXAGONAL_SERVICE_CREATED_MSG)

@cli.command()
@click.argument('port')
def start(port: int):
    """Start the FastAPI server.."""
    try:
        subprocess.run(['uvicorn', 'app:app', '--port', str(port), '--reload'], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f'{Message.SERVER_NETWORK_ACCESS_ERROR_MSG}: {e}')


@cli.command()
@click.argument('port')
def serve(port: int):
    """Set up the FastAPI server accessible from any machine."""
    try:
        subprocess.run(['uvicorn', 'app:app', '--host', '0.0.0.0', '--port', str(port), '--reload'], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f'{Message.SERVER_NETWORK_ACCESS_ERROR_MSG}: {e}')


@cli.command()
@click.argument('redis_env')
async def clean_redis(redis_env: str):
    try:
        from Osdental.RedisCache.Redis import RedisCacheAsync
        redis_url = os.getenv(redis_env)
        if not redis_url:
            logger.warning(f'Environment variable not found: {redis_env}')
            return
        
        redis = RedisCacheAsync(redis_url=redis_url)
        await redis.flush()
        logger.info(Message.REDIS_CLEANUP_SUCCESS_MSG)
    except Exception as e:
        logger.error(f'{Message.REDIS_CLEANUP_ERROR_MSG}: {e}')


@cli.command()
@click.argument('name')
def proto_files(name: str):
    proto_dir = r'.\src\Infrastructure\Grpc\Proto'
    gen_dir = r'.\src\Infrastructure\Grpc\Generated'

    if platform.system() == 'Windows':
        # Ejecuta el comando de grpc_tools.protoc
        cmd = f'''python -m grpc_tools.protoc -I={proto_dir} \
        --python_out={gen_dir} \
        --grpc_python_out={gen_dir} \
        {proto_dir}\\{name}Service.proto \
        {proto_dir}\\Common.proto'''
    else:
        # Linux / macOS
        cmd = f'''python -m grpc_tools.protoc -I={proto_dir} \
        --python_out={gen_dir} \
        --grpc_python_out={gen_dir} \
        {proto_dir}/{name}Service.proto \
        {proto_dir}/Common.proto'''

    subprocess.run(cmd, shell=True)
    logger.info(Message.PROTO_FILES_GENERATED_MSG)


@click.command()
@click.option("--host", default="0.0.0.0", help='Host where to set up the server')
@click.option("--port", default=5000, help='Server port')
@click.option("--workers", default=4, help='Number of workers')
def run_server(host, port, workers):
    """Launch the application with uvicorn on Windows or gunicorn on other systems"""
    if sys.platform.startswith("win"):
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app:app",
            "--host", host,
            "--port", str(port),
            "--workers", str(workers)
        ]
    else:
        cmd = [
            sys.executable, "-m", "gunicorn",
            "app:app",
            "-k", "uvicorn.workers.UvicornWorker",
            "--bind", f"{host}:{port}",
            "--workers", str(workers)
        ]
    
    logger.info(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)
    
if __name__ == "__main__":
    cli()
