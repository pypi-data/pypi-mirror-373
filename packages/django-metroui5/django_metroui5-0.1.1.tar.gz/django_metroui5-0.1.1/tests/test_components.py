"""
Тесты для модуля components
"""
import pytest
from metroui5.components import (
    render_alert,
    render_button,
    render_tile,
    render_card,
    render_progress,
    render_accordion,
    render_calendar,
    render_dialog,
    render_dropdown,
    render_input,
    render_list,
    render_menu,
    render_navigation,
    render_panel,
    render_sidebar,
    render_table,
    render_tabs,
    render_toolbar,
    render_modal,
    render_breadcrumb,
    render_pagination,
    render_badge,
    render_avatar,
    render_rating,
)


class TestRenderAlert:
    """Тесты для компонента Alert"""

    def test_render_alert_basic(self):
        """Тест базового рендеринга alert"""
        result = render_alert("Test message")
        assert 'class="alert alert-info"' in result
        assert "Test message" in result
        assert 'role="alert"' in result

    def test_render_alert_with_type(self):
        """Тест рендеринга alert с типом"""
        result = render_alert("Success message", alert_type="success")
        assert 'class="alert alert-success"' in result

    def test_render_alert_dismissible(self):
        """Тест рендеринга dismissible alert"""
        result = render_alert("Dismissible message", dismissible=True)
        assert 'class="alert alert-info alert-dismissible"' in result
        assert 'data-role="close"' in result
        assert "&times;" in result

    def test_render_alert_with_custom_attrs(self):
        """Тест рендеринга alert с пользовательскими атрибутами"""
        result = render_alert("Test message", id="test-alert", data_test="value")
        assert 'id="test-alert"' in result
        assert 'data_test="value"' in result

    def test_render_alert_all_types(self):
        """Тест всех типов alert"""
        types = ["info", "success", "warning", "danger", "error"]
        for alert_type in types:
            result = render_alert("Test", alert_type=alert_type)
            assert f'alert-{alert_type}' in result


class TestRenderButton:
    """Тесты для компонента Button"""

    def test_render_button_basic(self):
        """Тест базового рендеринга button"""
        result = render_button("Click me")
        assert 'class="button"' in result
        assert "Click me" in result
        assert 'type="button"' in result

    def test_render_button_with_type(self):
        """Тест рендеринга button с типом"""
        result = render_button("Primary", button_type="primary")
        assert 'class="button primary"' in result

    def test_render_button_outline(self):
        """Тест рендеринга outline button"""
        result = render_button("Outline", button_type="success", outline=True)
        assert 'class="button outline-success"' in result

    def test_render_button_with_size(self):
        """Тест рендеринга button с размером"""
        result = render_button("Large", size="lg")
        assert 'class="button button-lg"' in result

    def test_render_button_with_custom_attrs(self):
        """Тест рендеринга button с пользовательскими атрибутами"""
        result = render_button("Test", id="test-btn", disabled=True)
        assert 'id="test-btn"' in result
        assert "disabled" in result

    def test_render_button_all_types(self):
        """Тест всех типов button"""
        types = ["default", "primary", "secondary", "success", "danger", "warning", "info"]
        for button_type in types:
            result = render_button("Test", button_type=button_type)
            if button_type == "default":
                assert 'class="button"' in result
            else:
                assert button_type in result


class TestRenderTile:
    """Тесты для компонента Tile"""

    def test_render_tile_basic(self):
        """Тест базового рендеринга tile"""
        result = render_tile("Test Tile")
        assert 'class="tile tile-medium tile-blue"' in result
        assert 'data-role="tile"' in result
        assert "Test Tile" in result

    def test_render_tile_with_size(self):
        """Тест рендеринга tile с размером"""
        result = render_tile("Test", size="large")
        assert 'class="tile tile-large tile-blue"' in result

    def test_render_tile_with_color(self):
        """Тест рендеринга tile с цветом"""
        result = render_tile("Test", color="red")
        assert 'class="tile tile-medium tile-red"' in result

    def test_render_tile_with_icon(self):
        """Тест рендеринга tile с иконкой"""
        result = render_tile("Test", icon="home")
        assert 'data-icon="home"' in result

    def test_render_tile_with_content(self):
        """Тест рендеринга tile с содержимым"""
        result = render_tile("Title", content="Additional content")
        assert "Title" in result
        assert "Additional content" in result

    def test_render_tile_all_sizes(self):
        """Тест всех размеров tile"""
        sizes = ["small", "medium", "large", "wide", "tall"]
        for size in sizes:
            result = render_tile("Test", size=size)
            assert f'tile-{size}' in result

    def test_render_tile_all_colors(self):
        """Тест всех цветов tile"""
        colors = ["blue", "green", "red", "yellow", "orange", "purple", "pink", "brown", "gray"]
        for color in colors:
            result = render_tile("Test", color=color)
            assert f'tile-{color}' in result


