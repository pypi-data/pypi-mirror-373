# Django MetroUI5

[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/django-4.1%20%7C%204.2%20%7C%205.0%20%7C%205.1%20%7C%205.2.5-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Compatibility](https://img.shields.io/badge/compatibility-25%20combinations-brightgreen.svg)](https://github.com/DevCraftClub/django-metroui5/actions)

**Django MetroUI5** - это Django пакет для интеграции MetroUI v5 с Django 4.1+ и Python 3.9+.

**Django MetroUI5** is a Django package for integrating MetroUI v5 with Django 4.1+ and Python 3.9+.

> 🔄 **Compatibility Tested**: Our CI/CD pipeline tests **25 different combinations** of Python and Django versions to ensure metroui5 works across all supported environments.

## 🚀 Особенности / Features

- **Полная интеграция MetroUI v5** с Django / **Full MetroUI v5 integration** with Django
- **Template tags** для всех основных компонентов MetroUI / **Template tags** for all major MetroUI components
- **Автоматическое рендеринг форм** с MetroUI стилизацией / **Automatic form rendering** with MetroUI styling
- **Поддержка MetroUI компонентов**: tiles, cards, buttons, alerts, progress bars / **MetroUI component support**:
  tiles, cards, buttons, alerts, progress bars
- **Responsive дизайн** для всех устройств / **Responsive design** for all devices
- **🔄 Comprehensive Compatibility Testing** - Tested across **25 Python + Django combinations**
- **Django 4.1+ совместимость** / **Django 4.1+ compatibility**
- **Python 3.9+ поддержка** / **Python 3.9+ support**
- **Bilingual documentation** - English and Russian comments and docstrings
- **Full test coverage** - Comprehensive testing for all components
- **Online demo application** - Live demonstration of all features

## 📋 Требования / Requirements

- Python 3.9, 3.10, 3.11, 3.12, or 3.13
- Django 4.1, 4.2, 5.0, 5.1, or 5.2.5
- MetroUI v5 (включен в пакет) / MetroUI v5 (included in package)

## 🛠️ Быстрый старт / Quick Start

### 1. Установка пакета / Package Installation

```bash
# Клонирование репозитория / Clone repository
git clone https://github.com/DevCraftClub/django-metroui5.git
cd django-metroui5

# Установка в режиме разработки / Install in development mode
pip install -e .
```

### 2. Запуск демонстрационного приложения / Running Demo Application

```bash
# Переход в папку с демо / Navigate to demo folder
cd example

# Проверка конфигурации / Check configuration
python3 manage.py check

# Запуск сервера разработки / Start development server
python3 manage.py runserver
```

Демо приложение будет доступно по адресу: **http://127.0.0.1:8000/** / Demo application will be available at: \* \*http://127.0.0.1:8000/**

### 3. Доступные страницы демо / Available Demo Pages

- **Главная** (`/`) - Обзор всех возможностей MetroUI5 / **Main** (`/`) - Overview of all MetroUI5 capabilities
- **Формы** (`/forms/`) - Демонстрация рендеринга Django форм / **Forms** (`/forms/`) - Django form rendering
  demonstration
- **Компоненты** (`/components/`) - Все доступные UI компоненты / **Components** (`/components/`) - All available UI
  components
- **Tiles** (`/tiles/`) - Примеры MetroUI tiles / **Tiles** (`/tiles/`) - MetroUI tiles examples

## 🧪 Тестирование / Testing

### 🧪 Compatibility Testing

Our CI/CD pipeline tests **25 different combinations** of Python and Django versions to ensure metroui5 works across all supported environments:

- **Python**: 3.9, 3.10, 3.11, 3.12, 3.13
- **Django**: 4.1, 4.2, 5.0, 5.1, 5.2.5

### Запуск тестов / Running Tests

```bash
# В корневой папке проекта / In project root folder
pytest

# Тесты с покрытием / Tests with coverage
pytest --cov=metroui5

# Django тесты / Django tests
cd example
python3 manage.py test

# Тестирование совместимости / Compatibility testing
# Tests run automatically on GitHub Actions for all Python + Django combinations
```

## 📚 Документация / Documentation

- **[CHANGELOG.md](CHANGELOG.md)** - История изменений / Change history
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Руководство по вкладу / Contribution guide
- **Inline Documentation** - Bilingual comments and docstrings throughout the codebase
- **Test Coverage** - Comprehensive test suite with detailed examples

## 🎯 Использование в вашем проекте / Using in Your Project

### 1. Добавьте в INSTALLED_APPS / Add to INSTALLED_APPS

```python
INSTALLED_APPS = [
	# ... другие приложения / ... other applications
	'metroui5',
]
```

### 2. Настройте MetroUI (опционально) / Configure MetroUI (optional)

```python
# settings.py
METROUI5 = {
	'css_url': {
		'url': 'metroui5/css/metro.all.css',
		'integrity': None,
		'crossorigin': None,
	},
	'javascript_url': {
		'url': 'metroui5/js/metro.all.js',
		'integrity': None,
		'crossorigin': None,
	},
	'icons_css_url': {
		'url': 'metroui5/icons/icons.css',
		'integrity': None,
		'crossorigin': None,
	},
	'theme': 'default',
	'set_placeholder': True,
	'required_css_class': 'required',
	'error_css_class': 'error',
	'success_css_class': 'success',
}
```

### 3. Используйте в шаблонах / Use in Templates

```html
{% load metroui5 %}

<!DOCTYPE html>
<html>
	<head>
		<title>{% block title %}My App{% endblock %}</title>
		{% metroui5_css %} {% metroui5_icons_css %}
	</head>
	<body>
		<div class="container">{% block content %}{% endblock %}</div>

		{% metroui5_javascript %}
	</body>
</html>
```

## 🧩 Template Tags

### CSS и JavaScript / CSS and JavaScript

- `{% metroui5_css %}` - Включает CSS файл MetroUI / Includes MetroUI CSS file
- `{% metroui5_javascript %}` - Включает JavaScript файл MetroUI / Includes MetroUI JavaScript file
- `{% metroui5_icons_css %}` - Включает CSS файл иконок MetroUI / Includes MetroUI icons CSS file

### Формы / Forms

- `{% metroui5_form form %}` - Рендерит форму с MetroUI стилизацией / Renders form with MetroUI styling
- `{% metroui5_field field %}` - Рендерит поле формы / Renders form field
- `{% metroui5_form_errors form %}` - Рендерит ошибки формы / Renders form errors
- `{% metroui5_formset formset %}` - Рендерит формсет / Renders formset

### Компоненты / Components

- `{% metroui5_button content %}` - MetroUI кнопка / MetroUI button
- `{% metroui5_tile title %}` - MetroUI tile
- `{% metroui5_card %}` - MetroUI карточка / MetroUI card
- `{% metroui5_progress value %}` - MetroUI progress bar
- `{% metroui5_alert content %}` - MetroUI alert
- `{% metroui5_messages %}` - Django сообщения в MetroUI стиле / Django messages in MetroUI style

## 🎨 Примеры использования / Usage Examples

### Кнопки / Buttons

```html
{% metroui5_button "Submit" button_type="primary" size="lg" %} {%
metroui5_button "Cancel" button_type="secondary" outline=True %}
```

### Tiles

```html
{% metroui5_tile "Settings" size="medium" color="blue" icon="cog" %} {%
metroui5_tile "Users" size="large" color="green" content="1,234 active users" %}
```

### Формы / Forms

```html
<!-- Рендеринг всей формы / Render entire form -->
{% metroui5_form form %}

<!-- Рендеринг отдельных полей / Render individual fields -->
{% metroui5_field form.username %} {% metroui5_field form.email %}
```

### Progress Bars

```html
{% metroui5_progress 75 color="blue" %} {% metroui5_progress 50 color="green"
size="large" %}
```

## 🔧 Разработка / Development

### Установка для разработки / Development Installation

```bash
git clone https://github.com/DevCraftClub/django-metroui5.git
cd django-metroui5
pip install -e .[dev]
```

### Проверка кода / Code Quality

```bash
black --check .
flake8 .
mypy .
```

## 📦 Структура проекта / Project Structure

```
django-metroui5/
├── metroui5/                    # Основной пакет / Main package
│   ├── templatetags/           # Template tags
│   ├── templates/              # Шаблоны MetroUI / MetroUI templates
│   ├── static/                 # Статические файлы MetroUI / MetroUI static files
│   ├── components.py           # UI компоненты / UI components
│   ├── forms.py                # Рендеринг форм / Form rendering
│   ├── renderers.py            # Система рендереров / Renderer system
│   └── ...
├── example/                     # Демонстрационное приложение / Demo application
├── tests/                       # Тесты / Tests
├── docs/                        # Документация / Documentation
└── ...
```

## 🌟 Особенности реализации / Implementation Features

- **Следование принципам DRY** - переиспользование кода между компонентами / **DRY principles** - code reuse between
  components
- **Bilingual documentation** - English and Russian comments and docstrings throughout
- **Generic шаблоны** - базовые шаблоны для переиспользования / **Generic templates** - base templates for reuse
- **Комплексное тестирование** - покрытие всех основных функций / **Comprehensive testing** - coverage of all main
  functions
- **Современная архитектура** - использование Python 3.9+ возможностей / **Modern architecture** - using Python 3.9+ capabilities
  capabilities
- **Full MetroUI v5 integration** - complete component library with Django integration

## 📈 Следующие шаги / Next Steps

### Краткосрочные задачи / Short-term Tasks

1. ✅ Добавить больше MetroUI компонентов / Add more MetroUI components
2. ✅ Расширить систему тестирования / Expand testing system
3. ✅ Улучшить документацию / Improve documentation
4. ✅ Создать онлайн демо / Create online demo

### Среднесрочные задачи / Medium-term Tasks

1. Добавить поддержку тем / Add theme support
2. Создать дополнительные рендереры / Create additional renderers
3. Добавить поддержку Jinja2 / Add Jinja2 support

### Долгосрочные задачи / Long-term Tasks

1. ✅ Создать онлайн демо / Create online demo
2. Добавить поддержку других версий Django / Add support for other Django versions
3. Создать экосистему плагинов / Create plugin ecosystem

## 🤝 Вклад в проект / Contributing

Мы приветствуем вклад в развитие проекта! Пожалуйста, ознакомьтесь с [CONTRIBUTING.md](CONTRIBUTING.md) для получения
дополнительной информации.

We welcome contributions to the project! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

## 📄 Лицензия / License

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для получения дополнительной информации.

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## 🙏 Благодарности / Acknowledgments

- [MetroUI](https://metroui.org.ua/) - за отличный UI фреймворк / for excellent UI framework
- [Django](https://www.djangoproject.com/) - за мощный веб-фреймворк / for powerful web framework
- [django-bootstrap5](https://github.com/zostera/django-bootstrap5) - за вдохновение архитектуры / for architecture
  inspiration

## 📞 Поддержка / Support

Если у вас есть вопросы или проблемы: / If you have questions or issues:

- Создайте [Issue](https://github.com/DevCraftClub/django-metroui5/issues) / Create
  an [Issue](https://github.com/DevCraftClub/django-metroui5/issues)
- Обратитесь к [документации](https://django-metroui5.readthedocs.io/) / Check
  the [documentation](https://django-metroui5.readthedocs.io/)
- Присоединитесь к обсуждениям в [Discussions](https://github.com/DevCraftClub/django-metroui5/discussions) / Join
  discussions in [Discussions](https://github.com/DevCraftClub/django-metroui5/discussions)

---

**Django MetroUI5** - Сделайте ваши Django приложения красивыми с MetroUI v5! 🎨✨

**Django MetroUI5** - Make your Django applications beautiful with MetroUI v5! 🎨✨

## 🎯 Текущий статус проекта / Current Project Status

### ✅ Завершенные задачи / Completed Tasks

- **Bilingual Documentation** - English and Russian comments/docstrings throughout codebase
- **Comprehensive Testing** - Full test coverage for all components and utilities
- **Compatibility Testing Matrix** - 25 Python + Django version combinations tested
- **Online Demo Application** - Live demonstration of all MetroUI5 features
- **MetroUI v5 Integration** - Complete component library with Django integration
- **Form Rendering System** - Automatic MetroUI styling for Django forms
- **Template Tags** - Complete set of MetroUI component template tags
- **Static Files Management** - Proper MetroUI CSS/JS integration

### 🔄 В процессе / In Progress

- **Jinja2 Support** - Template engine compatibility
- **Plugin Ecosystem** - Extensible component system

### 📋 Планируется / Planned

- **Theme System** - Multiple MetroUI themes
- **Additional Renderers** - Specialized form renderers
- **Performance Optimization** - Enhanced rendering speed

## 🚀 Быстрый тест / Quick Test

Хотите быстро протестировать пакет? Запустите демо приложение: / Want to quickly test the package? Run the demo
application:

```bash
# Установка и запуск за 3 команды / Installation and launch in 3 commands
pip install -e .
cd example
python3 manage.py runserver
```

Откройте http://127.0.0.1:8000/ в браузере и наслаждайтесь MetroUI5! 🎉 / Open http://127.0.0.1:8000/ in your browser and
enjoy MetroUI5! 🎉
