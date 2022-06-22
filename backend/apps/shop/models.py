import math

from django.db import models

from django.db.models import Avg

from .managers import ShopUnitManager


class ShopUnit(models.Model):
    id = models.UUIDField(verbose_name='Уникальный идентификатор',
                          primary_key=True,
                          # default=uuid.uuid4
                          )
    name = models.CharField(verbose_name="Имя категории/товара",
                            max_length=100,
                            unique=True,
                            )
    date = models.DateTimeField(verbose_name='Время последнего обновления элемента',
                                )
    parentId = models.ForeignKey('self',
                                 verbose_name='UUID родительской категории',
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True,
                                 related_name='children'
                                 )
    type = models.CharField(verbose_name='Тип элемента - категория или товар',
                            choices=[
                                ('OFFER', 'OFFER'),
                                ('CATEGORY', 'CATEGORY')
                            ],
                            max_length=9
                            )
    price = models.IntegerField(verbose_name='Цена',
                                null=True,
                                blank=True
                                )

    objects = ShopUnitManager()

    def recalculate_price(self):
        new_price = self.children.all().aggregate(Avg('price'))['price__avg']
        if new_price:
            new_price = math.floor(new_price)
        self.price = new_price
        self.save()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = 'shop_unit'
