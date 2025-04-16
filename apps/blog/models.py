from django.db import models
from django.utils import timezone



def blog_thumbnail_directory(instance, filename):
    return "blog/{0}{1}".format(instance.title, filename)

class Post(models.Models):

    class PostObjets(models.Manager)
        def get_queryset(self):
            return super().get_queryset().filter(status='published')


    status_options = (
        ("draf", "Draft"),
        ("published", "Published")
    )


    title = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    content = models.TextField()
    thumbnail = models.ImageField(upload_to=blog_thumbnail_directory)

    keywords = models.CharField(max_length=128)
    slug = models.CharField(max_length=128)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(max_Length=10, choices=status_options, deafult='draft')

    objects = models.Manager() # default manager
    postobjects = PostObjects() # custom manager

    class Meta:
        ordering = ("-published")

    def __str__(self):  
        return self.title  