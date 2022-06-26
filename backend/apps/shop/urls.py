from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from ..shop.views import *

schema_view = get_schema_view(
    openapi.Info(
        title="Yandex Market",
        default_version='v0.0.1',
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('imports', ShopUnitImportView.as_view()),
    path('delete/<str:id>', shop_unit_destroy),
    path('nodes/<str:id>', ShopUnitRetrieveView.as_view()),
    path('sales', ShopUnitSalesView.as_view()),
    path('swagger', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui')
]
