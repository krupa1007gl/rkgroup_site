from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase

from .models import Visit

User = get_user_model()


class VisitTrackingMiddlewareTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_get_request_creates_visit(self):
        self.client.get('/about/')
        self.assertEqual(Visit.objects.count(), 1)
        visit = Visit.objects.first()
        self.assertEqual(visit.path, '/about/')
        self.assertEqual(visit.status_code, 200)

    def test_post_request_is_not_tracked(self):
        self.client.post('/callback/', {'name': 'Т', 'phone': '+79161234567'})
        self.assertEqual(Visit.objects.count(), 0)

    def test_admin_and_static_paths_are_ignored(self):
        self.client.get('/admin/login/')
        self.assertEqual(Visit.objects.count(), 0)

    def test_404_is_tracked(self):
        self.client.get('/this-page-does-not-exist/')
        self.assertEqual(Visit.objects.count(), 1)
        self.assertEqual(Visit.objects.first().status_code, 404)


class ExportStatisticsAccessTests(TestCase):
    def test_requires_auth(self):
        response = self.client.get('/admin/export-statistics/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_staff_user_can_export(self):
        User.objects.create_superuser('admin', 'admin@test.com', 'testpass123')
        self.client.login(username='admin', password='testpass123')
        Visit.objects.create(ip='1.2.3.4', path='/about/', status_code=200)

        response = self.client.post('/admin/export-statistics/', {'period': 'day'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
