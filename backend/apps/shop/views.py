from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response

from .serializers import *
from ..services.base import categories_recalculation
from ..services.responses import HTTP_REQUEST, HTTP_400_BAD_REQUEST
from ..shop.models import ShopUnit


class ShopUnitImportView(CreateAPIView):
    serializer_class = ShopUnitImportSerializer
    queryset = ShopUnit.objects.all()

    def create(self, request, *args, **kwargs):
        # Проверка даты
        updateDate = request.data.get('updateDate')
        if not updateDate:
            return HTTP_400_BAD_REQUEST("not updateDate")

        # Проверка items и добавления даты в item
        items = request.data.get('items', [])
        if not items:
            return HTTP_400_BAD_REQUEST("list items is empty")
        for item in items:
            item.update({'date': updateDate})

        # Сериализация + валидация
        serializer = self.get_serializer(data=items, many=True)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return HTTP_400_BAD_REQUEST(list(e.detail[0].items())[0][1][0])
        # Сохранение объектов
        self.perform_create(serializer)

        # Перерасчет поля price у категорий, в которых произошли изменения
        changed_categories = set(
            ShopUnit.objects.get_shop_unit(id=item["parentId"])
            for item in items if item["parentId"] is not None)

        categories_recalculation(changed_categories)

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['DELETE'])
def shop_unit_destroy(request, *args, **kwargs):
    unit = ShopUnit.objects.get(id=kwargs.get("id"))
    if not unit:
        return HTTP_400_BAD_REQUEST('Item not found')
    unit.delete()

    # пересчитать price родителя после удаление child
    categories_recalculation([unit.parentId])
    return HTTP_REQUEST(status.HTTP_200_OK, 'ok')


class ShopUnitRetrieveView(RetrieveAPIView):
    serializer_class = ShopUnitRetrieveSerializer
    queryset = ShopUnit.objects.all()
    lookup_field = 'id'

