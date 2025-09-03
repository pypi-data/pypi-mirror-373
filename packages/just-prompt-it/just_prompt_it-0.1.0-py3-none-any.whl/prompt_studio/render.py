"""Standalone template rendering functionality."""

import re
from typing import Any, Dict

import jinja2

from .exceptions import TemplateRenderError


def preprocess_template(template_str: str) -> str:
    """
    Replace {{ var }} inside Jinja2 control block conditions with raw variable names.
    e.g., {% if {{variable_name}} %} -> {% if variable_name %}
    Supports complex expressions like {{ var.attr }} or {{ var[0] }}.
    Only replaces within control block conditions, not template content.
    Supported control blocks: block, for, if, elif, else, set, filter, macro, call, with,
    include, import, extends, raw, autoescape, trans, blocktrans.
    Reference: Jinja2 Template Designer Documentation (https://jinja.palletsprojects.com/en/3.1.x/templates/).

    Args:
        template_str (str): The Jinja2 template string to preprocess.

    Returns:
        str: The processed template string with variables replaced in control blocks.

    Raises:
        ValueError: If the template is malformed or processing fails.
    """
    try:
        # Define all supported control blocks
        control_blocks = r"block|for|if|elif|else|set|filter|macro|call|with|include|import|extends|raw|autoescape|trans|blocktrans"

        # Process each control block to replace variable expressions
        def replace_in_block(match):
            block_content = match.group(0)
            # Replace {{ expression }} with expression, preserving dots, brackets, and subscripts
            return re.sub(
                r"\{\{\s*([\w\[\]\.]+)\s*\}\}", r"\1", block_content, flags=re.DOTALL
            )

        # Match control blocks and apply replacement only within them
        processed = re.sub(
            rf"{{%\s*(?:{control_blocks})\s+[^%]*?%}}",
            replace_in_block,
            template_str,
            flags=re.DOTALL,
        )
        return processed
    except Exception as e:
        raise ValueError(f"Error processing template: {str(e)}")


def render(template: str, context: Dict[str, Any], strict: bool = True) -> str:
    """
    Render a Jinja2 template with the given data.

    Args:
        template: The template string.
        context: Dictionary of variables for rendering.
        strict: If True, raise errors on undefined variables.

    Returns:
        The rendered template string.

    Raises:
        TemplateRenderError: For template errors.
    """
    env = jinja2.Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=jinja2.StrictUndefined if strict else jinja2.Undefined,
    )
    try:
        jinja_template = env.from_string(preprocess_template(template).strip())
        return jinja_template.render(context)
    except jinja2.TemplateSyntaxError as e:
        raise TemplateRenderError(f"Template syntax error: {str(e)} (line {e.lineno})")
    except jinja2.UndefinedError as e:
        raise TemplateRenderError(f"Undefined variable in template: {str(e)}")
    except jinja2.TemplateError as e:
        raise TemplateRenderError(f"Error rendering template: {str(e)}")
