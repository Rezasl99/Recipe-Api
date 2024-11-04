""" Test for ingredients API """

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Ingredient,
    Recipe,
)
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')

def detail_url(ingredient_id):
    """ Create and return an ingredient detail URL """
    return reverse('recipe:ingredient-detail', args=[ingredient_id])

def create_user(email='user@example.com', password='password123'):
    """ Creating and returning a sample user """
    return get_user_model().objects.create_user(email=email,password=password)

class PublicIngredientsApiTests(TestCase):
    """ Test unauthenticated API request """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test authentication is required for retrieving ingredients. """
        res = self.client.get(INGREDIENTS_URL)

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
        ingredient = Ingredient.objects.create(user=self.user, name='name1')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """ Test updating an ingredient """
        ingredient = Ingredient.objects.create(user=self.user, name='mincedmeat')

        payload = {'name': 'raw-meat'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """ Test deleting an ingredient """
        ingredient = Ingredient.objects.create(user= self.user, name='testname')

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipe(self):
        """ Test listing ingredients by those assigned to recipe """
        in1 = Ingredient.objects.create(user=self.user, name='in1name')
        in2 = Ingredient.objects.create(user=self.user, name='in2name')
        recipe = Recipe.objects.create(
            title='recipeTitle',
            time_minutes='5',
            price=Decimal('2.5'),
            user=self.user,
        )
        recipe.ingredients.add(in1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filered_ingredients_unique(self):
        """ Test filtered ingredients returns a unique list """
        in1 = Ingredient.objects.create(user=self.user, name='name1')
        Ingredient.objects.create(user=self.user, name='name2')

        recipe1 = Recipe.objects.create(
            title='Sampletitle',
            time_minutes=50,
            price=Decimal('2.5'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Sampletitle2',
            time_minutes=51,
            price=Decimal('3'),
            user=self.user,
        )
        recipe1.ingredients.add(in1)
        recipe2.ingredients.add(in1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)


