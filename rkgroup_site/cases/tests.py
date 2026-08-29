from django.test import TestCase

from .models import Case


class CaseDataTests(TestCase):
    """
    Раздел «Кейсы» скрыт с сайта (маршруты не подключены, см. rkgroup/urls.py),
    но данные и модель остаются в проекте — чтобы вернуть раздел, когда
    появится первый настоящий кейс. Проверяем сами данные, а не страницы:
    контент должен остаться честным (без вымышленных цифр и без привязки
    к неподтверждённым компаниям).
    """

    def test_cases_are_seeded_by_migration(self):
        self.assertEqual(Case.objects.count(), 6)

    def test_no_unverified_real_company_names(self):
        stored = ' '.join(
            Case.objects.values_list('company', flat=True)
        ) + ' '.join(Case.objects.values_list('full_description', flat=True))
        for banned_name in ['Тверская генерация', 'X5 Retail Group', 'Ростелеком', 'ПЭК', 'ТТК', '2ГИС']:
            self.assertNotIn(banned_name, stored)
