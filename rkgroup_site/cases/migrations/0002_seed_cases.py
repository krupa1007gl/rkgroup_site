import json
from pathlib import Path

from django.db import migrations

FIXTURE = Path(__file__).resolve().parent.parent / 'fixtures' / 'cases_data.json'


def seed_cases(apps, schema_editor):
    Case = apps.get_model('cases', 'Case')
    if Case.objects.exists():
        return

    with open(FIXTURE, encoding='utf-8') as f:
        records = json.load(f)

    for record in records:
        fields = dict(record['fields'])
        fields.pop('created_at', None)  # auto_now_add
        Case.objects.create(pk=record['pk'], **fields)


def unseed_cases(apps, schema_editor):
    Case = apps.get_model('cases', 'Case')
    with open(FIXTURE, encoding='utf-8') as f:
        records = json.load(f)
    Case.objects.filter(pk__in=[r['pk'] for r in records]).delete()


class Migration(migrations.Migration):
    dependencies = [('cases', '0001_initial')]

    operations = [migrations.RunPython(seed_cases, unseed_cases)]
