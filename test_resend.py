import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from pathlib import Path
import resend

print("=" * 60)
print("🔍 EMAIL SETUP DIAGNOSTIC")
print("=" * 60)

# Check 1: Resend Configuration
print("\n1️⃣ RESEND CONFIGURATION:")
print(f"   API Key exists: {'✅' if settings.RESEND_API_KEY else '❌'}")
if settings.RESEND_API_KEY:
    print(f"   API Key starts with 're_': {'✅' if settings.RESEND_API_KEY.startswith('re_') else '❌'}")
    print(f"   API Key (first 10 chars): {settings.RESEND_API_KEY[:10]}...")
else:
    print("   ❌ No API key found!")

# Check 2: Email Settings
print("\n2️⃣ EMAIL SETTINGS:")
print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print(f"   ADMIN_EMAIL: {settings.ADMIN_EMAIL}")

# Check 3: Template Directory
print("\n3️⃣ TEMPLATE DIRECTORY:")
base_dir = Path(settings.BASE_DIR)
templates_dir = base_dir / 'templates' / 'enquiries'
print(f"   Looking for: {templates_dir}")
print(f"   Directory exists: {'✅' if templates_dir.exists() else '❌'}")

if templates_dir.exists():
    required_templates = [
        'base.html',
        'booking_confirmation.html',
        'booking_admin_notification.html',
        'general_enquiry_notification.html',
        'contact_enquiry_notification.html'
    ]
    
    print("\n   Template files:")
    for template in required_templates:
        template_path = templates_dir / template
        status = '✅' if template_path.exists() else '❌'
        print(f"   {status} {template}")
else:
    print("   ❌ Templates directory not found!")
    print(f"   Create it at: {templates_dir}")

# Check 4: Test Resend Connection
print("\n4️⃣ RESEND CONNECTION TEST:")
try:
    resend.api_key = settings.RESEND_API_KEY
    params = {
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [settings.ADMIN_EMAIL],
        "subject": "🔍 Diagnostic Test - Your Email System Works!",
        "html": "<h1>Success! ✅</h1><p>Your Resend email configuration is working correctly.</p>"
    }
    
    email = resend.Emails.send(params)
    print(f"   ✅ Test email sent successfully!")
    print(f"   Email ID: {email.get('id', 'N/A')}")
    print(f"   Check your inbox: {settings.ADMIN_EMAIL}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check 5: Recent Bookings
print("\n5️⃣ RECENT BOOKINGS:")
try:
    from enquiries.models import Booking
    recent_bookings = Booking.objects.all().order_by('-created_at')[:3]
    
    if recent_bookings:
        print(f"   Found {recent_bookings.count()} recent booking(s):")
        for booking in recent_bookings:
            print(f"   - {booking.get_full_name()} ({booking.email}) - {booking.created_at}")
    else:
        print("   No bookings found in database")
except Exception as e:
    print(f"   ❌ Error accessing bookings: {e}")

print("\n" + "=" * 60)
print("SUMMARY:")
print("=" * 60)

issues = []
if not settings.RESEND_API_KEY:
    issues.append("Missing RESEND_API_KEY in .env")
if not templates_dir.exists():
    issues.append("Missing templates/enquiries/ directory")
if settings.ADMIN_EMAIL == 'admin@example.com':
    issues.append("Update ADMIN_EMAIL in .env to your real email")

if issues:
    print("❌ ISSUES FOUND:")
    for issue in issues:
        print(f"   • {issue}")
else:
    print("✅ Everything looks good! Try making a booking.")

print("=" * 60)