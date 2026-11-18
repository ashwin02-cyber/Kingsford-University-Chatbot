from django.urls import path
from .views import (
    HealthCheckView, HomeSummaryView, DepartmentListView,
    ProgrammeListView, AdmissionsGroupedView, AnnouncementListView,
    EventListView, KnowledgeDocumentListView
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('home/', HomeSummaryView.as_view(), name='home-summary'),
    path('departments/', DepartmentListView.as_view(), name='department-list'),
    path('programmes/', ProgrammeListView.as_view(), name='programme-list'),
    path('admissions/', AdmissionsGroupedView.as_view(), name='admissions-grouped'),
    path('announcements/', AnnouncementListView.as_view(), name='announcement-list'),
    path('events/', EventListView.as_view(), name='event-list'),
    path('knowledge/', KnowledgeDocumentListView.as_view(), name='knowledge-list'),
]
