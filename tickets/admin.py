from django.contrib import admin
from .models import Ticket, Question, TicketCounter


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'subject', 'type', 'difficulty', 'created_at']
    list_filter = ['subject', 'type', 'difficulty']
    search_fields = ['text']
    ordering = ['-created_at']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'get_question_count']
    list_filter = ['created_at']
    readonly_fields = ['created_at']

    def get_question_count(self, obj):
        return obj.questions.count()

    get_question_count.short_description = 'Вопросов'


@admin.register(TicketCounter)
class TicketCounterAdmin(admin.ModelAdmin):
    list_display = ['subject', 'last_number']
