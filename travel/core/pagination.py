from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'current_page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'results': data,
        })
    
    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'required': ['count', 'current_page', 'page_size', 'results'],
            'properties': {
                'count': {
                    'type': 'integer',
                    'example': 123,
                },
                'page_size': {
                    'type': 'integer',
                    'example': 10,
                },
                'current_page': {
                    'type': 'integer',
                    'example': 1,
                },
                'results': schema,
            },
        }
