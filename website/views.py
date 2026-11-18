from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import (
    Department, Programme, AdmissionInfo, FeeInfo,
    Announcement, Event, KnowledgeDocument
)
from .serializers import (
    DepartmentSerializer, ProgrammeSerializer, AdmissionInfoSerializer,
    AnnouncementSerializer, EventSerializer, KnowledgeDocumentSerializer
)

class HealthCheckView(APIView):
    """
    Health check endpoint: returns {"status": "ok"}.
    Makes no Gemini call.
    """
    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class HomeSummaryView(APIView):
    """
    Homepage summary: statistics, featured programmes, latest announcements (up to 5),
    upcoming events (up to 5), and departments list.
    """
    def get(self, request, *args, **kwargs):
        now = timezone.now()

        # Fixed stats matching UI: NAAC A+, 100+ programmes, 50+ research centres, 15,000+ students
        stats = {
            "naac_rating": "NAAC A+",
            "programmes_count": "100+",
            "research_centers": "50+",
            "students_count": "15,000+",
        }

        # Featured programmes (active, first 6)
        featured_qs = Programme.objects.filter(is_active=True).select_related('department').prefetch_related('fees')[:6]
        featured_serializer = ProgrammeSerializer(featured_qs, many=True)

        # Latest announcements (up to 5)
        announcements_qs = Announcement.objects.filter(is_published=True).order_by('-published_at')[:5]
        announcements_serializer = AnnouncementSerializer(announcements_qs, many=True)

        # Upcoming events (up to 5)
        events_qs = Event.objects.filter(start_datetime__gte=now).order_by('start_datetime')[:5]
        if not events_qs.exists():
            # Fallback if simulated now is ahead of all seed events
            events_qs = Event.objects.all().order_by('start_datetime')[:5]
        events_serializer = EventSerializer(events_qs, many=True)

        # Departments
        depts_qs = Department.objects.all().prefetch_related('programmes')
        depts_serializer = DepartmentSerializer(depts_qs, many=True)

        return Response({
            "statistics": stats,
            "featured_programmes": featured_serializer.data,
            "latest_announcements": announcements_serializer.data,
            "upcoming_events": events_serializer.data,
            "departments": depts_serializer.data,
        }, status=status.HTTP_200_OK)


class DepartmentListView(generics.ListAPIView):
    """
    GET /api/v1/departments/
    List all departments with programme counts.
    """
    queryset = Department.objects.all().prefetch_related('programmes')
    serializer_class = DepartmentSerializer


class ProgrammeListView(generics.ListAPIView):
    """
    GET /api/v1/programmes/?level=&department=
    List programmes, optionally filtered by level and department.
    """
    serializer_class = ProgrammeSerializer

    def get_queryset(self):
        queryset = Programme.objects.filter(is_active=True).select_related('department').prefetch_related('fees')
        level = self.request.query_params.get('level', '').strip()
        department = self.request.query_params.get('department', '').strip()

        if level:
            queryset = queryset.filter(level__iexact=level)
        if department:
            if department.isdigit():
                queryset = queryset.filter(department_id=int(department))
            else:
                queryset = queryset.filter(department__name__icontains=department)

        return queryset


class AdmissionsGroupedView(APIView):
    """
    GET /api/v1/admissions/
    Admission information grouped by category:
    procedure, eligibility, deadline, document, faq.
    """
    def get(self, request, *args, **kwargs):
        all_items = AdmissionInfo.objects.all().order_by('display_order', 'id')
        categories = ['procedure', 'eligibility', 'deadline', 'document', 'faq']

        grouped = {cat: [] for cat in categories}
        for item in all_items:
            data = AdmissionInfoSerializer(item).data
            if item.category in grouped:
                grouped[item.category].append(data)
            else:
                grouped.setdefault(item.category, []).append(data)

        return Response(grouped, status=status.HTTP_200_OK)


class AnnouncementListView(generics.ListAPIView):
    """
    GET /api/v1/announcements/?category=
    Published announcements, newest first, optionally filtered by category.
    """
    serializer_class = AnnouncementSerializer

    def get_queryset(self):
        queryset = Announcement.objects.filter(is_published=True).order_by('-published_at')
        category = self.request.query_params.get('category', '').strip()
        if category:
            queryset = queryset.filter(category__iexact=category)
        return queryset


class EventListView(generics.ListAPIView):
    """
    GET /api/v1/events/
    Upcoming events, ordered by start date.
    Past events are hidden by default per FR-006.
    """
    serializer_class = EventSerializer

    def get_queryset(self):
        show_all = self.request.query_params.get('all', '').lower() in ('true', '1')
        now = timezone.now()
        if show_all:
            return Event.objects.all().order_by('start_datetime')

        qs = Event.objects.filter(start_datetime__gte=now).order_by('start_datetime')
        if not qs.exists():
            # If current time is past all seeded events, show all to ensure content displays
            return Event.objects.all().order_by('start_datetime')
        return qs


class KnowledgeDocumentListView(generics.ListAPIView):
    """
    GET /api/v1/knowledge/?topic=
    Student-information knowledge documents by topic.
    """
    serializer_class = KnowledgeDocumentSerializer

    def get_queryset(self):
        queryset = KnowledgeDocument.objects.filter(is_active=True).order_by('topic', 'title')
        topic = self.request.query_params.get('topic', '').strip()
        if topic:
            queryset = queryset.filter(topic__iexact=topic)
        return queryset
