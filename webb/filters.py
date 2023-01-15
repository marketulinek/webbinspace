from .models import Visit
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div
import django_filters


class VisitFilterFormHelper(FormHelper):
    form_method = 'GET'
    layout = Layout(
        Div(
            Div('target_name', css_class='col-sm-3'),
            Div('category', css_class='col-sm-3'),
            Div('keywords', css_class='col-sm-3'),
            Submit('submit', 'Filter', css_class='btn-outline-webb col-1'),
            css_class='row'
        )
    )


class VisitFilter(django_filters.FilterSet):
    target_name = django_filters.CharFilter(field_name='target_name', lookup_expr='icontains')
    keywords = django_filters.CharFilter(field_name='keywords', lookup_expr='icontains')

    class Meta:
        model = Visit
        fields = ['target_name', 'category', 'keywords']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper = VisitFilterFormHelper()
