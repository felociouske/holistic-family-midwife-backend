from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking, GeneralEnquiry, ContactEnquiry
from .serializers import BookingSerializer, GeneralEnquirySerializer, ContactEnquirySerializer

class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Send confirmation email
        booking = serializer.instance
        self.send_confirmation_email(booking)
        self.send_admin_notification(booking)
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'status': 'success',
            'message': 'Booking submitted successfully. We will contact you within 24 hours.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    def send_confirmation_email(self, booking):
        subject = f'Booking Confirmation - {booking.service_type}'
        message = f"""
        Dear {booking.get_full_name()},
        
        Thank you for booking with Holistic Family Midwife!
        
        Booking Details:
        - Service: {booking.get_service_type_display()}
        - Preferred Date: {booking.preferred_date}
        - Preferred Time: {booking.preferred_time}
        
        We will review your request and contact you within 24 hours to confirm your appointment.
        
        If you have any questions, please contact us at:
        Phone: +254 797 735 027
        Email: info@holisticfamilymidwife.com
        
        Best regards,
        Holistic Family Midwife Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [booking.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email: {e}")
    
    def send_admin_notification(self, booking):
        subject = f'New Booking Request - {booking.get_full_name()}'
        message = f"""
        New booking request received:
        
        Client: {booking.get_full_name()}
        Email: {booking.email}
        Phone: {booking.phone}
        Service: {booking.get_service_type_display()}
        Date: {booking.preferred_date}
        Time: {booking.preferred_time}
        
        Login to admin panel to review and confirm.
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],  # Send to admin
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending admin notification: {e}")


class GeneralEnquiryCreateView(generics.CreateAPIView):
    queryset = GeneralEnquiry.objects.all()
    serializer_class = GeneralEnquirySerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Send notification
        enquiry = serializer.instance
        self.send_notification(enquiry)
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'status': 'success',
            'message': 'Your message has been sent successfully. We will get back to you soon.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    def send_notification(self, enquiry):
        subject = f'New Enquiry from {enquiry.name}'
        message = f"""
        New general enquiry received:
        
        Name: {enquiry.name}
        Email: {enquiry.email}
        Phone: {enquiry.phone}
        
        Message:
        {enquiry.message}
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending notification: {e}")


class ContactEnquiryCreateView(generics.CreateAPIView):
    queryset = ContactEnquiry.objects.all()
    serializer_class = ContactEnquirySerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Send notification
        enquiry = serializer.instance
        self.send_notification(enquiry)
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'status': 'success',
            'message': 'Your message has been sent successfully. We will respond within 24 hours.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    def send_notification(self, enquiry):
        subject = f'New Contact Form Submission - {enquiry.get_reason_display()}'
        message = f"""
        New contact enquiry received:
        
        Name: {enquiry.name}
        Email: {enquiry.email}
        Phone: {enquiry.phone}
        Reason: {enquiry.get_reason_display()}
        Due Date: {enquiry.due_date if enquiry.due_date else 'N/A'}
        
        Message:
        {enquiry.message}
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending notification: {e}")


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'ok', 'message': 'API is running'})