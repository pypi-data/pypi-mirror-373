from enum import StrEnum

class GraphqlOperation(StrEnum):
    QUERY = 'query'
    MUTATION = 'mutation'