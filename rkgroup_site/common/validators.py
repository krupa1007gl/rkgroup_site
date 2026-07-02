import re
from django.core.exceptions import ValidationError


def validate_phone(value):
    """Валидация российского номера телефона"""
    cleaned = re.sub(r'[\s\(\)\-]', '', value)
    
    patterns = [
        r'^\+7\d{10}$',
        r'^8\d{10}$',
        r'^\d{10}$',
        r'^7\d{10}$',
    ]
    
    if not any(re.match(pattern, cleaned) for pattern in patterns):
        raise ValidationError('Введите корректный номер телефона (например: +7 915 725-88-78)')
    
    if cleaned.startswith('8'):
        cleaned = '+7' + cleaned[1:]
    elif cleaned.startswith('7') and len(cleaned) == 11:
        cleaned = '+' + cleaned
    elif len(cleaned) == 10:
        cleaned = '+7' + cleaned
    
    return cleaned


def validate_email(value):
    """Валидация email"""
    if '@' not in value or '.' not in value.split('@')[-1]:
        raise ValidationError('Введите корректный email адрес')
    return value


def validate_image_size(value, max_size_mb=5):
    """Проверка размера изображения"""
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'Размер изображения не должен превышать {max_size_mb} МБ')
    return value


def validate_image_extension(value):
    """Проверка расширения изображения"""
    import os
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    
    if ext not in valid_extensions:
        raise ValidationError(f'Неподдерживаемый формат. Разрешенные: {", ".join(valid_extensions)}')
    return value
