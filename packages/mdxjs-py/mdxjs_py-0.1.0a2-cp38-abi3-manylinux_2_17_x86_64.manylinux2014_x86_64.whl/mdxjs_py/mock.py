"""Mock implementation for testing when Rust module isn't built."""

import re


def mock_compile(source: str, **_kwargs: object) -> str:
    """Mock MDX compilation for testing.

    Performs basic validation checks without actual compilation.
    """
    # Check for common MDX issues

    # Check for unclosed JSX tags
    unclosed_pattern = r"<(\w+)(?:\s[^>]*)?>"

    # Find all opening tags
    re.findall(unclosed_pattern, source)
    re.findall(r"</(\w+)>", source)

    # Simple check for template variables
    if re.search(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}", source):
        # Check if it's not in a code block
        code_blocks = re.findall(r"```[\s\S]*?```", source)
        source_without_code = source
        for block in code_blocks:
            source_without_code = source_without_code.replace(block, "")

        if re.search(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}", source_without_code):
            template_vars = re.findall(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", source_without_code)
            for var in template_vars:
                if "_" in var or var in ["content", "title", "next", "prev"]:
                    msg = f"1:1: Unexpected template variable: {{{var}}}"
                    raise ValueError(msg)

    # Check for unclosed code blocks
    backtick_count = source.count("```")
    if backtick_count % 2 != 0:
        msg = "Unclosed code block: missing closing ```"
        raise ValueError(msg)

    # Check for unclosed inline code
    lines = source.split("\n")
    for i, line in enumerate(lines):
        if "```" not in line:  # Skip code block lines
            tick_count = line.count("`")
            if tick_count % 2 != 0:
                msg = f"{i + 1}:1: Unclosed inline code: odd number of backticks"
                raise ValueError(msg)

    # If no errors, return mock compiled output
    return "// Mock compiled MDX\nfunction MDXContent() { return 'compiled'; }"
