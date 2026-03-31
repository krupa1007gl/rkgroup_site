from django.views.generic import ListView, DetailView
from .models import News

class NewsListView(ListView):
    model = News
    template_name = 'news/news_list.html'
    context_object_name = 'news'
    paginate_by = 6
    
    def get_queryset(self):
        return News.objects.filter(is_active=True)

class NewsDetailView(DetailView):
    model = News
    template_name = 'news/news_detail.html'
    context_object_name = 'news'