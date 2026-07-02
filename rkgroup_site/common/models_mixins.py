class TextListMixin:
    """Миксин для работы с текстовыми полями как со списками"""
    
    def get_list_from_text(self, field_name):
        """Безопасное преобразование текста с разделителями в список"""
        text = getattr(self, field_name, '')
        if text:
            return [item.strip() for item in text.split('\n') if item.strip()]
        return []
    
    def get_advantages_list(self):
        return self.get_list_from_text('advantages')
    
    def get_results_list(self):
        return self.get_list_from_text('results')
    
    def get_tags_list(self):
        return self.get_list_from_text('tags')
    
    def get_integrations_list(self):
        return self.get_list_from_text('integrations')
