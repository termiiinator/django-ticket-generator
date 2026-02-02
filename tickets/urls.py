from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate/', views.generate_ticket, name='generate_ticket'),
    path('questions/', views.questions_list, name='questions_list'),
    path('questions/add-bulk/', views.add_bulk_questions, name='add_bulk_questions'),
    path('questions/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('questions/export/', views.export_questions, name='export_questions'),
    path('questions/import/', views.import_questions, name='import_questions'),
]
