from datetime import datetime
from pprint import pprint

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import serializers, status


from ..shop.models import ShopUnit


class ShopUnitImportSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=100,
                                 )
    date = serializers.CharField(max_length=100)
    parentId = serializers.UUIDField(allow_null=True)

    type = serializers.ChoiceField(choices=[
        ('OFFER', 'OFFER'),
        ('CATEGORY', 'CATEGORY')
    ])
    price = serializers.IntegerField(allow_null=True,
                                     min_value=0
                                     )
    # class Meta:
    #     model = ShopUnit
    #     fields = ('id', 'name', 'date', 'parentId', 'type', 'price')

    def create(self, validated_data):
        id = validated_data.get('id')
        shop_unit = ShopUnit.objects.get_shop_unit(id=id)

        if shop_unit is not None:
            print('обновляю')
            if shop_unit.type != validated_data['type']:
                raise serializers.ValidationError()
            # print(validated_data['name'])
            # print(shop_unit.name)
            # валидировать имя когда апдейт
            shop_unit.name = validated_data['name']
            shop_unit.parentId = validated_data['parentId']
            shop_unit.price = validated_data['price']
            shop_unit.date = validated_data['date']
            shop_unit.save()
        else:
            shop_unit = ShopUnit.objects.create(**validated_data)
        return shop_unit

    def validate(self, data):
        shop_unit_id = data.get('id')
        shop_unit = ShopUnit.objects.get_shop_unit(id=shop_unit_id)
        shop_unit_type = data.get('type')

        data['name'] = self._validate_name(data.get('name'), shop_unit)
        data['date'] = self._validate_date(data.get('date'))
        data['parentId'] = self._validate_parentId(data.get('parentId'), shop_unit)
        data['price'] = self._validate_price(data.get('price'), shop_unit_type)

        # pprint(data)

        return data

    def _validate_name(self, name, unit):
        if unit:
            return name
        if ShopUnit.objects.get_shop_unit(name=name):
            print('name')
            raise serializers.ValidationError()
        return name

    def _validate_date(self, value):
        try:
            datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            raise serializers.ValidationError()
        return value

    def _validate_parentId(self, pid, unit: ShopUnit):
        parent = ShopUnit.objects.get_shop_unit(id=pid)
        if parent and parent.type == 'OFFER' or parent == unit:
            print('parent')
            raise serializers.ValidationError()
        return parent

    def _validate_price(self, price, shop_unit_type):
        if shop_unit_type == 'OFFER' and price <= 0:
            print('цена у категории')
            raise serializers.ValidationError()
        if shop_unit_type == 'CATEGORY' and price is not None:
            print('цена у категории')
            raise serializers.ValidationError()
        return price
