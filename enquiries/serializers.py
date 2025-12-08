from rest_framework import serializers
from datetime import date
from .models import Booking, GeneralEnquiry, ContactEnquiry, BlogPost, Category, Tag, Author

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'status')
    
    def validate_phone(self, value):
        # Clean phone number
        value = value.strip().replace(' ', '').replace('-', '')
        if not value.startswith('+254') and not value.startswith('254') and not value.startswith('0'):
            raise serializers.ValidationError("Phone number must be a valid Kenyan number")
        return value
    
    def validate(self, data):
        if data.get('preferred_date') and data['preferred_date'] < date.today():
            raise serializers.ValidationError({'preferred_date': 'Date cannot be in the past'})
        return data


class GeneralEnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralEnquiry
        fields = '__all__'
        read_only_fields = ('created_at', 'is_read')


class ContactEnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactEnquiry
        fields = '__all__'
        read_only_fields = ('created_at', 'is_read')

class AuthorSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['id', 'name', 'bio', 'avatar']

    def get_avatar(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
        return None

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

class BlogPostListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    featured_image = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image',
            'author', 'category', 'tags', 'published_date',
            'reading_time', 'is_featured', 'views_count'
        ]

    def get_featured_image(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
        return None

class BlogPostDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    featured_image = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'featured_image',
            'author', 'category', 'tags', 'published_date', 'reading_time',
            'is_featured', 'views_count', 'created_at', 'updated_at'
        ]

    def get_featured_image(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
        return None
