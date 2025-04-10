from rest_framework import serializers
from .models import Recipe, Category, Ingredient, RecipeIngredient, Review, Favorite
from users.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'quantity', 'unit', 'notes']

class ReviewSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'author', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True
    )
    reviews = ReviewSerializer(many=True, read_only=True)
    is_favorite = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'ingredients', 'instructions',
            'categories', 'preparation_time', 'cooking_time', 'servings',
            'difficulty', 'author', 'image', 'created_at', 'updated_at',
            'reviews', 'is_favorite', 'average_rating'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all()
    )
    ingredients = serializers.JSONField(write_only=True)

    class Meta:
        model = Recipe
        fields = [
            'title', 'description', 'ingredients', 'instructions',
            'categories', 'preparation_time', 'cooking_time', 'servings',
            'difficulty', 'image'
        ]

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        categories = validated_data.pop('categories', [])
        
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        
        recipe.categories.set(categories)
        
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get_or_create(
                name=ingredient_data['name']
            )[0]
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                quantity=ingredient_data.get('quantity', ''),
                unit=ingredient_data.get('unit', ''),
                notes=ingredient_data.get('notes', '')
            )
        
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        categories = validated_data.pop('categories', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if categories is not None:
            instance.categories.set(categories)
        
        if ingredients_data is not None:
            # Clear existing ingredients
            instance.recipe_ingredients.all().delete()
            
            # Add new ingredients
            for ingredient_data in ingredients_data:
                ingredient = Ingredient.objects.get_or_create(
                    name=ingredient_data['name']
                )[0]
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    quantity=ingredient_data.get('quantity', ''),
                    unit=ingredient_data.get('unit', ''),
                    notes=ingredient_data.get('notes', '')
                )
        
        instance.save()
        return instance

class FavoriteSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'recipe', 'created_at']
        read_only_fields = ['id', 'created_at']

class FavoriteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['recipe']
    
    def create(self, validated_data):
        favorite, created = Favorite.objects.get_or_create(
            user=self.context['request'].user,
            recipe=validated_data['recipe']
        )
        return favorite