from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Ticket, Question
import random


def index(request):
    """Main page with ticket list"""
    tickets = Ticket.objects.all().order_by('-created_at')
    context = {
        'tickets': tickets,
        'total_tickets': Ticket.objects.count(),
    }
    return render(request, 'tickets/index.html', context)


def ticket_detail(request, pk):
    """Show individual ticket"""
    ticket = get_object_or_404(Ticket, pk=pk)
    questions = ticket.questions.all()
    context = {
        'ticket': ticket,
        'questions': questions,
    }
    return render(request, 'tickets/ticket.html', context)


def generate_ticket(request):
    """Generate random ticket"""
    questions = Question.objects.all()
    if questions.count() < 5:
        return HttpResponse("Not enough questions to generate a ticket")
    
    selected = random.sample(list(questions), 5)
    ticket = Ticket.objects.create()
    ticket.questions.set(selected)
    
    return render(request, 'tickets/ticket.html', {'ticket': ticket})


def questions_list(request):
    """Show all questions"""
    questions = Question.objects.all().order_by('subject')
    subjects = Question.SUBJECTS
    subject_filter = request.GET.get('subject', '')
    
    if subject_filter:
        questions = questions.filter(subject=subject_filter)
    
    context = {
        'questions': questions,
        'subjects': subjects,
        'selected_subject': subject_filter,
    }
    return render(request, 'tickets/questions.html', context)
