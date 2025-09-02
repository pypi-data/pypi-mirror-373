"""
ASCII Art Generator supporting all letters A-Z (uppercase), space, colors, and borders.
"""

from typing import Dict, List
import re


class ASCIIGenerator:
    """ASCII Art Generator class with full alphabet support."""

    def __init__(self):
        self.fonts = self._load_fonts()
        self.colors = {
            "black": "\033[30m",
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "magenta": "\033[35m",
            "cyan": "\033[36m",
            "white": "\033[37m",
            "bright_black": "\033[90m",
            "bright_red": "\033[91m",
            "bright_green": "\033[92m",
            "bright_yellow": "\033[93m",
            "bright_blue": "\033[94m",
            "bright_magenta": "\033[95m",
            "bright_cyan": "\033[96m",
            "bright_white": "\033[97m",
        }
        self.reset = "\033[0m"

    def _load_fonts(self) -> Dict[str, Dict[str, List[str]]]:
        """Load full alphabet A-Z for simple and block fonts."""
        simple = {
            "A": [" * ", "* *", "***", "* *", "* *"],
            "B": ["** ", "* *", "** ", "* *", "** "],
            "C": [" **", "*  ", "*  ", "*  ", " **"],
            "D": ["** ", "* *", "* *", "* *", "** "],
            "E": ["***", "*  ", "** ", "*  ", "***"],
            "F": ["***", "*  ", "** ", "*  ", "*  "],
            "G": [" **", "*  ", "* *", "* *", " **"],
            "H": ["* *", "* *", "***", "* *", "* *"],
            "I": ["***", " * ", " * ", " * ", "***"],
            "J": ["  *", "  *", "  *", "* *", " * "],
            "K": ["* *", "** ", "*  ", "** ", "* *"],
            "L": ["*  ", "*  ", "*  ", "*  ", "***"],
            "M": ["*   *", "** **", "* * *", "*   *", "*   *"],
            "N": ["*   *", "**  *", "* * *", "*  **", "*   *"],
            "O": ["***", "* *", "* *", "* *", "***"],
            "P": ["** ", "* *", "** ", "*  ", "*  "],
            "Q": ["***", "* *", "* *", " **", "  *"],
            "R": ["** ", "* *", "** ", "* *", "* *"],
            "S": [" **", "*  ", " * ", "  *", "** "],
            "T": ["***", " * ", " * ", " * ", " * "],
            "U": ["* *", "* *", "* *", "* *", "***"],
            "V": ["* *", "* *", "* *", "* *", " * "],
            "W": ["*   *", "*   *", "* * *", "** **", "*   *"],
            "X": ["* *", "* *", " * ", "* *", "* *"],
            "Y": ["* *", "* *", " * ", " * ", " * "],
            "Z": ["***", "  *", " * ", "*  ", "***"],
            " ": ["   ", "   ", "   ", "   ", "   "],
        }

        block = {
            "A": ["  █  ", " █ █ ", "█████", "█   █", "█   █"],
            "B": ["████ ", "█   █", "████ ", "█   █", "████ "],
            "C": [" ████", "█    ", "█    ", "█    ", " ████"],
            "D": ["████ ", "█   █", "█   █", "█   █", "████ "],
            "E": ["█████", "█    ", "████ ", "█    ", "█████"],
            "F": ["█████", "█    ", "████ ", "█    ", "█    "],
            "G": [" ████", "█    ", "█  ██", "█   █", " ████"],
            "H": ["█   █", "█   █", "█████", "█   █", "█   █"],
            "I": ["█████", "  █  ", "  █  ", "  █  ", "█████"],
            "J": ["    █", "    █", "    █", "█   █", " ███ "],
            "K": ["█  █", "█ █ ", "██  ", "█ █ ", "█  █"],
            "L": ["█    ", "█    ", "█    ", "█    ", "█████"],
            "M": ["█   █", "██ ██", "█ █ █", "█   █", "█   █"],
            "N": ["█   █", "██  █", "█ █ █", "█  ██", "█   █"],
            "O": ["█████", "█   █", "█   █", "█   █", "█████"],
            "P": ["████ ", "█   █", "████ ", "█    ", "█    "],
            "Q": ["█████", "█   █", "█   █", "█  ██", "█████"],
            "R": ["████ ", "█   █", "████ ", "█  █ ", "█   █"],
            "S": [" ████", "█    ", " ███ ", "    █", "████ "],
            "T": ["█████", "  █  ", "  █  ", "  █  ", "  █  "],
            "U": ["█   █", "█   █", "█   █", "█   █", "█████"],
            "V": ["█   █", "█   █", "█   █", " █ █ ", "  █  "],
            "W": ["█   █", "█   █", "█ █ █", "██ ██", "█   █"],
            "X": ["█   █", " █ █ ", "  █  ", " █ █ ", "█   █"],
            "Y": ["█   █", " █ █ ", "  █  ", "  █  ", "  █  "],
            "Z": ["█████", "   █ ", "  █  ", " █   ", "█████"],
            " ": ["     ", "     ", "     ", "     ", "     "],
        }

        return {"simple": simple, "block": block}

    def _add_border(self, text: str, border_char: str, padding: int = 1) -> str:
        """Add border around ASCII text."""
        if not text.strip():
            return text
        lines = text.split("\n")
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        max_width = max(len(ansi_escape.sub("", line)) for line in lines)
        inner_width = max_width + 2 * padding
        border_width = inner_width + 2

        top = border_char * border_width
        bottom = border_char * border_width
        bordered_lines = [top]

        for _ in range(padding):
            bordered_lines.append(border_char + " " * inner_width + border_char)

        for line in lines:
            clean_line = ansi_escape.sub("", line)
            right_pad = " " * (inner_width - padding - len(clean_line))
            bordered_lines.append(border_char + " " * padding + line + right_pad + border_char)

        for _ in range(padding):
            bordered_lines.append(border_char + " " * inner_width + border_char)

        bordered_lines.append(bottom)
        return "\n".join(bordered_lines)

    def generate(self, text: str, font: str = "simple", color: str = None, border: str = None) -> str:
        if font not in self.fonts:
            raise ValueError(f"Font '{font}' not available.")
        if color and color not in self.colors:
            raise ValueError(f"Color '{color}' not available.")

        text = text.upper()
        font_data = self.fonts[font]

        # Determine height
        sample_char = next((c for c in text if c in font_data), " ")
        height = len(font_data.get(sample_char, font_data[" "]))

        lines = []
        for i in range(height):
            line = ""
            for char in text:
                char_lines = font_data.get(char, font_data.get(" ", [" " * len(font_data[sample_char][0])]))
                line += char_lines[i] if i < len(char_lines) else " " * len(char_lines[0])
                line += " "  # << add this space between letters
            lines.append(line.rstrip())

        result = "\n".join(lines)

        if color:
            result = f"{self.colors[color]}{result}{self.reset}"
        if border:
            result = self._add_border(result, border)
        return result

    def list_fonts(self) -> List[str]:
        return list(self.fonts.keys())

    def list_colors(self) -> List[str]:
        return list(self.colors.keys())


# Global instance
_generator = ASCIIGenerator()


def generate(text: str, font: str = "simple", color: str = None, border: str = None) -> str:
    return _generator.generate(text, font, color, border)


def list_fonts() -> List[str]:
    return _generator.list_fonts()


def list_colors() -> List[str]:
    return _generator.list_colors()
