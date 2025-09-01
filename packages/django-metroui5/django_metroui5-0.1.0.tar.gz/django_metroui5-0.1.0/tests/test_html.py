"""
Тесты для модуля html
"""
import pytest
from metroui5.html import (
    render_tag,
    render_link_tag,
    render_script_tag,
    render_custom_css_files,
    render_custom_javascript_files,
)


class TestRenderTag:
    """Тесты для функции render_tag"""

    def test_render_tag_basic(self):
        """Тест базового рендеринга тега"""
        result = render_tag("div")
        assert result == "<div />"

    def test_render_tag_with_attributes(self):
        """Тест рендеринга тега с атрибутами"""
        result = render_tag("div", {"class": "test", "id": "main"})
        assert result == '<div class="test" id="main" />'

    def test_render_tag_with_content(self):
        """Тест рендеринга тега с содержимым"""
        result = render_tag("div", content="Hello World")
        assert result == "<div>Hello World</div>"

    def test_render_tag_with_attributes_and_content(self):
        """Тест рендеринга тега с атрибутами и содержимым"""
        result = render_tag("div", {"class": "test"}, "Hello World")
        assert result == '<div class="test">Hello World</div>'

    def test_render_tag_not_closed(self):
        """Тест рендеринга незакрытого тега"""
        result = render_tag("div", close=False)
        assert result == "<div>"

    def test_render_tag_with_none_attributes(self):
        """Тест рендеринга тега с None атрибутами"""
        result = render_tag("div", {"class": None, "id": "main"})
        assert result == '<div id="main" />'

    def test_render_tag_with_boolean_attributes(self):
        """Тест рендеринга тега с булевыми атрибутами"""
        result = render_tag("input", {"disabled": True, "readonly": False})
        assert result == "<input disabled />"

    def test_render_tag_with_empty_string_attributes(self):
        """Тест рендеринга тега с пустыми строковыми атрибутами"""
        result = render_tag("div", {"class": "", "id": "main"})
        assert result == '<div class="" id="main" />'

    def test_render_tag_with_zero_attribute(self):
        """Тест рендеринга тега с нулевым атрибутом"""
        result = render_tag("div", {"value": 0})
        assert result == '<div value="0" />'

    def test_render_tag_complex_attributes(self):
        """Тест рендеринга тега со сложными атрибутами"""
        attrs = {
            "class": "btn btn-primary",
            "data-toggle": "modal",
            "aria-label": "Close",
            "style": "color: red;"
        }
        result = render_tag("button", attrs, "Click me")
        expected = '<button class="btn btn-primary" data-toggle="modal" aria-label="Close" style="color: red;">Click me</button>'
        assert result == expected


class TestRenderLinkTag:
    """Тесты для функции render_link_tag"""

    def test_render_link_tag_simple_url(self):
        """Тест рендеринга link тега с простым URL"""
        result = render_link_tag("test.css")
        assert 'href="test.css"' in result
        assert 'rel="stylesheet"' in result
        assert 'type="text/css"' in result
        assert result.startswith('<link')
        assert result.endswith('>')

    def test_render_link_tag_with_custom_attrs(self):
        """Тест рендеринга link тега с пользовательскими атрибутами"""
        result = render_link_tag("test.css", media="print", title="Test CSS")
        assert 'href="test.css"' in result
        assert 'rel="stylesheet"' in result
        assert 'type="text/css"' in result
        assert 'media="print"' in result
        assert 'title="Test CSS"' in result
        assert result.startswith('<link')
        assert result.endswith('>')

    def test_render_link_tag_with_config_dict(self):
        """Тест рендеринга link тега с конфигурационным словарем"""
        config = {
            "url": "custom.css",
            "integrity": "sha256-test",
            "crossorigin": "anonymous",
            "media": "screen"
        }
        result = render_link_tag(config)
        assert 'href="custom.css"' in result
        assert 'rel="stylesheet"' in result
        assert 'type="text/css"' in result
        assert 'media="screen"' in result
        assert 'integrity="sha256-test"' in result
        assert 'crossorigin="anonymous"' in result
        assert result.startswith('<link')
        assert result.endswith('>')

    def test_render_link_tag_override_defaults(self):
        """Тест переопределения значений по умолчанию"""
        config = {
            "url": "custom.css",
            "rel": "preload",
            "type": "text/css"
        }
        result = render_link_tag(config)
        assert 'href="custom.css"' in result
        assert 'rel="preload"' in result
        assert 'type="text/css"' in result
        assert result.startswith('<link')
        assert result.endswith('>')

    def test_render_link_tag_with_integrity(self):
        """Тест рендеринга link тега с integrity"""
        result = render_link_tag("test.css", integrity="sha256-abc123")
        assert 'href="test.css"' in result
        assert 'rel="stylesheet"' in result
        assert 'type="text/css"' in result
        assert 'integrity="sha256-abc123"' in result
        assert result.startswith('<link')
        assert result.endswith('>')

    def test_render_link_tag_with_crossorigin(self):
        """Тест рендеринга link тега с crossorigin"""
        result = render_link_tag("test.css", crossorigin="anonymous")
        assert 'href="test.css"' in result
        assert 'rel="stylesheet"' in result
        assert 'type="text/css"' in result
        assert 'crossorigin="anonymous"' in result
        assert result.startswith('<link')
        assert result.endswith('>')


