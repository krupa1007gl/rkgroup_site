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


class SiteMapPagesTests(TestCase):
    """
    Карта сайта по концепции: 5 страниц + FAQ отдают 200, старых
    приложений bots/news (удалены — их нет в концепции) больше не
    существует.
    """

    def test_concept_pages_return_200(self):
        for url in ['/', '/about/', '/partners/', '/cases/', '/faq/', '/contact/']:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, msg=url)

    def test_ailab_page_returns_200(self):
        response = self.client.get('/ailab/')
        self.assertEqual(response.status_code, 200)

    def test_removed_apps_are_gone(self):
        for url in ['/bots/', '/news/']:
            self.assertEqual(self.client.get(url).status_code, 404, msg=url)


class SeededContentTests(TestCase):
    """
    Контент наполняется data-миграциями, а не только фикстурами: на свежей
    БД (как на деплое) партнёрские бейджи, логотипы клиентов и карточки
    кейсов должны быть на месте, иначе блоки под {% if %} исчезают и
    страницы выглядят пустыми.
    """

    def test_home_shows_badges_and_client_logos(self):
        response = self.client.get('/')
        self.assertContains(response, 'badge-pill')
        self.assertContains(response, 'Twin')
        self.assertContains(response, 'Сколково')
        self.assertContains(response, 'client-logo-card')

    def test_cases_page_is_not_empty(self):
        response = self.client.get('/cases/')
        self.assertContains(response, 'case-card-modern')


class StylesheetWiringTests(TestCase):
    """
    Регрессия на повторявшийся класс багов: шаблон использует CSS-классы
    из файла, который сам не подключает, — вёрстка молча остаётся без
    стилей (так было с .cases-hero, .alert-*, .faq-item, .chat-bubble).
    """

    CSS_FOR_MARKER = {
        'faq-item': 'css/faq.css',
        'chat-bubble': 'css/base.css',
        'ui-mockup': 'css/base.css',
    }

    def test_pages_load_stylesheets_for_markup_they_use(self):
        for url in ['/', '/about/', '/partners/', '/faq/', '/ailab/']:
            content = self.client.get(url).content.decode()
            for marker, stylesheet in self.CSS_FOR_MARKER.items():
                if marker in content:
                    self.assertIn(
                        stylesheet, content,
                        msg=f'{url} использует .{marker}, но не подключает {stylesheet}',
                    )
