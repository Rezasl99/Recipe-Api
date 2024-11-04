""" Test for the tags API """

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Tag,
    Recipe,
    )

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    """ Create and return a tag detail url """
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='password123'):
    """ Create and return a new example user """
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsAPITests(TestCase):
    """ Test unauthenticated API request """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test authentication is required for retrieving tags """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsAPITest(TestCase):
    """ Test authenticated API request """
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """ Test retrieving a list of tags """
        Tag.objects.create(user=self.user, name='Tag1')
        Tag.objects.create(user=self.user, name='Tag2')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """ Test list of tags is limited to authenticated user """
        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='user2name')
        tag = Tag.objects.create(user=self.user, name='user1name')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """ Test updating a tag """
        tag = Tag.objects.create(user=self.user, name='Tagname')

        payload = {'name':'Tagupdatedname'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """ Test deleting a tag """
        tag = Tag.objects.create(user=self.user, name='Tagname')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """ Test listing tags to those assigned to recipe """
        tag1 = Tag.objects.create(user=self.user, name='tag1name')
        tag2 = Tag.objects.create(user=self.user, name='tag2name')


        recipe = Recipe.objects.create(
            title='titlesample',
            time_minutes=50,
            price=Decimal('2.5'),
            user=self.user,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtred_tags_unique(self):
        """ Test filtered tags return a unique list """
        tag = Tag.objects.create(user=self.user, name= 'tag1name')
        Tag.objects.create(user=self.user, name='tag2name')

        recipe1 = Recipe.objects.create(
            title='title1sample',
            time_minutes=50,
            price=Decimal('2.5'),
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='title2sample',
            time_minutes=51,
            price=Decimal('3.5'),
            user=self.user,
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
