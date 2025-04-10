from django.urls import path
from .views import (
    RecipeListView, RecipeDetailView,
    CategoryListView, IngredientListView,
    RecipeByCategoryView, RecipeByIngredientView,
    ReviewCreateView, FavoriteListView, FavoriteDetailView,
    TopRatedRecipesView, PopularRecipesView
)

urlpatterns = [
    # Recipes
    path('', RecipeListView.as_view(), name='recipe-list'),
    path('<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    
    # Categories and Ingredients
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('ingredients/', IngredientListView.as_view(), name='ingredient-list'),
    
    # Filtering
    path('category/<int:category_id>/', RecipeByCategoryView.as_view(), name='recipe-by-category'),
    path('ingredient/<int:ingredient_id>/', RecipeByIngredientView.as_view(), name='recipe-by-ingredient'),
    
    # Reviews
    path('<int:recipe_id>/reviews/', ReviewCreateView.as_view(), name='review-create'),
    
    # Favorites
    path('favorites/', FavoriteListView.as_view(), name='favorite-list'),
    path('favorites/<int:recipe_id>/', FavoriteDetailView.as_view(), name='favorite-detail'),
    
    # Special listings
    path('top-rated/', TopRatedRecipesView.as_view(), name='top-rated-recipes'),
    path('popular/', PopularRecipesView.as_view(), name='popular-recipes'),
]