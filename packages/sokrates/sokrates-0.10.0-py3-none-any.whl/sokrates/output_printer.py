# This script defines the `OutputPrinter` class, a utility for printing
# formatted and colored output to the console. It centralizes various
# types of messages (headers, sections, info, success, warning, error, progress,
# and file creation notifications) to ensure consistent and visually
# appealing terminal feedback for the user.

from .colors import Colors

class OutputPrinter:
  """
  A utility class providing static methods for printing formatted and
  colored messages to the console. It uses ANSI escape codes for styling.
  """
  
  @staticmethod
  def print_header(title: str, color: str = Colors.BRIGHT_CYAN, width: int = 60) -> None:
    """
    Prints a decorative header with a title centered within borders.

    Args:
        title (str): The text to display as the header title.
        color (str): The ANSI color code for the header. Defaults to Colors.BRIGHT_CYAN.
        width (int): The total width of the header, including borders. Defaults to 60.
    """
    border = "═" * width
    print(f"\n{color}{Colors.BOLD}╔{border}╗{Colors.RESET}")
    print(f"{color}{Colors.BOLD}║{title.center(width)}{Colors.RESET}")
    print(f"{color}{Colors.BOLD}╚{border}╝{Colors.RESET}\n")

  @staticmethod
  def print(value: str, color = Colors.BRIGHT_YELLOW):
      """
      Prints a value with the specified color.

      Args:
          value (str): The text to print.
          color (str): The ANSI color code for the output. Defaults to Colors.BRIGHT_YELLOW.
      """
      print(f"{color}{value}{Colors.RESET}")
  
  @staticmethod
  def print_section(title: str, color: str = Colors.BRIGHT_BLUE, char: str = "─") -> None:
      """
      Prints a section separator with a title.

      Args:
          title (str): The text to display as the section title.
          color (str): The ANSI color code for the section. Defaults to Colors.BRIGHT_BLUE.
          char (str): The character used to draw the separator lines. Defaults to "─".
      """
      print(f"\n{color}{Colors.BOLD}{char * 50}{Colors.RESET}")
      print(f"{color}{Colors.BOLD} {title}{Colors.RESET}")
      print(f"{color}{Colors.BOLD}{char * 50}{Colors.RESET}")

  @staticmethod
  def print_info(label: str, value: str, label_color: str = Colors.BRIGHT_GREEN, value_color: str = Colors.WHITE) -> None:
      """
      Prints formatted information with a colored label and value.

      Args:
          label (str): The label for the information.
          value (str): The value of the information.
          label_color (str): The ANSI color code for the label. Defaults to Colors.BRIGHT_GREEN.
          value_color (str): The ANSI color code for the value. Defaults to Colors.WHITE.
      """
      print(f"{label_color}{Colors.BOLD}{label}:{Colors.RESET} {value_color}{value}{Colors.RESET}")

  @staticmethod
  def print_success(message: str) -> None:
      """
      Prints a success message with a checkmark icon.

      Args:
          message (str): The success message to display.
      """
      print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}✓ {message}{Colors.RESET}")

  @staticmethod
  def print_warning(message: str) -> None:
      """
      Prints a warning message with a warning icon.

      Args:
          message (str): The warning message to display.
      """
      print(f"{Colors.BRIGHT_YELLOW}{Colors.BOLD}⚠ {message}{Colors.RESET}")

  @staticmethod
  def print_error(message: str) -> None:
      """
      Prints an error message with an 'X' icon.

      Args:
          message (str): The error message to display.
      """
      print(f"{Colors.BRIGHT_RED}{Colors.BOLD}✗ {message}{Colors.RESET}")

  @staticmethod
  def print_progress(message: str) -> None:
      """
      Prints a progress message with a spinning arrow icon.

      Args:
          message (str): The progress message to display.
      """
      print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}⟳ {message}{Colors.RESET}")

  @staticmethod
  def print_file_created(filename: str) -> None:
      """
      Prints a message indicating that a file has been created, with the filename highlighted.

      Args:
          filename (str): The name or path of the created file.
      """
      print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}📄 Created: {Colors.RESET}{Colors.CYAN}{filename}{Colors.RESET}")
