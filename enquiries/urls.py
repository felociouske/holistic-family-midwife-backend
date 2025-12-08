from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookingCreateView,
    GeneralEnquiryCreateView,
    ContactEnquiryCreateView,
    health_check,
    BlogPostViewSet,
    CategoryViewSet, 
    TagViewSet
)

app_name = 'enquiries'

router = DefaultRouter()
router.register(r'blog/posts', BlogPostViewSet, basename='blogpost')
router.register(r'blog/categories', CategoryViewSet, basename='category')
router.register(r'blog/tags', TagViewSet, basename='tag')

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('bookings/', BookingCreateView.as_view(), name='booking-create'),
    path('general-enquiries/', GeneralEnquiryCreateView.as_view(), name='general-enquiry-create'),
    path('contact-enquiries/', ContactEnquiryCreateView.as_view(), name='contact-enquiry-create'),

    path('', include(router.urls)),
]