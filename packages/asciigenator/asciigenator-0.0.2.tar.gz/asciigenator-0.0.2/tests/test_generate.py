import asciigenator
import subprocess
import sys
import os

CLI_SCRIPT = os.path.join(os.path.dirname(__file__), "../asciigenator/cli.py")


def test_generate_simple_font():
    result = asciigenator.generate("Hello", font="simple")
    assert isinstance(result, str)
    assert len(result.strip()) > 0
    # Optionally, check for a known pattern in the output
    assert "*" in result  # Simple font uses asterisks


def test_generate_block_font():
    result = asciigenator.generate("W1rld", font="block")
    assert isinstance(result, str)
    assert len(result.strip()) > 0
    # Optionally, check for a known pattern in the output
    assert "█" in result  # Block font uses block characters


def test_generate_empty_string():
    result = asciigenator.generate("", font="simple")
    assert result.strip() == ""


def test_generate_with_color():
    """Test ASCII generation with color."""
    result = asciigenator.generate("Hello", font="simple", color="red")
    assert isinstance(result, str)
    assert len(result.strip()) > 0
    # Check for ANSI color codes
    assert "\033[31m" in result  # Red color code
    assert "\033[0m" in result  # Reset code
    assert "*" in result  # Simple font pattern


def test_generate_with_border():
    """Test ASCII generation with border."""
    result = asciigenator.generate("Hi", font="simple", border="#")
    assert isinstance(result, str)
    assert len(result.strip()) > 0
    # Check for border characters
    assert "#" in result
    assert "*" in result  # Original content should still be there
    lines = result.split("\n")
    # First and last lines should be all border characters
    assert all(char == "#" for char in lines[0])
    assert all(char == "#" for char in lines[-1])


def test_generate_with_color_and_border():
    """Test ASCII generation with both color and border."""
    result = asciigenator.generate("Test", font="simple", color="blue", border="*")
    assert isinstance(result, str)
    assert len(result.strip()) > 0
    # Check for color codes
    assert "\033[34m" in result  # Blue color code
    assert "\033[0m" in result  # Reset code
    # Check for border
    assert "*" in result
    lines = result.split("\n")
    # Should have border lines
    assert len(lines) > 5  # Original content + border lines


def test_generate_block_font_with_border():
    """Test block font with border."""
    result = asciigenator.generate("A", font="block", border="+")
    assert isinstance(result, str)
    assert len(result.strip()) > 0
    # Check for both block characters and border
    assert "█" in result or "╗" in result or "║" in result  # Block font characters
    assert "+" in result  # Border character
    lines = result.split("\n")
    # First and last lines should be all border characters
    assert all(char == "+" for char in lines[0])
    assert all(char == "+" for char in lines[-1])


def test_invalid_font():
    """Test error handling for invalid font."""
    try:
        asciigenator.generate("Hello", font="invalid_font")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Font 'invalid_font' not available" in str(e)


def test_invalid_color():
    """Test error handling for invalid color."""
    try:
        asciigenator.generate("Hello", font="simple", color="invalid_color")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Color 'invalid_color' not available" in str(e)


def test_list_fonts():
    """Test listing available fonts."""
    fonts = asciigenator.list_fonts()
    assert isinstance(fonts, list)
    assert "simple" in fonts
    assert "block" in fonts
    assert len(fonts) >= 2


def test_list_colors():
    """Test listing available colors."""
    colors = asciigenator.list_colors()
    assert isinstance(colors, list)
    assert "red" in colors
    assert "blue" in colors
    assert "green" in colors
    assert len(colors) >= 8  # Should have at least basic colors


def test_border_with_different_characters():
    """Test border with different border characters."""
    test_chars = ["#", "*", "=", "+", "-", "|"]

    for border_char in test_chars:
        result = asciigenator.generate("X", font="simple", border=border_char)
        assert isinstance(result, str)
        assert border_char in result
        lines = result.split("\n")
        # First and last lines should contain the border character
        assert border_char in lines[0]
        assert border_char in lines[-1]


def test_empty_border():
    """Test that None border doesn't add border."""
    result_no_border = asciigenator.generate("Test", font="simple")
    result_none_border = asciigenator.generate("Test", font="simple", border=None)
    assert result_no_border == result_none_border


def test_case_insensitive():
    """Test that text is converted to uppercase properly."""
    result_lower = asciigenator.generate("hello", font="simple")
    result_upper = asciigenator.generate("HELLO", font="simple")
    assert result_lower == result_upper


def run_cli(args):
    result = subprocess.run([sys.executable, "-m", "asciigenator.cli"] + args, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode


def test_list_fonts_api():
    """Test listing available fonts via API."""
    fonts = asciigenator.list_fonts()
    assert isinstance(fonts, list)
    assert "simple" in fonts
    assert "block" in fonts
    assert len(fonts) >= 2


def test_list_fonts_cli():
    """Test listing available fonts via CLI."""
    out, err, code = run_cli(["--list-fonts"])
    assert code == 0
    assert "simple" in out
    assert "block" in out


def test_generate_with_color_api():
    """Test ASCII generation with color via API."""
    result = asciigenator.generate("Hello", font="simple", color="red")
    assert "\033[31m" in result
    assert "\033[0m" in result
    assert "*" in result


def test_generate_with_color_cli():
    """Test ASCII generation with color via CLI."""
    out, err, code = run_cli(["Hi", "-c", "red"])
    assert code == 0
    assert "\033[31m" in out
    assert "\033[0m" in out


def test_generate_with_border_api():
    """Test border generation via API."""
    result = asciigenator.generate("Hi", font="simple", border="#")
    lines = result.split("\n")
    assert "#" in result
    assert all(char == "#" for char in lines[0])
    assert all(char == "#" for char in lines[-1])


def test_generate_with_border_cli():
    """Test border generation via CLI."""
    out, err, code = run_cli(["Hi", "-b", "#"])
    lines = out.splitlines()
    assert "#" in out
    assert "#" in lines[0]
    assert "#" in lines[-1]
