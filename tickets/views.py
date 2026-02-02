from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Q, Count
import json
import random
from datetime import datetime

from .models import Question, TicketCounter, SUBJECTS

PHYSICS_LEVELS = 5


def index(request):
    """Главная страница - генератор билетов"""
    subjects_data = []
    for subject_code, subject_name in SUBJECTS:
        questions = Question.objects.filter(subject=subject_code)
        
        if subject_code == 'physics':
            # Для физики проверяем наличие вопросов по уровням
            level_counts = {}
            for level in range(1, PHYSICS_LEVELS + 1):
                level_counts[level] = questions.filter(difficulty=level).count()
            
            valid = all(count > 0 for count in level_counts.values())
            message = None if valid else f"Недостаточно вопросов по физике"
        else:
            # Для остальных предметов
            theory_count = questions.filter(type='theory').count()
            practice_count = questions.filter(type='practice').count()
            
            valid = theory_count >= 2 and practice_count >= 3
            message = None if valid else f"Теория: {theory_count}/2, Практика: {practice_count}/3"
        
        subjects_data.append({
            'code': subject_code,
            'name': subject_name,
            'valid': valid,
            'message': message
        })
    
    context = {
        'subjects': subjects_data
    }
    return render(request, 'tickets/index.html', context)


def generate_ticket(request):
    """Генерация билета"""
    if request.method == 'POST':
        subject = request.POST.get('subject')
        
        try:
            # Получаем или создаем счетчик
            counter, created = TicketCounter.objects.get_or_create(subject=subject)
            ticket_number = counter.increment()
            
            if subject == 'physics':
                # Логика для физики
                selected_questions = []
                for level in range(1, PHYSICS_LEVELS + 1):
                    questions = list(Question.objects.filter(
                        subject='physics',
                        difficulty=level
                    ))
                    
                    if not questions:
                        raise ValueError(f"Нет вопросов для уровня {level} по физике")
                    
                    selected_questions.append(random.choice(questions))
                
                context = {
                    'ticket_number': ticket_number,
                    'subject': dict(SUBJECTS).get(subject),
                    'subject_code': subject,
                    'date': datetime.now().strftime('%d.%m.%Y'),
                    'physics_questions': selected_questions,
                    'is_physics': True
                }
            else:
                # Логика для остальных предметов
                theory_questions = list(Question.objects.filter(
                    subject=subject,
                    type='theory'
                ))
                practice_questions = list(Question.objects.filter(
                    subject=subject,
                    type='practice'
                ))
                
                if len(theory_questions) < 2:
                    raise ValueError("Недостаточно теоретических вопросов")
                if len(practice_questions) < 3:
                    raise ValueError("Недостаточно практических заданий")
                
                selected_theory = random.sample(theory_questions, 2)
                selected_practice = random.sample(practice_questions, 3)
                
                context = {
                    'ticket_number': ticket_number,
                    'subject': dict(SUBJECTS).get(subject),
                    'subject_code': subject,
                    'date': datetime.now().strftime('%d.%m.%Y'),
                    'theory_questions': selected_theory,
                    'practice_questions': selected_practice,
                    'is_physics': False
                }
            
            return render(request, 'tickets/ticket.html', context)
            
        except Exception as e:
            messages.error(request, f'Ошибка генерации: {str(e)}')
            return redirect('index')
    
    return redirect('index')


def questions_list(request):
    """Страница управления вопросами"""
    # Фильтры
    subject_filter = request.GET.get('subject', '')
    type_filter = request.GET.get('type', '')
    difficulty_filter = request.GET.get('difficulty', '')
    search = request.GET.get('search', '')
    
    # Базовый запрос
    questions = Question.objects.all()
    
    # Применяем фильтры
    if subject_filter:
        questions = questions.filter(subject=subject_filter)
    if type_filter:
        questions = questions.filter(type=type_filter)
    if difficulty_filter:
        questions = questions.filter(difficulty=int(difficulty_filter))
    if search:
        questions = questions.filter(text__icontains=search)
    
    # Статистика
    stats = {}
    for subject_code, subject_name in SUBJECTS:
        if subject_code == 'physics':
            level_counts = {}
            for level in range(1, PHYSICS_LEVELS + 1):
                count = Question.objects.filter(
                    subject='physics',
                    difficulty=level
                ).count()
                level_counts[level] = count
            stats[subject_code] = {
                'name': subject_name,
                'levels': level_counts
            }
        else:
            theory_count = Question.objects.filter(
                subject=subject_code,
                type='theory'
            ).count()
            practice_count = Question.objects.filter(
                subject=subject_code,
                type='practice'
            ).count()
            stats[subject_code] = {
                'name': subject_name,
                'theory': theory_count,
                'practice': practice_count
            }
    
    context = {
        'questions': questions,
        'subjects': SUBJECTS,
        'stats': stats,
        'physics_levels': range(1, PHYSICS_LEVELS + 1),
        'filters': {
            'subject': subject_filter,
            'type': type_filter,
            'difficulty': difficulty_filter,
            'search': search
        }
    }
    return render(request, 'tickets/questions.html', context)


def add_bulk_questions(request):
    """Массовое добавление вопросов"""
    if request.method == 'POST':
        subject = request.POST.get('subject')
        question_type = request.POST.get('type', 'theory')
        difficulty = request.POST.get('difficulty')
        text = request.POST.get('text', '')
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            messages.error(request, 'Нет корректных строк для импорта')
            return redirect('questions_list')
        
        created_count = 0
        for line in lines:
            question = Question(
                subject=subject,
                type=question_type,
                text=line
            )
            
            if subject == 'physics' and difficulty:
                question.difficulty = int(difficulty)
            
            question.save()
            created_count += 1
        
        messages.success(request, f'Добавлено вопросов: {created_count}')
        return redirect('questions_list')
    
    return redirect('questions_list')


def delete_question(request, question_id):
    """Удаление вопроса"""
    if request.method == 'POST':
        question = get_object_or_404(Question, id=question_id)
        question.delete()
        messages.success(request, 'Вопрос удален')
    
    return redirect('questions_list')


def export_questions(request):
    """Экспорт вопросов в JSON"""
    questions = Question.objects.all()
    
    data = []
    for q in questions:
        item = {
            'id': str(q.id),
            'subject': dict(SUBJECTS).get(q.subject),
            'type': q.type,
            'text': q.text
        }
        if q.difficulty:
            item['difficulty'] = q.difficulty
        data.append(item)
    
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="questions-{datetime.now().strftime("%Y%m%d")}.json"'
    
    return response


def import_questions(request):
    """Импорт вопросов из JSON"""
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']
            data = json.loads(file.read().decode('utf-8'))
            
            # Обратный словарь для поиска кода по названию
            subject_reverse = {name: code for code, name in SUBJECTS}
            
            imported_count = 0
            for item in data:
                subject_name = item.get('subject')
                subject_code = subject_reverse.get(subject_name)
                
                if not subject_code:
                    continue
                
                question = Question(
                    subject=subject_code,
                    type=item.get('type', 'theory'),
                    text=item.get('text', '')
                )
                
                if 'difficulty' in item:
                    question.difficulty = item['difficulty']
                
                question.save()
                imported_count += 1
            
            messages.success(request, f'Импортировано вопросов: {imported_count}')
        except Exception as e:
            messages.error(request, f'Ошибка импорта: {str(e)}')
    
    return redirect('questions_list')
