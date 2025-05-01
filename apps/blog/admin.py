from django.contrib import admin
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Category, Post, Heading, PostAnalytics

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'parent', 'slug')
    search_fields = ('name', 'title', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('parent',)
    ordering = ('name',)
    readonly_fields = ('id',)


class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget(config_name='default'))
    class Meta:
        model = Post
        fields = '__all__'

class HeadingInline(admin.TabularInline):
    model = Heading
    extra = 1
    fields = ('title', 'level', 'order', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('order',)
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ('title', 'status', 'category','created_at','updated_at')
    search_fields = ('title', 'description', 'content', 'keywords', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('status','category','updated_at',)
    ordering = ('-created_at',)
    readonly_fields = ('id','created_at','updated_at',)
    fieldsets = (
        ('General Information', {
            'fields': ('title','description', 'content', 'thumbnail','keywords','slug','category')
        }),
        ('Status & Date', {
            'fields': ('status','created_at','updated_at')
        }),
      
    )
    inlines = [ HeadingInline]

@admin.register(Heading)
class HeadingAdmin(admin.ModelAdmin):   
    list_display = ('title', 'post', 'level', 'order') 
    search_fields = ('title', 'post__title')
    list_filter = ('level', 'post')
    ordering = ('post','order')

@admin.register(PostAnalytics)    
class PostAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('pos_title','views', 'impressions', 'clicks', 'clicks_through_rate', 'avg_time_on_page')
    search_fields = ('post__title',)
    readonly_fields = ('post','views', 'impressions', 'clicks', 'clicks_through_rate', 'avg_time_on_page')
    ordering = ('-post__created_at',)

    def pos_title(self, obj):
        obj.post.title = obj.post.title
        return obj.post.title

    #post_title.short_description = 'Post Title'    