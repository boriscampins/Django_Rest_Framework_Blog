from celery import shared_task

import logging

import redis

from django.conf import settings

from .models import PostAnalytics

logger = logging.getLogger(__name__)

redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=6379, db=0)


@shared_task
def increment_post_impressions(post_id):
    
    try:
        analytics, created = PostAnalytics.objects.get_or_create(post__id=post_id)
        analytics.increment_impressions()
    except Exceptions as e:
        logger.info("Error Incrementing impressions for Post ID {post_id}: {str(e)}")

@shared_task
def sync_impression_to_db():
    keys = redis_client.keys("post:impressions:*")
    for key in keys:
        try:
            post_id = key.decode("utf-8").split(":")[-1]
            impressions = int(redis_client.get(key))
        
            analytics, created = PostAnalytics.objects.get_or_create(post__id=post_id)
            analytics.impressions += impressions
            analytics.save()
            
            redis_client.delete(key)
        except Exception as e:
            print (f"Error syncing impressions for {key}: {str(e)}")    