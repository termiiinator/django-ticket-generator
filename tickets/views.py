import json
import random
from datetime import date

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import SUBJECTS, Question, Ticket, TicketCounter


def index(request):
    subjects = []
    for code, name in SUBJECTS:
        if code == 'physics':
            counts = {i: Question.objects.filter(subject='physics', difficulty=i).count() for i in range(1, 6)}
            valid = all(c >= 1 for c in counts.values())
            missing = [str(i) for i, c in counts.items() if c < 1]
            message = f"Нужен хотя бы 1 вопрос уровней: {', '.join(missing)}" if missing else ''
        else:
            theory = Question.objects.filter(subject=code, type='theory').count()
            practice = Question.objects.filter(subject=code, type='practice').count()
            valid = theory >= 2 and practice >= 3
            parts = []
            if theory < 2:
                parts.append(f"теория: {theory}/2")
            if practice < 3:
                parts.append(f"практика: {practice}/3")
            message = ("Нужно: " + ", ".join(parts)) if parts else ''
        subjects.append({'name': name, 'code': code, 'valid': valid, 'message': message})

    return render(request, 'tickets/index.html', {'subjects': subjects})


def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    return render(request, 'tickets/ticket.html', {
        'ticket': ticket,
        'questions': ticket.questions.all(),
    })


def generate_ticket(request):
    subject_code = request.POST.get('subject') if request.method == 'POST' else request.GET.get('subject')
    if not subject_code:
        return redirect('index')

    subject_display = dict(SUBJECTS).get(subject_code, subject_code)

    if subject_code == 'physics':
        selected = []
        for level in range(1, 6):
            qs = list(Question.objects.filter(subject='physics', difficulty=level))
            if not qs:
                return HttpResponse(f"Недостаточно вопросов физики уровня {level}")
            selected.append(random.choice(qs))
        theory_questions, practice_questions = [], []
        physics_questions = selected
    else:
        theory_qs = list(Question.objects.filter(subject=subject_code, type='theory'))
        practice_qs = list(Question.objects.filter(subject=subject_code, type='practice'))
        if len(theory_qs) < 2 or len(practice_qs) < 3:
            return HttpResponse("Недостаточно вопросов для генерации билета")
        theory_questions = random.sample(theory_qs, 2)
        practice_questions = random.sample(practice_qs, 3)
        selected = theory_questions + practice_questions
        physics_questions = []

    ticket = Ticket.objects.create()
    ticket.questions.set(selected)

    counter, _ = TicketCounter.objects.get_or_create(subject=subject_code)
    ticket_number = counter.increment()

    return render(request, 'tickets/ticket.html', {
        'ticket': ticket,
        'subject': subject_display,
        'subject_code': subject_code,
        'ticket_number': ticket_number,
        'is_physics': subject_code == 'physics',
        'physics_questions': physics_questions,
        'theory_questions': theory_questions,
        'practice_questions': practice_questions,
        'date': date.today().strftime('%d.%m.%Y'),
    })


def questions_list(request):
    subject_filter = request.GET.get('subject', '')
    type_filter = request.GET.get('type', '')
    difficulty_filter = request.GET.get('difficulty', '')
    search_filter = request.GET.get('search', '')

    questions = Question.objects.all().order_by('subject', 'type', 'difficulty')
    if subject_filter:
        questions = questions.filter(subject=subject_filter)
    if type_filter:
        questions = questions.filter(type=type_filter)
    if difficulty_filter:
        questions = questions.filter(difficulty=difficulty_filter)
    if search_filter:
        questions = questions.filter(text__icontains=search_filter)

    return render(request, 'tickets/questions.html', {
        'questions': questions,
        'subjects': SUBJECTS,
        'physics_levels': range(1, 6),
        'filters': {
            'subject': subject_filter,
            'type': type_filter,
            'difficulty': difficulty_filter,
            'search': search_filter,
        },
    })


def add_bulk_questions(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        q_type = request.POST.get('type')
        texts = request.POST.get('text', '')
        difficulty = request.POST.get('difficulty') or None
        for line in texts.splitlines():
            line = line.strip()
            if line:
                Question.objects.create(
                    subject=subject,
                    type=q_type,
                    text=line,
                    difficulty=int(difficulty) if difficulty else None,
                )
        return redirect('questions_list')

    return render(request, 'tickets/questions.html', {
        'subjects': SUBJECTS,
        'physics_levels': range(1, 6),
        'questions': Question.objects.none(),
        'filters': {},
    })


@require_POST
def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.delete()
    return redirect('questions_list')


def export_questions(request):
    questions = list(Question.objects.values('subject', 'type', 'text', 'difficulty'))
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
                _, was_created = Question.objects.get_or_create(
                    subject=item['subject'],
                    type=item['type'],
                    text=item['text'],
                    defaults={'difficulty': item.get('difficulty')},
                )
                if was_created:
                    created += 1
            return JsonResponse({'status': 'ok', 'created': created})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return redirect('questions_list')
