from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from rest_framework.test import APIClient

from .models import Category, Post, PostAnalytics, Heading



class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name = "Tech",
            title="Technology",
            description="ALL about tecnology",
            slug="tech"

        )
    def test_category_creation(self):
        self.assertEqual(str(self.category), 'Tech')
        self.assertEqual(str(self.category.title), 'Technology')


class PostModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name = "Tech",
            title="Technology",
            description="ALL about tecnology",
            slug="tech"
        )
        self.post = Post.objects.create(
       
            title="Post 1",
            description="A test post",
            content="Content for the post",
            thumbnail=None,
            keywords="test, post",
            slug = "post-1",
            category=self.category,
            status="published"
        )
    def test_post_ceation(self):
        self.assertEqual(str(self.post), "Post 1")
        self.assertEqual(str(self.post.category.name), "Tech")

    def test_post_published_manager(self):
        self.assertTrue(Post.postobjects.filter(status="published").exists())

class PostAnaliticsModelTest(TestCase):
    def setUp(self):
        self.category =Category.objects.create(name="Analitics", slug="analitics")
        self.post = Post.objects.create(
            title="Analitics Post",
            description="A test post",
            content="Post for Analitics",
            slug = "analitics.post",
            category=self.category,
        )
        self.analitics = PostAnalytics.objects.create(post=self.post)

    def test_click_through_rate_update(self):
        self.analitics.increment_impression()
        self.analitics.increment_click()
        self.analitics.refresh_from_db()
        self.assertEqual(self.analitics.click_through_rate, 100.0)

class HeadingModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Heading", slug="heading")
        self.post = Post.objects.create(
            title="Post with Headings",
            description="Post containing headings",
            content="Content with heading",
            slug = "post-with-headings",
            category=self.category,
        )   
        self.heading = Heading.objects.create(
            post=self.post,
            title="Heading 1",
            slug="heading-1",
            level=1,
            order=1
        )  
    def test_heading_creation(self):
        self.assertEqual(self.heading.slug, "heading-1")
        self.assertEqual(self.heading.level, 1)       

class PostListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()   
        self.category = Category.objects.create(name="API", slug="api")
        self.api_key = settings.VALID_API_KEYS[0] 
        self.post = Post.objects.create(
            title="API Post",
            description="API Post description",
            content="API content",
            slug = "api-post",
            category=self.category,
            status="published"

        ) 
    def test_get_post_list(self):
        url = reverse('post-list')
        response = self.client.get(
            url,
            HTTP_API_KEY=self.api_key
        )
        
        #print(response.json())

        data = response.json()

        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertIn('success', data)
        self.assertEqual(data['status'], 200)
        self.assertIn('results', data)
        self.assertEqual(data['count'], 1)

        results = data['results']
        self.assertEqual(len(results), 1)


        post_data = results[0]

        self.assertEqual(post_data['id'], str(self.post.id))
        self.assertEqual(post_data['title'], self.post.title)
        self.assertEqual(post_data['description'], self.post.description)
        self.assertIsNone(post_data['thumbnail'])
        self.assertEqual(post_data['slug'], self.post.slug)

        category_data = post_data['category']
        self.assertEqual(category_data['name'], self.category.name)
        self.assertEqual(category_data['slug'], self.category.slug)

        self.assertEqual(post_data['view_count'], 0)
        self.assertIsNone(data['previous'])
