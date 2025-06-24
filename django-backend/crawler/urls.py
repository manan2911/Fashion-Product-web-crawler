# crawler/urls.py

from rest_framework.routers import DefaultRouter
from .views import CrawlJobViewSet

router = DefaultRouter()
router.register(r'jobs', CrawlJobViewSet, basename='crawljob')

urlpatterns = router.urls
