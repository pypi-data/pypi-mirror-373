from rich import prompt


def rich_warning(text: str) -> str:
    """
    Format a warning message with rich text.

    Args:
        text (str): The warning message to format.

    Returns:
        str: The formatted warning message.
    """
    return f'[dark_orange]{text}[/dark_orange]'


def rich_info(text: str) -> str:
    """
    Format an informational message with rich text.

    Args:
        text (str): The informational message to format.

    Returns:
        str: The formatted informational message.
    """
    return f'[blue]{text}[/blue]'


def rich_highlight(text: str) -> str:
    """
    Format a highlight message with rich text.

    Args:
        text (str): The highlight message to format.

    Returns:
        str: The formatted highlight message.
    """
    return f'[dark_cyan]{text}[/dark_cyan]'


def rich_error(text: str) -> str:
    """
    Format an error message with rich text.

    Args:
        text (str): The error message to format.

    Returns:
        str: The formatted error message.
    """
    return f'[red]{text}[/red]'


def rich_success(text: str) -> str:
    """
    Format a success message with rich text.

    Args:
        text (str): The success message to format.

    Returns:
        str: The formatted success message.
    """
    return f'[green]{text}[/green]'


def rich_highlight_version(text: str) -> str:
    """
    Format a version highlight message with rich text.

    Args:
        text (str): The version highlight message to format.

    Returns:
        str: The formatted version highlight message.
    """
    return f'[orange3]{text}[/orange3]'


def rich_command(text: str) -> str:
    return f'[dark_green]{text}[/dark_green]'


class CustomConfirm(prompt.Confirm):
    """
    Custom confirmation prompt class.

    Methods:
        process_response(value: str) -> bool: Convert choices to a boolean.
    """

    def process_response(self, value: str) -> bool:
        """
        Convert choices to a boolean.

        Args:
            value (str): The response value to process.

        Returns:
            bool: True if the response matches the first choice, False otherwise.

        Raises:
            prompt.InvalidResponse: If the response is not in the list of choices.
        """
        value = value.strip().lower()
        if value not in [c.lower() for c in self.choices]:
            raise prompt.InvalidResponse(self.validate_error_message)
        return value == self.choices[0]
