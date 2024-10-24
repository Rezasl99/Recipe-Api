# Test for recipe apis
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def create_recipe(user, **params):
    # create and return a sample recipe
    default = {
        'title': 'sample reciple title',
        'time_minutes': '22',
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf',
    }
    default.update(params)

    recipe = Recipe.objects.create(user=user, **default)
    return recipe

class PublicRecipeAPITest(TestCase):
    # Test unauthenticated API request

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        # Test auth is required to call API
        res = self.client(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHRIZED)


class PrivateRecipeAPITest(TestCase):
    # Test authenticated API request

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email = 'user@example.com',
            password = 'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrive_recipe(self):
        # Test getting a list of recipe
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipe = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        # Test list of recipes is limited to authenticated user
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'pass12345',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

