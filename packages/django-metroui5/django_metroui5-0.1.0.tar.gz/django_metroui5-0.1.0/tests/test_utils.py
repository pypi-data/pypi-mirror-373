"""
Утилиты для тестирования django-metroui5
"""
import pytest
from django import forms
from django.forms import formset_factory
from django.test import override_settings
from django.utils.safestring import mark_safe


class TestFormBuilder:
    """Построитель тестовых форм"""

    @staticmethod
    def create_simple_form():
        """Создание простой формы"""
        class SimpleForm(forms.Form):
            name = forms.CharField(max_length=100)
            email = forms.EmailField()
            message = forms.CharField(widget=forms.Textarea)
        
        return SimpleForm

    @staticmethod
    def create_form_with_choices():
        """Создание формы с выбором"""
        class ChoiceForm(forms.Form):
            category = forms.ChoiceField(
                choices=[
                    ('option1', 'Опция 1'),
                    ('option2', 'Опция 2'),
                    ('option3', 'Опция 3')
                ]
            )
            multiple_choice = forms.MultipleChoiceField(
                choices=[
                    ('choice1', 'Выбор 1'),
                    ('choice2', 'Выбор 2'),
                    ('choice3', 'Выбор 3')
                ]
            )
        
        return ChoiceForm

    @staticmethod
    def create_form_with_widgets():
        """Создание формы с различными виджетами"""
        class WidgetForm(forms.Form):
            text_input = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
            password = forms.CharField(widget=forms.PasswordInput())
            hidden = forms.CharField(widget=forms.HiddenInput())
            file = forms.FileField()
            image = forms.ImageField()
            date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
            time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
            datetime = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
            number = forms.IntegerField(widget=forms.NumberInput())
            url = forms.URLField(widget=forms.URLInput())
            email = forms.EmailField(widget=forms.EmailInput())
            tel = forms.CharField(widget=forms.TextInput(attrs={'type': 'tel'}))
            search = forms.CharField(widget=forms.TextInput(attrs={'type': 'search'}))
            range_input = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'range', 'min': 0, 'max': 100}))
            color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))
        
        return WidgetForm

    @staticmethod
    def create_form_with_validation():
        """Создание формы с валидацией"""
        class ValidationForm(forms.Form):
            required_field = forms.CharField(required=True)
            min_length_field = forms.CharField(min_length=5)
            max_length_field = forms.CharField(max_length=10)
            regex_field = forms.RegexField(regex=r'^[A-Za-z]+$')
            email_field = forms.EmailField()
            url_field = forms.URLField()
            integer_field = forms.IntegerField(min_value=0, max_value=100)
            decimal_field = forms.DecimalField(max_digits=5, decimal_places=2)
            date_field = forms.DateField()
            time_field = forms.TimeField()
            datetime_field = forms.DateTimeField()
            
            def clean(self):
                cleaned_data = super().clean()
                if cleaned_data.get('required_field') == 'error':
                    raise forms.ValidationError("Общая ошибка формы")
                return cleaned_data
        
        return ValidationForm


class TestDataBuilder:
    """Построитель тестовых данных"""

    @staticmethod
    def create_form_data():
        """Создание данных для формы"""
        return {
            'name': 'Тестовый пользователь',
            'email': 'test@example.com',
            'message': 'Тестовое сообщение для проверки функциональности',
            'category': 'option1',
            'multiple_choice': ['choice1', 'choice2'],
            'required_field': 'Тестовое значение',
            'min_length_field': 'Пять символов',
            'max_length_field': 'Короткий',
            'regex_field': 'OnlyLetters',
            'email_field': 'valid@email.com',
            'url_field': 'https://example.com',
            'integer_field': 50,
            'decimal_field': '25.50',
            'date_field': '2024-01-01',
            'time_field': '12:00',
            'datetime_field': '2024-01-01T12:00'
        }

    @staticmethod
    def create_invalid_form_data():
        """Создание неверных данных для формы"""
        return {
            'name': '',  # Пустое обязательное поле
            'email': 'invalid-email',  # Неверный email
            'message': 'Коротко',  # Слишком короткое
            'min_length_field': 'Коротко',  # Менее 5 символов
            'max_length_field': 'Слишком длинное значение',  # Более 10 символов
            'regex_field': '123',  # Только цифры
            'integer_field': 150,  # Больше максимального значения
            'decimal_field': '999.999',  # Слишком много цифр
            'required_field': 'error'  # Триггер общей ошибки
        }

    @staticmethod
    def create_formset_data(forms_count=2):
        """Создание данных для formset"""
        data = {
            'form-TOTAL_FORMS': str(forms_count),
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '10'
        }
        
        for i in range(forms_count):
            data[f'form-{i}-title'] = f'Заголовок {i + 1}'
            data[f'form-{i}-content'] = f'Содержание формы {i + 1}'
            data[f'form-{i}-priority'] = 'medium'
        
        return data


