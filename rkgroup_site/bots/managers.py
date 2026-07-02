from django.core.cache import cache
from django.db import models


class BotManager(models.Manager):
    """Менеджер модели Bot с кэшированием"""
    
    CACHE_KEY_ACTIVE = 'bots_active'
    CACHE_TIMEOUT = 300
    
    def get_active_bots(self):
        """Возвращает активных ботов с кэшированием"""
        bots = cache.get(self.CACHE_KEY_ACTIVE)
        if bots is None:
            bots = list(self.filter(is_active=True).order_by('id'))
            cache.set(self.CACHE_KEY_ACTIVE, bots, self.CACHE_TIMEOUT)
        return bots
    
    def get_bot_with_navigation(self, pk):
        """Возвращает бота и соседей для навигации"""
        bots = self.get_active_bots()
        
        for idx, bot in enumerate(bots):
            if bot.pk == pk:
                return {
                    'current': bot,
                    'prev': bots[idx - 1] if idx > 0 else None,
                    'next': bots[idx + 1] if idx < len(bots) - 1 else None,
                    'index': idx + 1,
                    'total': len(bots),
                }
        return None
    
    def clear_cache(self):
        cache.delete(self.CACHE_KEY_ACTIVE)