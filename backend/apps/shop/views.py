from pprint import pprint

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response

from .serializers import ShopUnitImportSerializer
from ..services.base import categories_recalculation
from ..services.error_codes import HTTP_REQUEST, HTTP_400_BAD_REQUEST
from ..shop.models import ShopUnit


class ShopUnitImport(CreateAPIView):
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
            return HTTP_400_BAD_REQUEST(e.detail)
        # Сохранение объектов
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # Перерасчет поля price у категорий, в которых произошли изменения
        changed_categories = set(
            ShopUnit.objects.get_shop_unit(
                id=unit["id"]) for unit in items if unit["type"] == 'CATEGORY')
        changed_categories.update(set(
            [ShopUnit.objects.get_shop_unit(id=item["parentId"]) for item in items if
             item["parentId"] is not None]))
        categories_recalculation(changed_categories)

        return HTTP_REQUEST(status.HTTP_200_OK, 'ok')