class TestRenderScriptTag:
    """Тесты для функции render_script_tag"""

    def test_render_script_tag_simple_url(self):
        """Тест рендеринга script тега с простым URL"""
        result = render_script_tag("test.js")
        assert 'src="test.js"' in result
        assert 'type="text/javascript"' in result
        assert result.startswith('<script')
        assert result.endswith(' />')

    def test_render_script_tag_with_custom_attrs(self):
        """Тест рендеринга script тега с пользовательскими атрибутами"""
        result = render_script_tag("test.js", async_attr=True, defer=True)
        assert 'src="test.js"' in result
        assert 'type="text/javascript"' in result
        assert 'async' in result
        assert 'defer' in result
        assert result.startswith('<script')
        assert result.endswith(' />')

    def test_render_script_tag_with_config_dict(self):
        """Тест рендеринга script тега с конфигурационным словарем"""
        config = {
            "url": "custom.js",
            "integrity": "sha256-test",
            "crossorigin": "anonymous",
            "defer": True
        }
        result = render_script_tag(config)
        assert 'src="custom.js"' in result
        assert 'type="text/javascript"' in result
        assert 'defer' in result
        assert 'integrity="sha256-test"' in result
        assert 'crossorigin="anonymous"' in result
        assert result.startswith('<script')
        assert result.endswith(' />')

    def test_render_script_tag_override_defaults(self):
        """Тест переопределения значений по умолчанию"""
        config = {
            "url": "custom.js",
            "type": "module"
        }
        result = render_script_tag(config)
        assert 'src="custom.js"' in result
        assert 'type="module"' in result
        assert result.startswith('<script')
        assert result.endswith(' />')

    def test_render_script_tag_with_async(self):
        """Тест рендеринга script тега с async"""
        result = render_script_tag("test.js", async_attr=True)
        assert 'src="test.js"' in result
        assert 'type="text/javascript"' in result
        assert 'async' in result
        assert result.startswith('<script')
        assert result.endswith(' />')

    def test_render_script_tag_with_defer(self):
        """Тест рендеринга script тега с defer"""
        result = render_script_tag("test.js", defer=True)
        assert 'src="test.js"' in result
        assert 'type="text/javascript"' in result
        assert 'defer' in result
        assert result.startswith('<script')
        assert result.endswith(' />')

    def test_render_script_tag_with_integrity(self):
        """Тест рендеринга script тега с integrity"""
        result = render_script_tag("test.js", integrity="sha256-abc123")
        assert 'src="test.js"' in result
        assert 'type="text/javascript"' in result
        assert 'integrity="sha256-abc123"' in result
        assert result.startswith('<script')
        assert result.endswith(' />')


