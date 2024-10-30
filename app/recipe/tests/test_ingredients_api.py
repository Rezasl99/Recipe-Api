""" Test for ingredients API """

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Ingredient
)
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')

def create_user(email='user@example.com', password='password123'):
    """ Creating and returning a sample user """
    return get_user_model().objects.create_user(email=email,password=password)

class PublicIngredientsApiTests(TestCase):
    """ Test unauthenticated API request """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test authentication is required for retrieving ingredients. """
        res = self.client(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientsApiTests(TestCase):
    """ Testing Authenticated API request """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """ Test getting ingredients for authenticated users"""
        Ingredient.objects.create(user=self.user, name='ingredientsname1')
        Ingredient.objects.create(user=self.user, name= 'ingredientsname2')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """ Test list of ingredients is limited to authenticated user """
        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2, name='name2')
        ingredient = Ingredient.object.create(user=self.user, name='name1')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)
