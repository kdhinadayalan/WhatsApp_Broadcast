from rest_framework import serializers
from .models import Contact, ContactGroup

class ContactSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = Contact
        fields = '__all__'

class ContactBulkImportSerializer(serializers.Serializer):
    contacts = serializers.ListField(child=serializers.DictField())

class ContactGroupSerializer(serializers.ModelSerializer):
    member_count = serializers.ReadOnlyField()
    members = ContactSerializer(many=True, read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(), many=True, write_only=True, required=False, source='members'
    )
    class Meta:
        model = ContactGroup
        fields = ['id', 'name', 'description', 'group_type', 'member_count', 'members', 'member_ids', 'created_at']

class ContactGroupListSerializer(serializers.ModelSerializer):
    member_count = serializers.ReadOnlyField()
    class Meta:
        model = ContactGroup
        fields = ['id', 'name', 'description', 'group_type', 'member_count', 'created_at']
