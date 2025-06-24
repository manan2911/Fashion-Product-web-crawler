import asyncio
from celery import shared_task
from django.utils import timezone
from .models import CrawlJob, ProductURL
from .crawler_worker import Crawler  # the refactored module

@shared_task
def run_crawl(job_id):
    job = CrawlJob.objects.get(pk=job_id)
    crawler = Crawler(job.url)
    products = asyncio.run(crawler.run())

    for url in products:
        ProductURL.objects.create(job=job, url=url)

    job.status = 'DONE'
    job.completed = timezone.now()
    job.save()