class TestRenderCard:
    """Тесты для компонента Card"""

    def test_render_card_basic(self):
        """Тест базового рендеринга card"""
        result = render_card("Card Title", "Card content")
        assert 'class="card"' in result
        assert "Card Title" in result
        assert "Card content" in result

    def test_render_card_with_header(self):
        """Тест рендеринга card с заголовком"""
        result = render_card(header="Header", content="Content")
        assert "Header" in result

    def test_render_card_with_footer(self):
        """Тест рендеринга card с подвалом"""
        result = render_card(content="Content", footer="Footer")
        assert "Footer" in result

    def test_render_card_with_image(self):
        """Тест рендеринга card с изображением"""
        result = render_card(content="Content", image="image.jpg")
        assert 'image="image.jpg"' in result

    def test_render_card_with_custom_attrs(self):
        """Тест рендеринга card с пользовательскими атрибутами"""
        result = render_card(content="Content", id="test-card")
        assert 'id="test-card"' in result


class TestRenderProgress:
    """Тесты для компонента Progress"""

    def test_render_progress_basic(self):
        """Тест базового рендеринга progress"""
        result = render_progress(50)
        assert 'class="progress progress-blue"' in result
        assert 'data-value="50"' in result

    def test_render_progress_with_label(self):
        """Тест рендеринга progress с меткой"""
        result = render_progress(75, label="75%")
        assert "75%" in result

    def test_render_progress_with_color(self):
        """Тест рендеринга progress с цветом"""
        result = render_progress(60, color="success")
        assert 'class="progress progress-success"' in result

    def test_render_progress_with_striped(self):
        """Тест рендеринга striped progress"""
        result = render_progress(40, striped=True)
        assert 'striped' in result

    def test_render_progress_with_animated(self):
        """Тест рендеринга animated progress"""
        result = render_progress(30, animated=True)
        assert 'animated' in result


class TestRenderInput:
    """Тесты для компонента Input"""

    def test_render_input_basic(self):
        """Тест базового рендеринга input"""
        result = render_input("text", "Test Input")
        assert 'type="text"' in result
        assert 'placeholder="Test Input"' in result

    def test_render_input_with_type(self):
        """Тест рендеринга input с типом"""
        result = render_input("email", "test@example.com")
        assert 'type="email"' in result

    def test_render_input_with_placeholder(self):
        """Тест рендеринга input с placeholder"""
        result = render_input("name", placeholder="Enter your name")
        assert 'placeholder="Enter your name"' in result

    def test_render_input_with_required(self):
        """Тест рендеринга required input"""
        result = render_input("name", required=True)
        assert "required" in result

    def test_render_input_with_disabled(self):
        """Тест рендеринга disabled input"""
        result = render_input("name", disabled=True)
        assert "disabled" in result

    def test_render_input_with_custom_attrs(self):
        """Тест рендеринга input с пользовательскими атрибутами"""
        result = render_input("name", id="test-input", data_test="value")
        assert 'id="test-input"' in result
        assert 'data_test="value"' in result


