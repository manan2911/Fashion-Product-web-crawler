from rest_framework import viewsets
from .models import CrawlJob
from .serializers import CrawlJobSerializer
from .tasks import run_crawl
import logging
logger = logging.getLogger(__name__)



class CrawlJobViewSet(viewsets.ModelViewSet):
    queryset = CrawlJob.objects.all().order_by('-created')
    serializer_class = CrawlJobSerializer

    def perform_create(self, serializer):
        job = serializer.save()
        logger.info(f"Enqueuing crawl job {job.id}")
        run_crawl.delay(job.id)