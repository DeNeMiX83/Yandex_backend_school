from django.core.exceptions import ObjectDoesNotExist
from django.db.models import manager


class ShopUnitManager(manager.Manager):
    def get_shop_unit(self, **kwargs):
        try:
            shop_unit = self.model.objects.get(**kwargs)
        except ObjectDoesNotExist:
            shop_unit = None
        return shop_unit