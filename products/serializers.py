from rest_framework import serializers
from .models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ProductImageUploadSerializer(serializers.ModelSerializer):
    """Used for writing — accepts the actual file."""
    class Meta:
        model = ProductImage
        fields = ["id", "product", "image"]

class ProductImageSerializer(serializers.ModelSerializer):
    """Used for reading — returns absolute URL."""
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "image"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None



class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "description", "price", "stock",
            "category", "category_id", "owner", "owner_username",
            "is_approved", "images", "created_at"
        ]
        read_only_fields = ["owner", "is_approved"]