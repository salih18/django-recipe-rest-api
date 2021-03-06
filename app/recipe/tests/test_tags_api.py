from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializers

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test Tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test thatthat login is required for retrieving tags"""

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test22@gmail.com', password='test123'
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""

        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')

        serializer = TagSerializers(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test tags for the authenticated user"""

        user2 = get_user_model().objects.create_user(
            email='test66@gmail.com',
            password='asda2ads'
        )

        Tag.objects.create(user=user2, name='Fruity')

        # This tag is the tag which authenticated user created
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        # This response contains self.client which we set self.user
        # in the setup function
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data), 1)

        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successfull(self):
        """Test creating a new tag"""

        payload = {'name': 'Test Tag'}

        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(user=self.user,
                                    name=payload['name']).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Creating a tag with invalid name"""

        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
