from rest_framework import serializers
from .models import Broadcast, BroadcastRecipient, AuditLog
from contacts.serializers import ContactGroupListSerializer
from wa_templates.serializers import MessageTemplateSerializer
from contacts.models import ContactGroup

class BroadcastRecipientSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    contact_phone = serializers.CharField(source='contact.phone_number', read_only=True)
    contact_role = serializers.CharField(source='contact.role', read_only=True)

    class Meta:
        model = BroadcastRecipient
        fields = ['id', 'contact_name', 'contact_phone', 'contact_role', 'status',
                  'error_message', 'sent_at', 'delivered_at', 'read_at']

class BroadcastListSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    delivery_rate = serializers.ReadOnlyField()
    group_names = serializers.SerializerMethodField()

    class Meta:
        model = Broadcast
        fields = ['id', 'title', 'template_name', 'status', 'total_recipients',
                  'sent_count', 'delivered_count', 'read_count', 'failed_count',
                  'delivery_rate', 'group_names', 'scheduled_at', 'started_at',
                  'completed_at', 'created_at']

    def get_group_names(self, obj):
        return list(obj.groups.values_list('name', flat=True))

class BroadcastCreateSerializer(serializers.ModelSerializer):
    group_ids = serializers.PrimaryKeyRelatedField(
        queryset=ContactGroup.objects.all(),
        many=True, write_only=True
    )

    class Meta:
        model = Broadcast
        fields = ['id', 'title', 'template', 'template_params', 'group_ids', 'scheduled_at']

    def create(self, validated_data):
        groups = validated_data.pop('group_ids', [])
        broadcast = Broadcast.objects.create(**validated_data)
        broadcast.groups.set(groups)
        return broadcast

class BroadcastDetailSerializer(serializers.ModelSerializer):
    template = MessageTemplateSerializer(read_only=True)
    groups = ContactGroupListSerializer(many=True, read_only=True)
    delivery_rate = serializers.ReadOnlyField()

    class Meta:
        model = Broadcast
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'
