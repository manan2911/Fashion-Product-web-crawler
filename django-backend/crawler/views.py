# crawler/views.py

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import CrawlJob
from .serializers import CrawlJobSerializer
from .tasks import run_crawl  # your crawler logic

class CrawlJobViewSet(viewsets.ModelViewSet):
    """
    Your existing async/Celery‐backed endpoints at /api/jobs/
    """
    queryset = CrawlJob.objects.all().order_by('-created')
    serializer_class = CrawlJobSerializer

    def perform_create(self, serializer):
        job = serializer.save()
        # this was running via Celery before:
        run_crawl.delay(job.id)


class SyncCrawlAPIView(APIView):
    """
    A synchronous POST endpoint at /api/sync-jobs/ that
    will block until crawling completes.
    """

    def post(self, request, *args, **kwargs):
        url = request.data.get('url')
        if not url:
            return Response(
                {"error": "Missing 'url' in request body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1) Create job in DB
        job = CrawlJob.objects.create(url=url)

        # 2) Run crawler right now (not via Celery)
        #    run_crawl.run(...) executes the same code immediately.
        run_crawl.run(job.id)

        # 3) Reload from DB so .status, .completed, .products are updated
        job.refresh_from_db()

        # 4) Serialize and return the finished job
        serializer = CrawlJobSerializer(job)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """
        Optional: list all previous sync‐run jobs.
        """
        qs = CrawlJob.objects.all().order_by('-created')
        serializer = CrawlJobSerializer(qs, many=True)
        return Response(serializer.data)
