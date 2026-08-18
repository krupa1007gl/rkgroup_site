import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Lead
from .services import create_lead, update_lead_status

User = get_user_model()


class LeadServicesTests(TestCase):
    def test_create_lead_defaults_to_not_processed(self):
        lead = create_lead(lead_type=Lead.LeadType.CONTACT, name='Иван', email='i@i.com', description='Привет')
        self.assertEqual(lead.status, Lead.Status.NOT_PROCESSED)
        self.assertFalse(lead.phone_verified)
        self.assertIsNone(lead.phone_verified_at)

    def test_create_lead_phone_verified_sets_timestamp(self):
        lead = create_lead(lead_type=Lead.LeadType.AI_LAB, phone='+79161234567', phone_verified=True)
        self.assertTrue(lead.phone_verified)
        self.assertIsNotNone(lead.phone_verified_at)

    def test_update_lead_status_changes_status(self):
        lead = create_lead(lead_type=Lead.LeadType.CALLBACK, name='П', phone='+79161234567')
        update_lead_status(lead, Lead.Status.PROCESSED)
        lead.refresh_from_db()
        self.assertEqual(lead.status, Lead.Status.PROCESSED)

    def test_update_lead_status_noop_if_same(self):
        lead = create_lead(lead_type=Lead.LeadType.CALLBACK, name='П', phone='+79161234567')
        original_updated_at = lead.updated_at
        update_lead_status(lead, Lead.Status.NOT_PROCESSED)
        lead.refresh_from_db()
        self.assertEqual(lead.updated_at, original_updated_at)


class LeadsAdminAccessTests(TestCase):
    """
    /leads/ и /leads/update-status/ раньше были доступны без авторизации
    и отдавали данные всем — теперь это /admin/leads/... и должны
    редиректить на логин, а не отдавать 200 с данными.
    """

    def setUp(self):
        self.lead = create_lead(lead_type=Lead.LeadType.CONTACT, name='Секретный лид', email='s@s.com')

    def test_leads_list_requires_auth(self):
        response = self.client.get('/admin/leads/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_update_status_requires_auth(self):
        response = self.client.post(
            '/admin/leads/update-status/',
            data=json.dumps({'lead_id': self.lead.pk, 'status': 'processed'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 302)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, Lead.Status.NOT_PROCESSED)

    def test_old_public_urls_are_gone(self):
        self.assertEqual(self.client.get('/leads/').status_code, 404)
        self.assertEqual(self.client.get('/export-statistics/').status_code, 404)

    def test_staff_user_can_see_leads_list(self):
        User.objects.create_superuser('admin', 'admin@test.com', 'testpass123')
        self.client.login(username='admin', password='testpass123')
        response = self.client.get('/admin/leads/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Секретный лид')

    def test_staff_user_can_update_status(self):
        User.objects.create_superuser('admin', 'admin@test.com', 'testpass123')
        self.client.login(username='admin', password='testpass123')
        response = self.client.post(
            '/admin/leads/update-status/',
            data=json.dumps({'lead_id': self.lead.pk, 'status': 'processed'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, Lead.Status.PROCESSED)
