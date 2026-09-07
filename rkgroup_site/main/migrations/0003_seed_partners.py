from django.db import migrations

# Партнёрские бейджи — статус компании, прямо заявленный в концепции.
BADGES = [
    ('Twin', 'https://twin24.ai'),
    ('Сколково', 'https://sk.ru'),
]

# Логотипы клиентов — плейсхолдеры. Реальные названия и логотипы можно
# ставить только после подтверждения права на публикацию по каждому
# клиенту (открытый вопрос из концепции). Заменяются через админку.
CLIENT_PLACEHOLDER_COUNT = 6
CLIENT_PLACEHOLDER_NAME = 'PLACEHOLDER — заменить на реального клиента'


def seed_partners(apps, schema_editor):
    Partner = apps.get_model('main', 'Partner')
    if Partner.objects.exists():
        return

    order = 0
    for name, website in BADGES:
        order += 1
        Partner.objects.create(name=name, partner_type='badge', website=website, order=order)

    for _ in range(CLIENT_PLACEHOLDER_COUNT):
        order += 1
        Partner.objects.create(name=CLIENT_PLACEHOLDER_NAME, partner_type='client', order=order)


def unseed_partners(apps, schema_editor):
    Partner = apps.get_model('main', 'Partner')
    Partner.objects.filter(name__in=[name for name, _ in BADGES]).delete()
    Partner.objects.filter(name=CLIENT_PLACEHOLDER_NAME).delete()


class Migration(migrations.Migration):
    dependencies = [('main', '0002_partner_partner_type')]

    operations = [migrations.RunPython(seed_partners, unseed_partners)]
