from django.contrib import admin
from django.contrib.admin import TabularInline

from apps.models import Category, Product, ProductImage, User


# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    pass
