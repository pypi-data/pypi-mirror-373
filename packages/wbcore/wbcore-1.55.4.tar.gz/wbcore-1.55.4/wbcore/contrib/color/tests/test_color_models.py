import pytest
from wbcore.contrib.color.factories import ColorGradientFactory
from wbcore.contrib.color.models import ColorGradient

COLORS = ["#FFFFFF", "#000000", "#FF5733", "#3357FF", "#FF33A1", "#800080"]


class TestColorGradientModel:
    @pytest.mark.django_db
    def integration_test(self, mocker):
        gradient = ColorGradientFactory()
        assert ColorGradient.objects.filter(id=gradient.id).exists()

    def test_str_method(self, mocker):
        gradient = ColorGradient()
        mocker.patch.object(gradient, "title", "My Gradient")
        assert str(gradient) == "My Gradient"

    def test_default_colors(self):
        gradient = ColorGradient()
        assert gradient.colors == []

    def test_get_gradient(self, mocker):
        gradient = ColorGradient()
        assert list(gradient.get_gradient()) == []

    def test_get_gradient_no_color_argument(self, mocker):
        gradient = ColorGradient()
        mocker.patch.object(gradient, "colors", COLORS)
        palette = list(gradient.get_gradient(color=None, color_size=3))
        assert len(palette) == 3

    def test_get_gradient_with_non_existent_color(self, mocker):
        gradient = ColorGradient()
        mocker.patch.object(gradient, "colors", COLORS)
        non_existent_color = "#123456"
        palette = list(gradient.get_gradient(color=non_existent_color))
        assert len(palette) == len(COLORS)
        assert palette == ["#000000", "#FF5733", "#3357FF", "#FF33A1", "#800080", "#FFFFFF"]

    @pytest.mark.parametrize("color_size", [20, 1, 0, -1])
    def test_get_gradient_with_different_size(self, color_size, mocker):
        gradient = ColorGradient()
        mocker.patch.object(gradient, "colors", COLORS)
        palette = list(gradient.get_gradient(color_size=color_size))
        base_colors = gradient.colors
        assert len(palette) == color_size if color_size > 0 else len(base_colors)
        for index, color in enumerate(palette):
            assert color == base_colors[index % len(base_colors)]

    @pytest.mark.parametrize("color", COLORS)
    def test_get_gradient_with_different_color(self, color, mocker):
        gradient = ColorGradient()
        mocker.patch.object(gradient, "colors", COLORS)
        base_colors = gradient.colors

        color_index = base_colors.index(color)
        palette = list(gradient.get_gradient(color=color))

        assert len(palette) == len(base_colors)
        assert palette == base_colors[color_index:] + base_colors[:color_index]
