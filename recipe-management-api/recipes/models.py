
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Category(models.Model):
    name = models.CharField(_('name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['name']

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(_('name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('ingredient')
        verbose_name_plural = _('ingredients')
        ordering = ['name']

    def __str__(self):
        return self.name

class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ('E', _('Easy')),
        ('M', _('Medium')),
        ('H', _('Hard')),
    ]

    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'))
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name=_('ingredients')
    )
    instructions = models.TextField(_('instructions'))
    categories = models.ManyToManyField(Category, verbose_name=_('categories'))
    preparation_time = models.PositiveIntegerField(_('preparation time (minutes)'))
    cooking_time = models.PositiveIntegerField(_('cooking time (minutes)'))
    servings = models.PositiveIntegerField(_('servings'))
    difficulty = models.CharField(
        _('difficulty'),
        max_length=1,
        choices=DIFFICULTY_CHOICES,
        default='M'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=_('author')
    )
    image = models.ImageField(
        _('image'),
        upload_to='recipe_images/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('recipe')
        verbose_name_plural = _('recipes')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name=_('recipe')
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name=_('ingredient')
    )
    quantity = models.CharField(_('quantity'), max_length=50)
    unit = models.CharField(_('unit'), max_length=50, blank=True)
    notes = models.CharField(_('notes'), max_length=200, blank=True)

    class Meta:
        verbose_name = _('recipe ingredient')
        verbose_name_plural = _('recipe ingredients')
        unique_together = ['recipe', 'ingredient']

    def __str__(self):
        return f"{self.quantity} {self.unit} {self.ingredient.name}"

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('recipe')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('author')
    )
    rating = models.PositiveSmallIntegerField(
        _('rating'),
        choices=RATING_CHOICES
    )
    comment = models.TextField(_('comment'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('review')
        verbose_name_plural = _('reviews')
        ordering = ['-created_at']
        unique_together = ['recipe', 'author']

    def __str__(self):
        return f"{self.rating} stars by {self.author.username} for {self.recipe.title}"

class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=_('user')
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=_('recipe')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('favorite')
        verbose_name_plural = _('favorites')
        unique_together = ['user', 'recipe']

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.recipe.title}"