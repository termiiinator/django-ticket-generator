from django.contrib import admin
from .models import Question, TicketCounter


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'type', 'difficulty', 'text_preview', 'created_at')
    list_filter = ('subject', 'type', 'difficulty', 'created_at')
    search_fields = ('text',)
    ordering = ('-created_at',)
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст вопроса'


@admin.register(TicketCounter)
class TicketCounterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'last_number')
    list_filter = ('subject',)
