from django.views.generic import ListView, DetailView
from .models import Case

class CaseListView(ListView):
    model = Case
    template_name = 'cases/case_list.html'
    context_object_name = 'cases'
    paginate_by = 9
    
    def get_queryset(self):
        return Case.objects.filter(is_active=True)

class CaseDetailView(DetailView):
    model = Case
    template_name = 'cases/case_detail.html'
    context_object_name = 'case'