from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Q
from .models import Recipe, Category, Ingredient, Review, Favorite
from .serializers import (
    RecipeSerializer, RecipeCreateUpdateSerializer,
    CategorySerializer, IngredientSerializer,
    ReviewSerializer, FavoriteSerializer, FavoriteCreateSerializer
)

class RecipeListView(generics.ListCreateAPIView):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categories', 'difficulty']
    search_fields = ['title', 'description', 'ingredients__name', 'categories__name']
    ordering_fields = ['preparation_time', 'cooking_time', 'servings', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class RecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all()
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {"detail": "You do not have permission to delete this recipe."},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class IngredientListView(generics.ListAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class RecipeByCategoryView(generics.ListAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Recipe.objects.filter(categories__id=category_id)

class RecipeByIngredientView(generics.ListAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        ingredient_id = self.kwargs['ingredient_id']
        return Recipe.objects.filter(ingredients__id=ingredient_id)

class ReviewCreateView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        recipe_id = self.kwargs['recipe_id']
        recipe = Recipe.objects.get(id=recipe_id)
        
        # Check if user already reviewed this recipe
        if Review.objects.filter(recipe=recipe, author=self.request.user).exists():
            raise serializers.ValidationError({"detail": "You have already reviewed this recipe."})
        
        serializer.save(author=self.request.user, recipe=recipe)

class FavoriteListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FavoriteCreateSerializer
        return FavoriteSerializer

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FavoriteDetailView(generics.DestroyAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'recipe_id'

    def get_object(self):
        recipe_id = self.kwargs['recipe_id']
        return Favorite.objects.get(user=self.request.user, recipe_id=recipe_id)

class TopRatedRecipesView(generics.ListAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Recipe.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).filter(
            avg_rating__isnull=False
        ).order_by('-avg_rating')[:10]

class PopularRecipesView(generics.ListAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Recipe.objects.annotate(
            favorite_count=models.Count('favorites')
        ).filter(
            favorite_count__gt=0
        ).order_by('-favorite_count')[:10]