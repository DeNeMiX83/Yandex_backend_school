from rest_framework import serializers

from ..services.base import categories_recalculation
from ..services.exсeptions import ValidationError
from ..services.validation import validate_name, validate_date, validate_parentId, validate_price
from ..shop.models import ShopUnit


class ShopUnitImportSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=100,
                                 )
    serializers.DateTimeField
    date = serializers.CharField(max_length=100)
    parentId = serializers.UUIDField(allow_null=True)

    type = serializers.ChoiceField(choices=[
        ('OFFER', 'OFFER'),
        ('CATEGORY', 'CATEGORY')
    ])
    price = serializers.IntegerField(allow_null=True)

    def create(self, validated_data):
        id = validated_data.get('id')
        shop_unit = ShopUnit.objects.get_shop_unit(id=id)
        if shop_unit is not None:
            print('обновляю')
            old_parent = shop_unit.parentId
            if shop_unit.type != validated_data['type']:
                raise ValidationError("you can't change the type")
            shop_unit.name = validated_data['name']
            shop_unit.parentId = validated_data['parentId']
            if shop_unit.type == 'OFFER':
                shop_unit.price = validated_data['price']
            shop_unit.date = validated_data['date']
            shop_unit.save()
            # обновляем price у отвязанного родителя
            if old_parent is not None:
                categories_recalculation([old_parent])
        else:
            shop_unit = ShopUnit.objects.create(**validated_data)
        return shop_unit

    def validate(self, data):
        shop_unit_id = data.get('id')
        shop_unit = ShopUnit.objects.get_shop_unit(id=shop_unit_id)
        shop_unit_type = data.get('type')

        data['name'] = validate_name(data.get('name'), shop_unit)
        data['date'] = validate_date(data.get('date'))
        data['parentId'] = validate_parentId(data.get('parentId'), shop_unit)
        data['price'] = validate_price(data.get('price'), shop_unit_type)

        # pprint(data)

        return data



class PatternShopForRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopUnit
        fields = ('id', 'name', 'date', 'type', 'price', 'parentId')


class ShopUnitRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopUnit
        fields = ('id', 'name', 'date', 'type', 'price', 'parentId')

    def to_representation(self, unit: ShopUnit):
        return self.get_json(unit)

    def get_json(self, unit: ShopUnit):
        children = unit.children.all()
        data = PatternShopForRetrieveSerializer.to_representation(self, unit)
        if children is None:
            return PatternShopForRetrieveSerializer(unit)
        correct_children = []
        for child in children:
            child = self.get_json(child)
            correct_children.append(child)
        if unit.type == 'CATEGORY':
           data.update({'children': correct_children})
        return data



