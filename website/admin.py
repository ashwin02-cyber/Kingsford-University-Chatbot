from django.contrib import admin
from .models import Department, Programme, AdmissionInfo, FeeInfo, Announcement, Event, KnowledgeDocument

admin.site.site_header = "Kingsford University Administration (Sample Data System)"
admin.site.site_title = "Kingsford Admin Portal"
admin.site.index_title = "Institutional Knowledge & Content Management [Note: All records are Sample Data]"

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'head_name')
    search_fields = ('name', 'description', 'head_name')

@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'level', 'duration', 'is_active')
    list_filter = ('level', 'department', 'is_active')
    search_fields = ('name', 'description', 'eligibility')

@admin.register(AdmissionInfo)
class AdmissionInfoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'deadline_date', 'display_order')
    list_filter = ('category',)
    search_fields = ('title', 'content')
    ordering = ('display_order', 'id')

@admin.register(FeeInfo)
class FeeInfoAdmin(admin.ModelAdmin):
    list_display = ('fee_type', 'programme', 'amount', 'currency')
    list_filter = ('currency', 'fee_type')
    search_fields = ('fee_type', 'notes')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published_at', 'is_published')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'body')
    date_hierarchy = 'published_at'

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'venue', 'start_datetime', 'end_datetime')
    search_fields = ('title', 'venue', 'description')
    date_hierarchy = 'start_datetime'

@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'is_active', 'updated_at')
    list_filter = ('topic', 'is_active')
    search_fields = ('title', 'content', 'keywords')
