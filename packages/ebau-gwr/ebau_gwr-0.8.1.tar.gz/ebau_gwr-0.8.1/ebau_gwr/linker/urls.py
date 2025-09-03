from rest_framework.routers import SimpleRouter

from . import views

r = SimpleRouter(trailing_slash=False)

r.register(r"gwr-links", views.GWRLinkViewSet)

urlpatterns = r.urls