class TestRenderCustomFiles:
    """Тесты для рендеринга пользовательских файлов"""

    def test_render_custom_css_files_empty(self):
        """Тест рендеринга пустого списка CSS файлов"""
        result = render_custom_css_files([])
        assert result == ""

    def test_render_custom_css_files_single(self):
        """Тест рендеринга одного CSS файла"""
        result = render_custom_css_files(["custom.css"])
        assert 'href="custom.css"' in result
        assert 'rel="stylesheet"' in result
        assert 'type="text/css"' in result
        assert result.startswith('<link')
        assert result.endswith('>')

    def test_render_custom_css_files_multiple(self):
        """Тест рендеринга нескольких CSS файлов"""
        result = render_custom_css_files(["custom1.css", "custom2.css"])
        assert 'href="custom1.css"' in result
        assert 'href="custom2.css"' in result
        assert 'rel="stylesheet"' in result
        assert 'type="text/css"' in result
        assert result.count('<link') == 2

    def test_render_custom_css_files_with_config(self):
        """Тест рендеринга CSS файлов с конфигурацией"""
        configs = [
            {"url": "custom1.css", "media": "print"},
            {"url": "custom2.css", "integrity": "sha256-test"}
        ]
        result = render_custom_css_files(configs)
        assert 'href="custom1.css"' in result
        assert 'href="custom2.css"' in result
        assert 'rel="stylesheet"' in result
        assert 'type="text/css"' in result
        assert 'media="print"' in result
        assert 'integrity="sha256-test"' in result
        assert result.count('<link') == 2

    def test_render_custom_javascript_files_empty(self):
        """Тест рендеринга пустого списка JavaScript файлов"""
        result = render_custom_javascript_files([])
        assert result == ""

    def test_render_custom_javascript_files_single(self):
        """Тест рендеринга одного JavaScript файла"""
        result = render_custom_javascript_files(["custom.js"])
        assert 'src="custom.js"' in result
        assert 'type="text/javascript"' in result
        assert result.startswith('<script')
        assert result.endswith(' />')

    def test_render_custom_javascript_files_multiple(self):
        """Тест рендеринга нескольких JavaScript файлов"""
        result = render_custom_javascript_files(["custom1.js", "custom2.js"])
        assert 'src="custom1.js"' in result
        assert 'src="custom2.js"' in result
        assert 'type="text/javascript"' in result
        assert result.count('<script') == 2

    def test_render_custom_javascript_files_with_config(self):
        """Тест рендеринга JavaScript файлов с конфигурацией"""
        configs = [
            {"url": "custom1.js", "defer": True},
            {"url": "custom2.js", "async_attr": True}
        ]
        result = render_custom_javascript_files(configs)
        assert 'src="custom1.js"' in result
        assert 'src="custom2.js"' in result
        assert 'type="text/javascript"' in result
        assert 'defer' in result
        assert 'async' in result
        assert result.count('<script') == 2


class TestEdgeCases:
    """Тесты для граничных случаев"""

    def test_render_tag_with_special_characters(self):
        """Тест рендеринга тега со специальными символами"""
        result = render_tag("div", {"data-test": "test&value"})
        assert result == '<div data-test="test&value" />'

    def test_render_tag_with_unicode_content(self):
        """Тест рендеринга тега с Unicode содержимым"""
        result = render_tag("div", content="Привет мир")
        assert result == "<div>Привет мир</div>"

    def test_render_tag_with_nested_quotes(self):
        """Тест рендеринга тега с вложенными кавычками"""
        result = render_tag("div", {"title": 'He said "Hello"'})
        assert 'title="He said "Hello""' in result
        assert result.startswith('<div')
        assert result.endswith('>')

    def test_render_tag_with_empty_content(self):
        """Тест рендеринга тега с пустым содержимым"""
        result = render_tag("div", content="")
        assert result == "<div></div>"

    def test_render_tag_with_zero_content(self):
        """Тест рендеринга тега с нулевым содержимым"""
        result = render_tag("div", content=0)
        assert result == "<div>0</div>"
