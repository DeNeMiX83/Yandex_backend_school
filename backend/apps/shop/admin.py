from django.contrib import admin

from ..shop.models import ShopUnit


@admin.register(ShopUnit)
class ShopUnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date', 'parentId', 'type', 'price')
