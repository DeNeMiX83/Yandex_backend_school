from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.response import Response

from .serializers import *
from ..services.base import categories_recalculation
from ..services.exсeptions import ValidationError
from ..services.responses import HTTP_REQUEST, HTTP_400_BAD_REQUEST


class ShopUnitImportView(CreateAPIView):
    serializer_class = ShopUnitImportSerializer
    queryset = ShopUnit.objects.all()

    def create(self, request, *args, **kwargs):
        # Проверка даты
        updateDate = request.data.get('updateDate')
        if not updateDate:
            return HTTP_400_BAD_REQUEST("not updateDate")

        # Проверка items
        items = request.data.get('items', [])
        if not items:
            return HTTP_400_BAD_REQUEST("list items is empty")
        # Добавления updateDate, проверка id и name на уникальность
        count_uuid = dict()
        count_name = dict()
        for item in items:
            # проверка id
            count_uuid[item['id']] = count_uuid.get(item['id'], 0) + 1
            if count_uuid[item['id']] > 1:
                return HTTP_400_BAD_REQUEST("uuid duplicate")
            # проверка name
            count_name[item['name']] = count_name.get(item['name'], 0) + 1
            if count_name[item['name']] > 1:
                return HTTP_400_BAD_REQUEST("name duplicate")

            item.update({'date': updateDate})

        serializer = self.get_serializer(data=items, many=True)
        try:
            # Сериализация + валидация
            serializer.is_valid(raise_exception=True)
            # Сохранение объектов
            self.perform_create(serializer)
        except ValidationError as e:
            return HTTP_400_BAD_REQUEST(e)
        print(serializer.data)
        # Перерасчет поля price у категорий, в которых произошли изменения
        changed_categories = set()
        for item in items:
            item = ShopUnit.objects.get_shop_unit(id=item.get("parentId"))
            if item:
                changed_categories.add(item)

        categories_recalculation(changed_categories)

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['DELETE'])
def shop_unit_destroy(request, *args, **kwargs):
    try:
        unit = ShopUnit.objects.get(id=kwargs.get("id"))
    except DjangoValidationError:
        return HTTP_400_BAD_REQUEST("Invalid uuid")
    except ObjectDoesNotExist:
        return HTTP_400_BAD_REQUEST("Item not found")
    # пересчитать price родителя после удаление child
    if unit.parentId is not None:
        categories_recalculation([unit.parentId])
    unit.delete()
    return HTTP_REQUEST(status.HTTP_200_OK, 'ok')


class ShopUnitRetrieveView(RetrieveAPIView):
    serializer_class = ShopUnitRetrieveSerializer
    queryset = ShopUnit.objects.all()
    lookup_field = 'id'


class ShopUnitSalesView(ListAPIView):
    serializer_class = PatternShopForRetrieveSerializer

    def get_queryset(self):
        query = self.request.GET.get('date')
        if query is None:
            raise ValidationError('date is empty')
        date = validate_date(query)
        return ShopUnit.objects.filter(date__gte=date - timedelta(hours=24), date__lte=date,
                                       type='OFFER')

    def get(self, request, *args, **kwargs):
        try:
            return self.list(request, *args, **kwargs)
        except ValidationError as e:
            return HTTP_400_BAD_REQUEST(e)