from django_filters import rest_framework as filters
from notes.models import Note

class NoteFilter(filters.FilterSet):
    """
    এই ফিল্টার ক্লাসটি category_name প্যারামিটার দিয়ে নোট ফিল্টার করতে সাহায্য করে।
    """
    category_name = filters.CharFilter(field_name='category__name', lookup_expr='exact')

    class Meta:
        model = Note
        fields = ['category_name']