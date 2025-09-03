from django.conf.urls import include
from django.urls import path

urlpatterns = [
    path("api/v1/linker/", include("ebau_gwr.linker.urls")),
    path("api/v1/", include("ebau_gwr.token_proxy.urls")),
]
