# notes/filters.py

from django_filters import rest_framework as filters
from .models import Contributor

class ContributorFilter(filters.FilterSet):
    department_name = filters.CharFilter(
        field_name='user__department__name', 
        lookup_expr='icontains' 
    )

    class Meta:
        model = Contributor
        fields = ['department_name'] 