class TestRenderTable:
    """Тесты для компонента Table"""

    def test_render_table_basic(self):
        """Тест базового рендеринга table"""
        headers = ["Name", "Email", "Phone"]
        data = [
            ["John Doe", "john@example.com", "123-456-7890"],
            ["Jane Smith", "jane@example.com", "098-765-4321"]
        ]
        result = render_table(headers, data)
        assert "<table" in result
        assert "Name" in result
        assert "john@example.com" in result

    def test_render_table_with_caption(self):
        """Тест рендеринга table с заголовком"""
        headers = ["Name", "Email"]
        data = [["John", "john@example.com"]]
        result = render_table(headers, data, caption="Users Table")
        assert "Users Table" in result

    def test_render_table_with_striped(self):
        """Тест рендеринга striped table"""
        headers = ["Name"]
        data = [["John"]]
        result = render_table(headers, data, striped=True)
        assert 'striped' in result

    def test_render_table_with_bordered(self):
        """Тест рендеринга bordered table"""
        headers = ["Name"]
        data = [["John"]]
        result = render_table(headers, data, bordered=True)
        assert 'bordered' in result

    def test_render_table_with_hover(self):
        """Тест рендеринга table с hover эффектом"""
        headers = ["Name"]
        data = [["John"]]
        result = render_table(headers, data, hover=True)
        assert 'hover' in result


class TestRenderModal:
    """Тесты для компонента Modal"""

    def test_render_modal_basic(self):
        """Тест базового рендеринга modal"""
        result = render_modal("Test Modal", "Modal content")
        assert 'class="modal"' in result
        assert "Test Modal" in result
        assert "Modal content" in result

    def test_render_modal_with_id(self):
        """Тест рендеринга modal с ID"""
        result = render_modal("Title", "Content", modal_id="test-modal")
        assert 'id="test-modal"' in result

    def test_render_modal_with_size(self):
        """Тест рендеринга modal с размером"""
        result = render_modal("Title", "Content", size="lg")
        assert 'size="lg"' in result

    def test_render_modal_with_footer(self):
        """Тест рендеринга modal с подвалом"""
        result = render_modal("Title", "Content", footer="Footer content")
        assert "Footer content" in result


class TestRenderPagination:
    """Тесты для компонента Pagination"""

    def test_render_pagination_basic(self):
        """Тест базового рендеринга pagination"""
        result = render_pagination(1, 10)
        assert 'class="pagination"' in result

    def test_render_pagination_with_show_first_last(self):
        """Тест рендеринга pagination с кнопками First/Last"""
        result = render_pagination(5, 10, show_first_last=True)
        assert "show_first_last" in result
        assert "1" in result
        assert "10" in result

    def test_render_pagination_with_show_prev_next(self):
        """Тест рендеринга pagination с кнопками Prev/Next"""
        result = render_pagination(5, 10, show_prev_next=True)
        assert "show_prev_next" in result
        assert "&laquo;" in result
        assert "&raquo;" in result


class TestRenderBadge:
    """Тесты для компонента Badge"""

    def test_render_badge_basic(self):
        """Тест базового рендеринга badge"""
        result = render_badge("5")
        assert 'class="badge badge-default"' in result
        assert "5" in result

    def test_render_badge_with_color(self):
        """Тест рендеринга badge с цветом"""
        result = render_badge("New", color="success")
        assert 'color="success"' in result

    def test_render_badge_with_size(self):
        """Тест рендеринга badge с размером"""
        result = render_badge("Large", size="lg")
        assert 'size="lg"' in result


class TestRenderRating:
    """Тесты для компонента Rating"""

    def test_render_rating_basic(self):
        """Тест базового рендеринга rating"""
        result = render_rating(4)
        assert 'class="rating"' in result

    def test_render_rating_with_max(self):
        """Тест рендеринга rating с максимальным значением"""
        result = render_rating(3, max_rating=5)
        assert result.count('class="star"') == 3
        assert result.count('class="star-empty"') == 2

    def test_render_rating_readonly(self):
        """Тест рендеринга readonly rating"""
        result = render_rating(4, readonly=True)
        assert 'readonly' in result


class TestEdgeCases:
    """Тесты для граничных случаев"""

    def test_render_components_with_empty_content(self):
        """Тест рендеринга компонентов с пустым содержимым"""
        alert_result = render_alert("")
        assert alert_result is not None
        
        button_result = render_button("")
        assert button_result is not None

    def test_render_components_with_special_characters(self):
        """Тест рендеринга компонентов со специальными символами"""
        result = render_alert("Test & <script>alert('xss')</script>")
        assert "Test &" in result
        assert "<script>alert('xss')</script>" in result

    def test_render_components_with_unicode(self):
        """Тест рендеринга компонентов с Unicode"""
        result = render_button("Привет мир")
        assert "Привет мир" in result
