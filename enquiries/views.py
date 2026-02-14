from rest_framework import status, generics, viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.conf import settings
from .models import Booking, GeneralEnquiry, ContactEnquiry, BlogPost, Category, Tag
from .serializers import BookingSerializer, GeneralEnquirySerializer, ContactEnquirySerializer, BlogPostListSerializer, BlogPostDetailSerializer, TagSerializer, CategorySerializer
from .email_service import EmailService

class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Send confirmation emails using EmailService
        booking = serializer.instance
        EmailService.send_booking_confirmation(booking)
        EmailService.send_booking_admin_notification(booking)
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'status': 'success',
            'message': 'Booking submitted successfully. We will contact you within 24 hours.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)


class GeneralEnquiryCreateView(generics.CreateAPIView):
    queryset = GeneralEnquiry.objects.all()
    serializer_class = GeneralEnquirySerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Send notification using EmailService
        enquiry = serializer.instance
        EmailService.send_general_enquiry_notification(enquiry)
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'status': 'success',
            'message': 'Your message has been sent successfully. We will get back to you soon.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)


class ContactEnquiryCreateView(generics.CreateAPIView):
    queryset = ContactEnquiry.objects.all()
    serializer_class = ContactEnquirySerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Send notification using EmailService
        enquiry = serializer.instance
        EmailService.send_contact_enquiry_notification(enquiry)
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'status': 'success',
            'message': 'Your message has been sent successfully. We will respond within 24 hours.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'ok', 'message': 'API is running'})


# ==================== BLOG VIEWS - UNCHANGED ====================

class BlogPostPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 50

class BlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BlogPost.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
    pagination_class = BlogPostPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'excerpt', 'content', 'tags__name']
    ordering_fields = ['published_date', 'views_count', 'title']
    ordering = ['-published_date']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BlogPostDetailSerializer
        return BlogPostListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured posts"""
        featured_posts = self.queryset.filter(is_featured=True)[:3]
        serializer = self.get_serializer(featured_posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Filter posts by category slug"""
        category_slug = request.query_params.get('category', None)
        if category_slug:
            posts = self.queryset.filter(category__slug=category_slug)
            page = self.paginate_queryset(posts)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(posts, many=True)
            return Response(serializer.data)
        return Response({'error': 'Category parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def by_tag(self, request):
        """Filter posts by tag slug"""
        tag_slug = request.query_params.get('tag', None)
        if tag_slug:
            posts = self.queryset.filter(tags__slug=tag_slug)
            page = self.paginate_queryset(posts)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(posts, many=True)
            return Response(serializer.data)
        return Response({'error': 'Tag parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search with multiple filters"""
        query = request.query_params.get('q', '')
        category = request.query_params.get('category', None)
        
        posts = self.queryset
        
        if query:
            posts = posts.filter(
                Q(title__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()
        
        if category and category != 'all':
            posts = posts.filter(category__slug=category)
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'