class TestComponentBuilder:
    """Построитель тестовых компонентов"""

    @staticmethod
    def create_alert_data():
        """Создание данных для alert компонента"""
        return [
            ("info", "Информационное сообщение"),
            ("success", "Сообщение об успехе"),
            ("warning", "Предупреждение"),
            ("danger", "Ошибка"),
            ("error", "Критическая ошибка")
        ]

    @staticmethod
    def create_button_data():
        """Создание данных для button компонента"""
        return [
            ("default", "Обычная кнопка"),
            ("primary", "Основная кнопка"),
            ("secondary", "Вторичная кнопка"),
            ("success", "Кнопка успеха"),
            ("danger", "Кнопка опасности"),
            ("warning", "Кнопка предупреждения"),
            ("info", "Информационная кнопка")
        ]

    @staticmethod
    def create_tile_data():
        """Создание данных для tile компонента"""
        sizes = ["small", "medium", "large", "wide", "tall"]
        colors = ["blue", "green", "red", "yellow", "orange", "purple", "pink", "brown", "gray"]
        
        return {
            'sizes': sizes,
            'colors': colors,
            'titles': ["Заголовок 1", "Заголовок 2", "Заголовок 3"],
            'contents': ["Содержание 1", "Содержание 2", "Содержание 3"],
            'icons': ["home", "user", "settings", "info", "help"]
        }

    @staticmethod
    def create_table_data():
        """Создание данных для table компонента"""
        headers = ["Имя", "Email", "Телефон", "Роль", "Статус"]
        data = [
            ["Иван Иванов", "ivan@example.com", "+7-999-123-45-67", "Администратор", "Активен"],
            ["Петр Петров", "petr@example.com", "+7-999-234-56-78", "Пользователь", "Активен"],
            ["Сидор Сидоров", "sidor@example.com", "+7-999-345-67-89", "Модератор", "Неактивен"],
            ["Анна Аннова", "anna@example.com", "+7-999-456-78-90", "Пользователь", "Активен"]
        ]
        
        return {
            'headers': headers,
            'data': data,
            'caption': "Список пользователей"
        }


class TestSettingsBuilder:
    """Построитель тестовых настроек"""

    @staticmethod
    def create_basic_settings():
        """Создание базовых настроек"""
        return {
            'METROUI5': {
                'wrapper_class': 'test-wrapper',
                'horizontal_label_class': 'col-sm-3',
                'horizontal_field_class': 'col-sm-9',
                'theme': 'light',
                'cdn_mode': False
            }
        }

    @staticmethod
    def create_advanced_settings():
        """Создание расширенных настроек"""
        return {
            'METROUI5': {
                'css_url': {
                    'url': 'custom.css',
                    'integrity': 'sha256-test',
                    'crossorigin': 'anonymous'
                },
                'javascript_url': {
                    'url': 'custom.js',
                    'defer': True,
                    'async': False
                },
                'icons_css_url': {
                    'url': 'custom-icons.css',
                    'media': 'print'
                },
                'custom_css_files': ['extra1.css', 'extra2.css'],
                'custom_javascript_files': ['extra1.js', 'extra2.js'],
                'theme': 'dark',
                'theme_switcher_enabled': True,
                'cdn_mode': True,
                'use_cdn': True,
                'minified': False
            }
        }

    @staticmethod
    def create_invalid_settings():
        """Создание неверных настроек"""
        return {
            'METROUI5': {
                'css_url': 'invalid_string',  # Должно быть dict
                'javascript_url': None,  # Должно быть dict
                'wrapper_class': 123,  # Должно быть string
                'theme': 'invalid_theme',  # Неверное значение
                'tile_size_options': 'invalid',  # Должно быть list
                'tile_color_options': 456  # Должно быть list
            }
        }


