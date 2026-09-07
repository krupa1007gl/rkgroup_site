import json

from django.core.cache import cache
from django.test import TestCase, override_settings

from leads.models import Lead

from .models import PhoneVerificationCode


def post_json(client, url, payload):
    return client.post(url, data=json.dumps(payload), content_type='application/json')


class AILabPageTests(TestCase):
    def test_page_returns_200(self):
        response = self.client.get('/ailab/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ailab.js')


class StaticEndpointsTests(TestCase):
    def test_scenario_returns_lines(self):
        response = self.client.get('/ailab/scenario/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('lines', response.json())

    def test_demo_crm_and_excel_return_json(self):
        self.assertEqual(self.client.get('/ailab/demo/crm/').status_code, 200)
        self.assertEqual(self.client.get('/ailab/demo/excel/').status_code, 200)

    def test_bot_status_is_coming_soon(self):
        response = self.client.get('/ailab/bot/status/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'coming_soon')


@override_settings(RATELIMIT_ENABLED=True, AILAB_STUB_OTP_CODE='0000')
class PhoneVerificationFlowTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_invalid_phone_is_rejected(self):
        response = post_json(self.client, '/ailab/verify/start/', {'phone': '123'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(PhoneVerificationCode.objects.exists())

    def test_honeypot_on_start_is_silently_ignored(self):
        response = post_json(self.client, '/ailab/verify/start/', {'phone': '+79161234567', 'website': 'spam'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(PhoneVerificationCode.objects.exists())

    def test_full_flow_creates_verified_lead(self):
        start = post_json(self.client, '/ailab/verify/start/', {'phone': '+7 916 123-45-67'})
        self.assertEqual(start.status_code, 200)
        self.assertTrue(PhoneVerificationCode.objects.filter(phone='+79161234567').exists())

        wrong = post_json(self.client, '/ailab/verify/confirm/', {'phone': '+79161234567', 'code': '1111'})
        self.assertEqual(wrong.status_code, 400)

        right = post_json(self.client, '/ailab/verify/confirm/', {'phone': '+79161234567', 'code': '0000'})
        self.assertEqual(right.status_code, 200)
        self.assertTrue(right.json()['verified'])

        lead = Lead.objects.get(lead_type=Lead.LeadType.AI_LAB, phone='+79161234567')
        self.assertTrue(lead.phone_verified)
        self.assertIsNotNone(lead.phone_verified_at)

    def test_code_cannot_be_reused(self):
        post_json(self.client, '/ailab/verify/start/', {'phone': '+79161234567'})
        post_json(self.client, '/ailab/verify/confirm/', {'phone': '+79161234567', 'code': '0000'})

        second_attempt = post_json(self.client, '/ailab/verify/confirm/', {'phone': '+79161234567', 'code': '0000'})
        self.assertEqual(second_attempt.status_code, 400)

    def test_attempts_are_limited(self):
        post_json(self.client, '/ailab/verify/start/', {'phone': '+79161234567'})
        for _ in range(PhoneVerificationCode.MAX_ATTEMPTS):
            post_json(self.client, '/ailab/verify/confirm/', {'phone': '+79161234567', 'code': 'wrong'})

        response = post_json(self.client, '/ailab/verify/confirm/', {'phone': '+79161234567', 'code': '0000'})
        self.assertEqual(response.status_code, 400)

    def test_rate_limit_per_phone_on_start(self):
        for _ in range(5):
            response = post_json(self.client, '/ailab/verify/start/', {'phone': '+79161234567'})
            self.assertEqual(response.status_code, 200)

        response = post_json(self.client, '/ailab/verify/start/', {'phone': '+79161234567'})
        self.assertEqual(response.status_code, 429)


@override_settings(RATELIMIT_ENABLED=True)
class LiveBotNotifyMeTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_creates_lead(self):
        response = post_json(self.client, '/ailab/bot/notify-me/', {'name': 'Аня', 'phone': '+79161234567'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Lead.objects.filter(lead_type=Lead.LeadType.AI_LAB, phone='+79161234567').exists())

    def test_honeypot_blocks_lead(self):
        response = post_json(
            self.client, '/ailab/bot/notify-me/', {'phone': '+79161234567', 'website': 'spam'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Lead.objects.exists())
