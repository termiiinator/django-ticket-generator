import json
import random

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import SUBJECTS, Question, Ticket


def index(request):
    tickets = Ticket.objects.all().order_by('-created_at')
    context = {
        'tickets': tickets,
        'total_tickets': Ticket.objects.count(),
    }
    return render(request, 'tickets/index.html', context)


def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    context = {
        'ticket': ticket,
        'questions': ticket.questions.all(),
    }
    return render(request, 'tickets/ticket.html', context)


def generate_ticket(request):
    questions = Question.objects.all()
    if questions.count() < 5:
        return HttpResponse("Недостаточно вопросов для генерации билета (нужно минимум 5)")

    selected = random.sample(list(questions), 5)
    ticket = Ticket.objects.create()
    ticket.questions.set(selected)

    return render(request, 'tickets/ticket.html', {'ticket': ticket})


def questions_list(request):
    subject_filter = request.GET.get('subject', '')
    questions = Question.objects.all().order_by('subject', 'type')

    if subject_filter:
        questions = questions.filter(subject=subject_filter)

    context = {
        'questions': questions,
        'subjects': SUBJECTS,
        'selected_subject': subject_filter,
    }
    return render(request, 'tickets/questions.html', context)


def add_bulk_questions(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        q_type = request.POST.get('type')
        texts = request.POST.get('texts', '')
        difficulty = request.POST.get('difficulty') or None

        created = 0
        for line in texts.splitlines():
            line = line.strip()
            if line:
                Question.objects.create(
                    subject=subject,
                    type=q_type,
                    text=line,
                    difficulty=int(difficulty) if difficulty else None,
                )
                created += 1

        return redirect('questions_list')

    context = {'subjects': SUBJECTS}
    return render(request, 'tickets/questions.html', context)


@require_POST
def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.delete()
    return redirect('questions_list')


def export_questions(request):
    questions = list(
        Question.objects.values('subject', 'type', 'text', 'difficulty')
    )
    response = HttpResponse(
        json.dumps(questions, ensure_ascii=False, indent=2),
        content_type='application/json',
    )
    response['Content-Disposition'] = 'attachment; filename="questions.json"'
    return response


def import_questions(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            data = json.load(request.FILES['file'])
            created = 0
            for item in data:
                Question.objects.get_or_create(
                    subject=item['subject'],
                    type=item['type'],
                    text=item['text'],
                    defaults={'difficulty': item.get('difficulty')},
                )
                created += 1
            return JsonResponse({'status': 'ok', 'created': created})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return redirect('questions_list')
