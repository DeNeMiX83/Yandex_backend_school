from datetime import datetime

from ..services.exсeptions import ValidationError
from ..shop.models import ShopUnit


def validate_name(name, unit):
    unit_use_name = ShopUnit.objects.get_shop_unit(name=name)
    if unit and unit == unit_use_name:
        return name
    if unit_use_name:
        print('name')
        raise ValidationError('name')
    return name


def validate_date(value):
    try:
        date = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        raise ValidationError("date parse failed")
    return date


def validate_parentId(pid, unit: ShopUnit):
    parent = ShopUnit.objects.get_shop_unit(id=pid)
    if parent and (parent.type == 'OFFER' or parent == unit):
        print('parent')
        raise ValidationError('parentId')
    return parent


def validate_price(price, shop_unit_type):
    if shop_unit_type == 'OFFER' and (price is None or price < 0):
        print('цена у категории')
        raise ValidationError('OFFER price must be >= 0')
    if shop_unit_type == 'CATEGORY' and price is not None:
        print('цена у категории')
        raise ValidationError('CATEGORY price must be null')
    return price
