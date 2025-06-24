from rest_framework import serializers
from .models import CrawlJob, ProductURL

class ProductURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductURL
        fields = ['url']

class CrawlJobSerializer(serializers.ModelSerializer):
    products = ProductURLSerializer(many=True, read_only=True)

    class Meta:
        model = CrawlJob
        fields = ['id', 'url', 'status', 'created', 'completed', 'products']
        read_only_fields = ['status', 'created', 'completed', 'products']
