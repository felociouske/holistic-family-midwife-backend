import resend
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger('enquiries.email_service')

class EmailService:
    """Service class for handling all email operations using Resend"""
    
    @staticmethod
    def send_email(subject, template_name, context, recipient_list):
        """
        Generic method to send HTML emails via Resend
        
        Args:
            subject: Email subject line
            template_name: Path to HTML template
            context: Dictionary of context variables for template
            recipient_list: List of recipient email addresses
        """
        try:
            # Render HTML content
            html_content = render_to_string(template_name, context)
            
            logger.info(f"Attempting to send email: {subject} to {recipient_list}")
            
            # Send email via Resend
            params = {
                "from": settings.DEFAULT_FROM_EMAIL,
                "to": recipient_list,
                "subject": subject,
                "html": html_content,
            }
            
            email = resend.Emails.send(params)
            
            logger.info(f"✅ Email sent successfully: {subject} to {recipient_list}")
            logger.info(f"Resend Email ID: {email.get('id', 'N/A')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending email: {subject} - {str(e)}")
            logger.exception("Full traceback:")
            return False
    
    @classmethod
    def send_booking_confirmation(cls, booking):
        """Send booking confirmation email to client"""
        subject = f'Booking Confirmation - {booking.get_service_type_display()}'
        template_name = 'enquiries/booking_confirmation.html'
        
        context = {
            'booking': booking,
            'client_name': booking.get_full_name(),
            'service': booking.get_service_type_display(),
            'preferred_date': booking.preferred_date,
            'preferred_time': booking.preferred_time,
            'phone': '+254 797 735 027',
            'email': 'info@holisticfamilymidwife.com',
            'website': 'https://holisticfamilymidwife.com',
        }
        
        logger.info(f"Sending booking confirmation to: {booking.email}")
        return cls.send_email(
            subject=subject,
            template_name=template_name,
            context=context,
            recipient_list=[booking.email]
        )
    
    @classmethod
    def send_booking_admin_notification(cls, booking):
        """Send booking notification to admin"""
        subject = f'New Booking Request - {booking.get_full_name()}'
        template_name = 'enquiries/booking_admin_notification.html'
        
        context = {
            'booking': booking,
            'client_name': booking.get_full_name(),
            'client_email': booking.email,
            'client_phone': booking.phone,
            'service': booking.get_service_type_display(),
            'preferred_date': booking.preferred_date,
            'preferred_time': booking.preferred_time,
            'additional_info': booking.additional_notes if booking.additional_notes else 'None provided',
        }
        
        logger.info(f"Sending admin notification to: {settings.ADMIN_EMAIL}")
        return cls.send_email(
            subject=subject,
            template_name=template_name,
            context=context,
            recipient_list=[settings.ADMIN_EMAIL]
        )
    
    @classmethod
    def send_general_enquiry_notification(cls, enquiry):
        """Send general enquiry notification to admin"""
        subject = f'New General Enquiry - {enquiry.name}'
        template_name = 'enquiries/general_enquiry_notification.html'
        
        context = {
            'enquiry': enquiry,
            'name': enquiry.name,
            'email': enquiry.email,
            'phone': enquiry.phone,
            'message': enquiry.message,
        }
        
        logger.info(f"Sending general enquiry notification to: {settings.ADMIN_EMAIL}")
        return cls.send_email(
            subject=subject,
            template_name=template_name,
            context=context,
            recipient_list=[settings.ADMIN_EMAIL]
        )
    
    @classmethod
    def send_contact_enquiry_notification(cls, enquiry):
        """Send contact enquiry notification to admin"""
        subject = f'New Contact Enquiry - {enquiry.get_reason_display()}'
        template_name = 'enquiries/contact_enquiry_notification.html'
        
        context = {
            'enquiry': enquiry,
            'name': enquiry.name,
            'email': enquiry.email,
            'phone': enquiry.phone,
            'reason': enquiry.get_reason_display(),
            'due_date': enquiry.due_date if enquiry.due_date else 'N/A',
            'message': enquiry.message,
        }
        
        logger.info(f"Sending contact enquiry notification to: {settings.ADMIN_EMAIL}")
        return cls.send_email(
            subject=subject,
            template_name=template_name,
            context=context,
            recipient_list=[settings.ADMIN_EMAIL]
        )