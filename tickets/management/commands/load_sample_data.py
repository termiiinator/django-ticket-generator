from django.core.management.base import BaseCommand
from tickets.models import Question


class Command(BaseCommand):
    help = 'Загрузка тестовых вопросов в базу данных'

    def handle(self, *args, **options):
        # Математика
        math_theory = [
            "Сформулируйте теорему Пифагора и докажите её",
            "Дайте определение производной функции. Геометрический смысл производной",
            "Определение первообразной. Основные свойства неопределённого интеграла",
            "Понятие предела функции. Основные теоремы о пределах",
            "Определение матрицы. Операции над матрицами",
        ]
        
        math_practice = [
            "Решите уравнение: x² - 5x + 6 = 0",
            "Найдите производную функции: f(x) = 3x³ - 2x² + 5x - 7",
            "Вычислите определённый интеграл: ∫[0,2] (x² + 1)dx",
            "Найдите предел: lim(x→2) (x² - 4)/(x - 2)",
            "Решите систему уравнений методом Крамера: 2x + y = 5, x - y = 1",
        ]
        
        # Физика (5 уровней)
        physics_l1 = [
            "Что такое сила?",
            "Определите понятие массы",
            "Что называется скоростью?",
        ]
        
        physics_l2 = [
            "Сформулируйте второй закон Ньютона",
            "Что такое кинетическая энергия?",
            "Определите импульс тела",
        ]
        
        physics_l3 = [
            "Выведите формулу центростремительного ускорения",
            "Объясните закон сохранения энергии",
            "Что такое момент силы?",
        ]
        
        physics_l4 = [
            "Решите задачу на движение тела под углом к горизонту",
            "Рассчитайте момент инерции диска",
            "Выведите уравнение колебаний математического маятника",
        ]
        
        physics_l5 = [
            "Докажите теорему Штейнера",
            "Решите систему связанных тел на наклонной плоскости",
            "Выведите уравнение движения в неинерциальной системе отсчёта",
        ]
        
        created = 0
        
        # Добавляем вопросы по математике
        for text in math_theory:
            Question.objects.create(
                subject='analysis',
                type='theory',
                text=text
            )
            created += 1
        
        for text in math_practice:
            Question.objects.create(
                subject='analysis',
                type='practice',
                text=text
            )
            created += 1
        
        # Добавляем вопросы по физике
        for text in physics_l1:
            Question.objects.create(
                subject='physics',
                type='theory',
                text=text,
                difficulty=1
            )
            created += 1
        
        for text in physics_l2:
            Question.objects.create(
                subject='physics',
                type='theory',
                text=text,
                difficulty=2
            )
            created += 1
        
        for text in physics_l3:
            Question.objects.create(
                subject='physics',
                type='theory',
                text=text,
                difficulty=3
            )
            created += 1
        
        for text in physics_l4:
            Question.objects.create(
                subject='physics',
                type='theory',
                text=text,
                difficulty=4
            )
            created += 1
        
        for text in physics_l5:
            Question.objects.create(
                subject='physics',
                type='theory',
                text=text,
                difficulty=5
            )
            created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Успешно загружено {created} вопросов')
        )
