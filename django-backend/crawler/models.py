from django.db import models

class CrawlJob(models.Model):
    url       = models.URLField()
    created   = models.DateTimeField(auto_now_add=True)
    completed = models.DateTimeField(null=True, blank=True)
    status    = models.CharField(max_length=20, default='PENDING')

    def __str__(self):
        return f'Job {self.id} on {self.url}'

class ProductURL(models.Model):
    job = models.ForeignKey(CrawlJob, on_delete=models.CASCADE, related_name='products')
    url = models.TextField()

    def __str__(self):
        return self.url
