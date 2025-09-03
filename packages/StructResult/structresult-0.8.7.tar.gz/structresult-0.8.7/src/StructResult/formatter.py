from typing import Callable


def format_eg(
        eg: ExceptionGroup,
        indent: int = 0,
        *,
        prefix: str = "  ",
        bullet: str = "- ",
        show_count: bool = True,
        repr_fn: Callable[[BaseException], str] = repr,
) -> str:
    """
    Formats an ExceptionGroup into a readable tree-like string representation.

    Args:
        eg: The ExceptionGroup to format
        indent: Current indentation level (default 0)
        prefix: String used for each indentation level (default two spaces)
        bullet: Marker for individual exceptions (default "- ")
        show_count: Whether to show sub-exception counts (default True)
        repr_fn: Function to convert exceptions to strings (default repr())

    Returns:
        Formatted string showing the exception hierarchy

    Example:
        >>> try:
        ...     raise ExceptionGroup("Root", [
        ...         ValueError("Invalid value"),
        ...         ExceptionGroup("Nested", [TypeError("Bad type")])
        ...     ])
        ... except ExceptionGroup as eg:
        ...     print(format_eg(eg))
        Root (2 sub-exceptions):
          - ValueError('Invalid value')
          Nested (1 sub-exception):
            - TypeError('Bad type')
    """
    current_prefix = prefix * indent
    count_info = f" ({len(eg.exceptions)} sub-exception{'s'[:len(eg.exceptions) != 1]})" if show_count else ""
    msg = [f"{current_prefix}{eg.message}{count_info}:"]

    for exc in eg.exceptions:
        if isinstance(exc, BaseExceptionGroup):
            # Recursively format nested ExceptionGroups
            msg.append(format_eg(
                exc,
                indent + 1,
                prefix=prefix,
                bullet=bullet,
                show_count=show_count,
                repr_fn=repr_fn,
            ))
        else:
            # Format regular exceptions with bullet points
            msg.append(f"{current_prefix}{prefix}{bullet}{repr_fn(exc)}")

    return "\n".join(msg)
