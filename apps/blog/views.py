from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework import permissions

from rest_framework.response import Response
from rest_framework.exceptions import NotFound, APIException

from .models import Post, PostView, PostAnalytics
from .serializers import PostListSerializer, PostSerializer, HeadingSerializer
from .utils import get_client_ip


#class PostListView(ListAPIView):
    #queryset = Post.postobjects.all()
    #serializer_class = PostListSerializer

class PostListView(APIView):
    def get(self, request,*args, **kwargs):
        try:
            posts = Post.postobjects.all()
            if not posts.exists():
                raise NotFound(detail="No post found.")
            
            serialized_posts = PostListSerializer(posts, many=True).data
        except Post.DoesNotExist:
            raise NotFound(detail="No post found")
        except Exceptions as e:
            raise APIException(detail="Anunexpected error ocurred: {str(e)}") 
        return Response(serialized_posts)



#class PostDetailView(RetrieveAPIView):
    #queryset = Post.postobjects.all()
    #serializer_class = PostSerializer
    #lookup_field = 'slug'

class PostDetailView(RetrieveAPIView):
    def get(self, request, slug):
        try:
            post = Post.postobjects.get(slug=slug)
        except Post.DoesNotExist:
            raise NotFound(detail="The request post does not exits")
        except Exceptions as e:
            raise APIException(detail="Anunexpected error ocurred: {str(e)}") 
        
        serialized_post = PostSerializer(post).data   
        
        try:
            post_analytics = PostAnalytics.objects.get(post=post)
            post_analytics.increment_view(request)
        except PostAnalytics.DoesNotExist:
            raise NotFound(detail="Analytics data for this post does not exist")
        except Exceptions as e:
            raise APIException(detail="An error ocurred while updting post analytics: {str(e)}") 

        return Response(serialized_post)
    
class IncrementPostClickView(APIView):
    
    def post(self, request):
        data = request.data
        try:
            post = Post.postobjects.get(slug=data['slug'])
        except Post.DoesNotExit:
            raise NotFound(detail= "The requested post does exist")    
        except Exceptions as e:
            raise APIException(detail="An error ocurred while ...: {str(e)}") 
        try:
            post_analytics, created = PostAnalytics.objects.get_or_create(post=post)
            post_analytics.increment_click()
        except Exceptions as e:
            raise APIException(detail="An error ocurred while updting post analytics: {str(e)}") 
        return Response({
            "message": "Click incremented successfully",
            "clicks": post_analytics.clicks
        })