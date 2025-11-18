from rest_framework import serializers
from datetime import date
from .models import Booking, GeneralEnquiry, ContactEnquiry

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