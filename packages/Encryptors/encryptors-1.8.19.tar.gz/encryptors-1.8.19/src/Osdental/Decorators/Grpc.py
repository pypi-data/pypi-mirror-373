from functools import wraps
from starlette.datastructures import Headers
from Osdental.Models.Response import Response
from Osdental.Models.FakeInfo import FakeInfo
from Osdental.Shared.Enums.GrahpqlOperation import GraphqlOperation
from Osdental.Shared.Enums.Constant import Constant

# Client
def with_grpc_metadata(func):
    """
    Decorator to transform data to bytes and build metadata for gRPC.
    """
    @wraps(func)
    async def wrapper(self, data, headers: Headers, *args, **kwargs):
        # Transform data to bytes if it is str
        if isinstance(data, str):
            data_bytes = data.encode(Constant.DEFAULT_ENCODING)
        else:
            data_bytes = data

        # Build metadata from headers
        user_token = headers.get('authorization', '')
        token_value = user_token.split(' ')[1] if user_token.startswith('Bearer ') else user_token
        metadata = [
            ('authorization', token_value),
            ('dynamicclientid', headers.get('dynamicClientId', '')),
        ]

        # Add extra metadata if it comes in kwargs
        extra_metadata = kwargs.pop('extra_metadata', None)
        if extra_metadata:
            if isinstance(extra_metadata, dict):
                metadata.extend(extra_metadata.items())
            else:
                metadata.extend(extra_metadata)

        # Call the actual gRPC method passing request and metadata
        res = await func(self, data_bytes, metadata, *args, **kwargs)

        # Return a uniform Response
        return Response(status=res.status, message=res.message, data=res.data)

    return wrapper

# Server
def __build_grpc_context(request, context, operation_name=GraphqlOperation.QUERY) -> tuple[str, FakeInfo]:
    if isinstance(request.data, bytes):
        aes_data_str = request.data.decode(Constant.DEFAULT_ENCODING)
    else:
        aes_data_str = str(request.data)

    metadata_dict = dict(context.invocation_metadata())
    user_token = metadata_dict.get('authorization')

    context_dict = {
        'user_token': user_token,
        'headers': metadata_dict,
    }

    info = FakeInfo(context_dict, operation_name)
    return aes_data_str, info


def with_grpc_info(operation_name: GraphqlOperation = GraphqlOperation.QUERY):
    """
    Decorator to wrap gRPC methods and build the FakeInfo.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(servicer, request, context):
            aes_data_str, info = __build_grpc_context(request, context, operation_name)
            return await func(servicer, aes_data_str, info)
        return wrapper
    return decorator