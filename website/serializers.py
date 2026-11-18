from rest_framework import serializers
from .models import (
    Department, Programme, AdmissionInfo, FeeInfo,
    Announcement, Event, KnowledgeDocument
)

class DepartmentSerializer(serializers.ModelSerializer):
    programmes_count = serializers.IntegerField(source='programmes.count', read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'head_name', 'programmes_count']


class FeeInfoSerializer(serializers.ModelSerializer):
    formatted_amount = serializers.SerializerMethodField()

    class Meta:
        model = FeeInfo
        fields = ['id', 'fee_type', 'amount', 'currency', 'formatted_amount', 'notes']

    def get_formatted_amount(self, obj):
        if obj.amount is None:
            return "Information not yet available"
        return f"{obj.currency} {obj.amount:,.2f}"


class ProgrammeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    fees = FeeInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Programme
        fields = [
            'id', 'department', 'department_name', 'name', 'level',
            'duration', 'eligibility', 'description', 'is_active', 'fees'
        ]


class AdmissionInfoSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = AdmissionInfo
        fields = ['id', 'category', 'category_display', 'title', 'content', 'deadline_date', 'display_order']


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'body', 'category', 'published_at', 'is_published']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'venue', 'start_datetime', 'end_datetime']


class KnowledgeDocumentSerializer(serializers.ModelSerializer):
    topic_display = serializers.CharField(source='get_topic_display', read_only=True)

    class Meta:
        model = KnowledgeDocument
        fields = ['id', 'topic', 'topic_display', 'title', 'content', 'keywords', 'updated_at']
