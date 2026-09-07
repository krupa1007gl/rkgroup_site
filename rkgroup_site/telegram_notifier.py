import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_message(message):
    """
    Отправляет сообщение в Telegram
    Токен и chat_id берутся из настроек
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not bot_token or not chat_id:
        logger.warning("⚠️ TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не настроены")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"✅ Telegram сообщение отправлено")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ошибка отправки в Telegram: {e}")
        return False


def send_new_lead_notification(name, phone, source, bot_name=''):
    """
    Отправляет уведомление о новой заявке
    """
    message = (
        f"🟢 <b>НОВАЯ ЗАЯВКА!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 <b>Имя:</b> {name}\n"
        f"📞 <b>Телефон:</b> {phone}\n"
        f"🔗 <b>Источник:</b> {source or 'Сайт'}\n"
    )
    if bot_name:
        message += f"🤖 <b>Бот:</b> {bot_name}\n"
    
    from datetime import datetime
    message += f"📅 <b>Время:</b> {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}\n"
    message += f"━━━━━━━━━━━━━━━━━━━━\n"
    message += f"📌 <i>Требуется обработка</i>"
    
    return send_telegram_message(message)


def send_status_change_notification(phone, old_status, new_status):
    """
    Отправляет уведомление об изменении статуса заявки
    """
    emoji = "✅" if new_status == "Обработано" else "🔄"
    
    message = (
        f"{emoji} <b>СТАТУС ИЗМЕНЁН</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📞 <b>Телефон:</b> {phone}\n"
        f"📌 <b>Было:</b> {old_status}\n"
        f"🔄 <b>Стало:</b> {new_status}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    return send_telegram_message(message)


def send_daily_report(stats):
    """
    Отправляет ежедневный отчёт
    stats: dict с ключами date, new, processed, expired, conversion
    """
    message = (
        f"📊 <b>ЕЖЕДНЕВНЫЙ ОТЧЁТ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 <b>Дата:</b> {stats['date']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆕 <b>Новых лидов:</b> {stats['new']}\n"
        f"✅ <b>Обработано:</b> {stats['processed']}\n"
        f"⏰ <b>Просрочено:</b> {stats['expired']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📈 <b>Конверсия:</b> {stats['conversion']:.1f}%\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <i>Отчёт сформирован автоматически</i>"
    )
    
    return send_telegram_message(message)