class TestAssertionHelper:
    """Помощник для проверок"""

    @staticmethod
    def assert_html_structure(result, expected_tags=None, expected_classes=None, expected_attrs=None):
        """Проверка структуры HTML"""
        if expected_tags:
            for tag in expected_tags:
                assert tag in result, f"Тег {tag} не найден в результате"
        
        if expected_classes:
            for class_name in expected_classes:
                assert class_name in result, f"CSS класс {class_name} не найден в результате"
        
        if expected_attrs:
            for attr, value in expected_attrs.items():
                if value is True:
                    assert attr in result, f"Атрибут {attr} не найден в результате"
                else:
                    assert f'{attr}="{value}"' in result, f"Атрибут {attr} со значением {value} не найден в результате"

    @staticmethod
    def assert_form_fields(result, expected_fields):
        """Проверка полей формы"""
        for field_name in expected_fields:
            assert f'name="{field_name}"' in result, f"Поле {field_name} не найдено в результате"

    @staticmethod
    def assert_form_errors(result, expected_errors):
        """Проверка ошибок формы"""
        for error in expected_errors:
            assert error.lower() in result.lower(), f"Ошибка {error} не найдена в результате"

    @staticmethod
    def assert_css_classes(result, expected_classes):
        """Проверка CSS классов"""
        for class_name in expected_classes:
            assert class_name in result, f"CSS класс {class_name} не найден в результате"

    @staticmethod
    def assert_component_rendering(result, component_type, expected_content):
        """Проверка рендеринга компонента"""
        assert component_type in result, f"Компонент {component_type} не найден в результате"
        if expected_content:
            assert expected_content in result, f"Содержимое {expected_content} не найдено в результате"


class TestFixtureHelper:
    """Помощник для фикстур"""

    @staticmethod
    def create_test_form():
        """Создание тестовой формы"""
        return TestFormBuilder.create_simple_form()()

    @staticmethod
    def create_test_formset():
        """Создание тестового formset"""
        TestFormset = formset_factory(TestFormBuilder.create_simple_form(), extra=2)
        return TestFormset()

    @staticmethod
    def create_test_data():
        """Создание тестовых данных"""
        return TestDataBuilder.create_form_data()

    @staticmethod
    def create_test_settings():
        """Создание тестовых настроек"""
        return TestSettingsBuilder.create_basic_settings()


# Декораторы для тестов
def with_metroui5_settings(settings_dict):
    """Декоратор для применения настроек MetroUI5"""
    def decorator(func):
        @override_settings(**settings_dict)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


def with_form_data(data_dict):
    """Декоратор для применения данных формы"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            kwargs['form_data'] = data_dict
            return func(*args, **kwargs)
        return wrapper
    return decorator


def with_component_data(component_type, data):
    """Декоратор для применения данных компонента"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            kwargs['component_data'] = data
            kwargs['component_type'] = component_type
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Глобальные фикстуры для pytest
@pytest.fixture
def test_form_builder():
    """Фикстура для построителя тестовых форм"""
    return TestFormBuilder


@pytest.fixture
def test_data_builder():
    """Фикстура для построителя тестовых данных"""
    return TestDataBuilder


@pytest.fixture
def test_component_builder():
    """Фикстура для построителя тестовых компонентов"""
    return TestComponentBuilder


@pytest.fixture
def test_settings_builder():
    """Фикстура для построителя тестовых настроек"""
    return TestSettingsBuilder


@pytest.fixture
def assertion_helper():
    """Фикстура для помощника проверок"""
    return TestAssertionHelper


@pytest.fixture
def test_form():
    """Фикстура для тестовой формы"""
    return TestFixtureHelper.create_test_form()


@pytest.fixture
def test_formset():
    """Фикстура для тестового formset"""
    return TestFixtureHelper.create_test_formset()


@pytest.fixture
def test_data():
    """Фикстура для тестовых данных"""
    return TestFixtureHelper.create_test_data()


@pytest.fixture
def basic_settings():
    """Фикстура для базовых настроек"""
    return TestFixtureHelper.create_test_settings()
