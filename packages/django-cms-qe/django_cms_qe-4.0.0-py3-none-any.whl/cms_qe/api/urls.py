from django.conf import settings
from django.urls import include, path
from django.utils.module_loading import import_string
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from knox.auth import TokenAuthentication
from knox.views import LoginView as KnoxLoginView, LogoutView as KnoxLogoutView
from rest_framework import routers

from .permissions import CmsQeApiPermission
from .views import CmsQeBasicAuthentication

ROUTER = routers.DefaultRouter()

for url, view_path, name in getattr(settings, "API_VIEWS", []):
    BaseClass = import_string(view_path)
    ApiClass = type(f'Api{BaseClass.__name__}', (BaseClass,), {
        "authentication_classes": BaseClass.authentication_classes + [CmsQeBasicAuthentication, TokenAuthentication],
        "permission_classes": BaseClass.permission_classes + [CmsQeApiPermission],
    })
    ROUTER.register(url, ApiClass, basename=name)


urlpatterns = [
    path("", include(ROUTER.urls)),
    path("login/", KnoxLoginView.as_view(
        authentication_classes=(CmsQeBasicAuthentication,), permission_classes=(CmsQeApiPermission,)),),
    path("logout/", KnoxLogoutView.as_view()),
    # Docs
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
