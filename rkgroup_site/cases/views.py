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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем всех активных кейсов для навигации
        cases = list(Case.objects.filter(is_active=True).order_by('pk'))
        current_index = cases.index(self.object)
        
        if current_index > 0:
            context['prev_case'] = cases[current_index - 1]
        if current_index < len(cases) - 1:
            context['next_case'] = cases[current_index + 1]
        
        context['current_index'] = current_index + 1
        context['total_count'] = len(cases)
        
        return context