from .models import Visit
import django_filters


class VisitFilter(django_filters.FilterSet):
    target_name = django_filters.CharFilter(field_name='target_name', lookup_expr='icontains')
    keywords = django_filters.CharFilter(field_name='keywords', lookup_expr='icontains')

    class Meta:
        model = Visit
        fields = ['target_name', 'category', 'keywords']
