from django.core.cache import cache
from django.test import TestCase, override_settings

from leads.models import Lead


@override_settings(RATELIMIT_ENABLED=True)
class ConsultationCreateViewTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_valid_submission_creates_lead(self):
        response = self.client.post(
            '/bots/consultation/',
            {
                'name': 'Игорь',
                'email': 'i@i.com',
                'phone': '+7 916 123-45-67',
                'message': 'Интересует бот',
                'bot_name': 'Голосовой бот',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        lead = Lead.objects.get(lead_type=Lead.LeadType.CONSULTATION)
        self.assertEqual(lead.bot_name, 'Голосовой бот')
        self.assertIn('Голосовой бот', lead.description)

    def test_invalid_phone_is_rejected(self):
        response = self.client.post(
            '/bots/consultation/',
            {'name': 'Игорь', 'email': 'i@i.com', 'phone': '123', 'bot_name': ''},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Lead.objects.exists())
