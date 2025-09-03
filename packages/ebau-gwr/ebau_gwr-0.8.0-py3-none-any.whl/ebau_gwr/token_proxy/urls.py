from rest_framework.routers import SimpleRouter

from . import views

r = SimpleRouter(trailing_slash=False)

r.register(r"housing-stat-token", views.TokenProxyView, basename="housingstattoken")

urlpatterns = r.urls
