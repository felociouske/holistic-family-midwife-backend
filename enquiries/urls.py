from django.urls import path
from .views import (
    BookingCreateView,
    GeneralEnquiryCreateView,
    ContactEnquiryCreateView,
    health_check
)

app_name = 'enquiries'

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('bookings/', BookingCreateView.as_view(), name='booking-create'),
    path('general-enquiries/', GeneralEnquiryCreateView.as_view(), name='general-enquiry-create'),
    path('contact-enquiries/', ContactEnquiryCreateView.as_view(), name='contact-enquiry-create'),
]