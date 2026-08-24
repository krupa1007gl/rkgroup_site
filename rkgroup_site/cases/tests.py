from django.test import TestCase

from .models import Case


class CaseHonestContentTests(TestCase):
    """Кейсы — обезличенные сценарии, без привязки к неподтверждённым компаниям."""

    fixtures = ['cases_data.json']

    def test_list_page_returns_200(self):
        response = self.client.get('/cases/')
        self.assertEqual(response.status_code, 200)

    def test_detail_page_returns_200(self):
        case = Case.objects.first()
        response = self.client.get(f'/cases/{case.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_no_unverified_real_company_names(self):
        response = self.client.get('/cases/')
        content = response.content.decode()
        for banned_name in ['Тверская генерация', 'X5 Retail Group', 'Ростелеком', 'ПЭК', 'ТТК', '2ГИС']:
            self.assertNotIn(banned_name, content)
