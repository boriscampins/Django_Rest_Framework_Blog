from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework_api.views import StandardAPIView
from rest_framework import permissions, status

from rest_framework.response import Response
from rest_framework.exceptions import NotFound, APIException
import redis
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .models import Post, PostView, PostAnalytics, Heading
from .serializers import PostListSerializer, PostSerializer, HeadingSerializer
from core.permissions import HasValidAPIKey
from .tasks import increment_post_impressions, increment_post_views_task
from .utils import get_client_ip

redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=6379, db=0)
#print(settings.REDIS_HOST)

class PostListView(StandardAPIView):
    permission_classes = [HasValidAPIKey]

    #@method_decorator(cache_page(60 * 1))
    def get(self, request, *args, **kwargs):
        try:

            cached_posts = cache.get("post_list")
            if cached_posts:
                for post in cached_posts:
                   redis_client.incr(f"post:impressions:{post['id']}") 
                return self.paginate(request, cached_posts)
            
            posts = Post.postobjects.all()
            
            if not posts.exists():
                raise NotFound(detail="No post found.")
            
            serialized_posts = PostListSerializer(posts, many=True).data


            cache.set("post_list", serialized_posts, timeout = 60 * 5)


            for post in posts:
                #increment_post_impressions.delay(post.id)
                redis_client.incr(f"post:impressions:{post.id}")  
                         
            
        except Exception as e:
           raise APIException(detail=f"An unexpected error ocurred: {str(e)}") 
        
        return self.paginate(request, serialized_posts)


class PostDetailView(StandardAPIView):
    permission_classes = [HasValidAPIKey]


    def get(self, request):
        ip_address = get_client_ip(request)

        slug = request.query_params.get("slug")

        try:
            cached_post = cache.get(f"post_detail:{slug}")
            if cached_post:
               #print(cached_post)
               increment_post_views_task.delay(cached_post['slug'], ip_address) 
               return self.response(cached_post) 

            post = Post.postobjects.get(slug=slug)

            serialized_post = PostSerializer(post).data   

            cache.set(f"post_detail:{slug}", serialized_post, timeout=60 * 5)
            
            increment_post_views_task.delay(post.slug, ip_address)
        
        except Post.DoesNotExist:
            raise NotFound(detail="The request post does not exits")
        except Exception as e:
            raise APIException(detail=f"Anunexpected error ocurred: {str(e)}") 
        return self.response(serialized_post)
    
class PostHeadingsView(StandardAPIView):
    permissions_classes = [HasValidAPIKey]

    def get(self, request):
        post_slug = request.query_params.get("slug")
        heading_objects = Heading.objects.filter(post__slug = post_slug)
        serialized_data = HeadingSerializer(heading_objects, many=True).data
        return self.response(serialized_data)


class IncrementPostClickView(StandardAPIView):
    
    def post(self, request):
        data = request.data
        try:
            post = Post.postobjects.get(slug=data['slug'])
        except Post.DoesNotExit:
            raise NotFound(detail= "The requested post does exist")    
                
        try:
            post_analytics, created = PostAnalytics.objects.get_or_create(post=post)
            post_analytics.increment_click()
        except Exception as e:
            raise APIException(detail="An error ocurred while updting post analytics: {str(e)}") 
        
        return self.response({
            "message": "Click incremented successfully",
            "clicks": post_analytics.clicks
        })