from django.db import models

SUBJECTS = [
    ('analysis', 'Анализ Алгоритмов'),
    ('complex', 'Комплексный Анализ'),
    ('differential', 'Диференциальные уравнения'),
    ('numerical', 'Численные методы'),
    ('physics', 'Физика'),
]

QUESTION_TYPES = [
    ('theory', 'Теория'),
    ('practice', 'Практика'),
]


class Question(models.Model):
    """Модель вопроса для экзаменационного билета"""
    
    subject = models.CharField(
        max_length=50,
        choices=SUBJECTS,
        verbose_name='Предмет'
    )
    type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES,
        verbose_name='Тип вопроса'
    )
    text = models.TextField(verbose_name='Текст вопроса')
    difficulty = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Уровень сложности (для физики)',
        help_text='Используется только для физики (1-5)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['subject', 'type', 'difficulty']

    def __str__(self):
        if self.subject == 'physics' and self.difficulty:
            return f"{self.get_subject_display()} - Уровень {self.difficulty}: {self.text[:50]}"
        return f"{self.get_subject_display()} - {self.get_type_display()}: {self.text[:50]}"


class TicketCounter(models.Model):
    """Модель для хранения счетчиков номеров билетов по предметам"""
    
    subject = models.CharField(
        max_length=50,
        choices=SUBJECTS,
        unique=True,
        verbose_name='Предмет'
    )
    last_number = models.IntegerField(
        default=0,
        verbose_name='Последний номер билета'
    )

    class Meta:
        verbose_name = 'Счетчик билетов'
        verbose_name_plural = 'Счетчики билетов'

    def __str__(self):
        return f"{self.get_subject_display()}: {self.last_number}"

    def increment(self):
        """Увеличить счетчик и вернуть новый номер"""
        self.last_number += 1
        self.save()
        return self.last_number
