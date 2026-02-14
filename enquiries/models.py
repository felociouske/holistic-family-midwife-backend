from django.db import models
from django.core.validators import RegexValidator
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone


class Booking(models.Model):
    SERVICE_CHOICES = [
        ('antenatal', 'Antenatal Care & Follow-Up'),
        ('consultations', 'Consultations'),
        ('partner_health', 'Partner Health Support'),
        ('postpartum', 'Postpartum Care & Follow-Up'),
        ('preconception', 'Preconception Care'),
        ('labor_prep', 'Preparation for Labor & Delivery'),
        ('teenage', 'Teenage Empowerment & Reproductive Education'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    phone_regex = RegexValidator(
        regex=r'^\+?254?\d{9,12}$',
        message="Phone number must be in format: '+254700000000'"
    )

    #PERSONAL INFORMATION
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(validators=[phone_regex], max_length=15)
    address = models.TextField()

    #appointment details
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    preferred_date = models.DateField()
    preferred_time = models.TimeField()

    #medical information
    due_date = models.DateField(null=True, blank=True)
    weeks_pregnant = models.IntegerField(null=True, blank=True)
    previous_pregnancies = models.CharField(max_length=255, blank=True)
    medical_conditions = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)

    #emergency contact
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=15)

    #addational
    additional_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    #metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.service_type} ({self.preferred_date})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class GeneralEnquiry(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    message = models.TextField()

    #metadata
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'General Enquiry'
        verbose_name_plural = 'General Enquiries'
    
    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}" 

class ContactEnquiry(models.Model):
    REASON_CHOICES = [
        ('new-patient', 'New Patient Consultation'),
        ('prenatal', 'Prenatal Care Question'),
        ('postpartum', 'Postpartum Support'),
        ('general', 'General Inquiry'),
    ]

    #contact information
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    due_date = models.DateField(null=True, blank=True)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    message = models.TextField()   

    #metadata
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Enquiry'
        verbose_name_plural = 'Contact Enquiries'
    
    def __str__(self):
        return f"{self.name} - {self.get_reason_display()}"
      

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_profile')
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='authors/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    excerpt = models.TextField(max_length=300, help_text="Brief summary of the post")
    content = RichTextUploadingField()
    featured_image = models.ImageField(upload_to='blog/featured/', blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    reading_time = models.IntegerField(default=5, help_text="Estimated reading time in minutes")
    views_count = models.IntegerField(default=0)
    
    published_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_date', '-created_at']
        indexes = [
            models.Index(fields=['-published_date']),
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-set published_date when status changes to published
        if self.status == 'published' and not self.published_date:
            self.published_date = timezone.now()
        
        # Auto-calculate reading time based on content
        if self.content:
            word_count = len(self.content.split())
            self.reading_time = max(1, round(word_count / 200))  # Average reading speed: 200 words/min
        
        super().save(*args, **kwargs)

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])