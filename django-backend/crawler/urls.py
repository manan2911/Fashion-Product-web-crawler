# crawler/urls.py

from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import CrawlJobViewSet, SyncCrawlAPIView

router = SimpleRouter()
router.register(r'jobs', CrawlJobViewSet, basename='job')

urlpatterns = [
    # our new sync endpoint:
    path('sync-jobs/', SyncCrawlAPIView.as_view(), name='sync-crawl'),
    # the old async/Celery-backed router:
    path('', include(router.urls)),
]
