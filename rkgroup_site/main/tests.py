from django.core.cache import cache
from django.test import TestCase, override_settings

from leads.models import Lead


@override_settings(RATELIMIT_ENABLED=True)
class FormLeadCreationTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_callback_creates_lead(self):
        response = self.client.post(
            '/callback/', {'name': 'Пётр', 'phone': '+7 916 123-45-67'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        lead = Lead.objects.get(lead_type=Lead.LeadType.CALLBACK)
        self.assertEqual(lead.name, 'Пётр')

    def test_contact_creates_lead(self):
        response = self.client.post(
            '/contact/',
            {'name': 'Анна', 'email': 'a@a.com', 'message': 'Привет'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        lead = Lead.objects.get(lead_type=Lead.LeadType.CONTACT)
        self.assertEqual(lead.email, 'a@a.com')

    def test_partners_creates_lead(self):
        response = self.client.post(
            '/partners/',
            {'name': 'ООО Ромашка', 'email': 'r@r.com', 'company': 'Ромашка'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        lead = Lead.objects.get(lead_type=Lead.LeadType.PARTNER)
        self.assertEqual(lead.company, 'Ромашка')

    def test_partners_rejects_invalid_email(self):
        response = self.client.post(
            '/partners/',
            {'name': 'Кто-то', 'email': 'не-email', 'company': 'X'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Lead.objects.filter(lead_type=Lead.LeadType.PARTNER).exists())

    def test_honeypot_blocks_lead_without_error(self):
        response = self.client.post(
            '/contact/',
            {'name': 'Bot', 'email': 'b@b.com', 'message': 'spam', 'website': 'http://spam.example'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Lead.objects.exists())

    def test_rate_limit_blocks_after_threshold(self):
        for _ in range(10):
            response = self.client.post(
                '/callback/', {'name': 'П', 'phone': '+79161234567'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/callback/', {'name': 'П', 'phone': '+79161234567'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 429)
        self.assertEqual(Lead.objects.filter(lead_type=Lead.LeadType.CALLBACK).count(), 10)
