import logging

from django.utils import timezone

from telegram_notifier import send_new_lead_notification, send_status_change_notification

from .models import Lead

logger = logging.getLogger(__name__)


def create_lead(
    lead_type,
    name='',
    email='',
    phone='',
    company='',
    bot_name='',
    description='',
    source='',
    phone_verified=False,
):
    """Создаёт заявку и отправляет уведомление в Telegram (если настроен)."""
    lead = Lead.objects.create(
        lead_type=lead_type,
        name=name,
        email=email,
        phone=phone,
        company=company,
        bot_name=bot_name,
        description=description,
        source=source[:200],
        phone_verified=phone_verified,
        phone_verified_at=timezone.now() if phone_verified else None,
    )

    send_new_lead_notification(
        name=lead.name or 'Не указано',
        phone=lead.phone or 'Не указан',
        source=lead.source,
        bot_name=lead.bot_name,
    )
    logger.info('Новая заявка #%s (%s): %s', lead.pk, lead.lead_type, lead.name)
    return lead


def update_lead_status(lead, new_status, changed_by=None):
    """Меняет статус заявки и отправляет уведомление об изменении."""
    old_status = lead.status
    old_status_label = lead.get_status_display()
    if old_status == new_status:
        return lead

    lead.status = new_status
    lead.save(update_fields=['status', 'updated_at'])

    who = getattr(changed_by, 'username', 'system')
    logger.info(
        'Статус заявки #%s изменён пользователем %s: %s -> %s',
        lead.pk, who, old_status, new_status,
    )

    if lead.phone:
        send_status_change_notification(lead.phone, old_status_label, lead.get_status_display())

    return lead
