from django_filters import rest_framework as filters
from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomFilterSet(filters.FilterSet):
    quantity = filters.NumberFilter(method='filter_quantity')
    direction = filters.CharFilter(method='filter_direction')
    # order = filters.OrderingFilter(fields=('name',))

    def filter_quantity(self, queryset, name, value):
        return queryset

    def filter_direction(self, queryset, name, value):
        if value.lower() == 'asc':
            return queryset.order_by(self.data.get('order', 'id'))
        elif value.lower() == 'desc':
            return queryset.order_by(f'-{self.data.get("order", "id")}')
        else:
            return queryset

    class Meta:
        fields = []


class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'quantity'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        return super().paginate_queryset(queryset, request, view)

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                return min(int(request.query_params[self.page_size_query_param]), self.max_page_size)
            except (KeyError, ValueError):
                pass
        return self.page_size

    def get_paginated_response(self, data):
        if self.page.paginator.count == 0:
            return Response({
                'count': 0,
                'next': None,
                'previous': None,
                'results': []
            })
        else:
            return super().get_paginated_response(data)


class GenericViewSetWithFilters(mixins.ListModelMixin, viewsets.GenericViewSet):
    filterset_class = None
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.filterset_class:
            filterset = self.filterset_class(self.request.GET, queryset=queryset)
            queryset = filterset.qs
        return queryset

    def get_filterset_class(self):
        if self.filterset_class:
            ordering_fields = self.get_ordering_fields(self.filterset_class.Meta.model)
            self.filterset_class.base_filters['order'].extra['choices'] = ordering_fields
        return self.filterset_class
