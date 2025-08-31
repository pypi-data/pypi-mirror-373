"""
Template rendering helper module for Jinja2 templates.

This module provides functionality for:
- Rendering templates with preservation of manual sections
- Handling template injection
- Managing template folders with automatic searching and conversion
- Support for preserving user-modified sections in regenerated files
"""

import logging
import os
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Set, Tuple, Type, Union
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template, UndefinedError


class RenderContext:  # pylint: disable=too-few-public-methods
    """Tracks filename and lineno for rendering/injection operations.

    Usage:
        context = RenderContext(filename="template.txt.j2", lineno=1)
        context.update(filename="other.txt", lineno=42)
        # Pass context to all rendering/injection functions to ensure
        # exceptions always include the correct filename and line number.
    """

    def __init__(self, filename="", lineno=1):
        self.filename = filename
        self.lineno = lineno

    def update(self, filename=None, lineno=None):
        """Update the render context with new filename or line number."""
        if filename is not None:
            self.filename = filename
        if lineno is not None:
            self.lineno = lineno


class ValidationContext:  # pylint: disable=too-few-public-methods
    """Context for injection validation containing template data and rendering context."""

    def __init__(self, template_str: str, pattern_match: re.Match, render_context: RenderContext):
        self.template_str = template_str
        self.pattern_match = pattern_match
        self.render_context = render_context
        self.remaining_content = template_str[pattern_match.end() :]
        self.pattern_offset = pattern_match.end()


class TemplateRendererException(Exception):
    """Exception with filename:lineno: message format for template errors."""

    def __init__(self, filename, lineno, message):
        # Create main error message with clickable file URI
        formatted_message = self._format_error_message(filename, lineno, message)
        super().__init__(formatted_message)
        self.filename = filename
        self.lineno = lineno
        self.message = message

    def _format_error_message(self, filename, lineno, message):
        """Format error message with clickable file URI when possible."""
        if not filename:
            return f'"":{lineno}: {message}'

        # Check if this is an inline template
        if filename.startswith("Inline template:"):
            return f"{filename}:{lineno}: {message}"

        # For template files, use intelligent path display
        basename = os.path.basename(filename)

        # Check if path needs file URI due to problematic characters (spaces, etc.)
        needs_file_uri = self._needs_file_uri(filename)

        if needs_file_uri:
            # For problematic paths, show clean error message, file URI below
            file_uri = self._create_file_uri(filename, lineno)
            return f"{message}\n    ↳ {file_uri}"

        # If the path contains template syntax in directory names,
        # we want to preserve the relative structure for context
        if "{{" in filename and "}}" in filename:
            # Extract meaningful relative path from template roots
            path_parts = filename.split(os.sep)

            # Find where template syntax starts in the path
            template_start_idx = -1
            for i, part in enumerate(path_parts):
                if "{{" in part and "}}" in part:
                    template_start_idx = i
                    break

            # If we found template syntax in directory names, preserve from that point
            if template_start_idx >= 0:
                relative_parts = path_parts[template_start_idx:]
                relative_path = "/".join(relative_parts)
                return f"{relative_path}:{lineno}: {message}"
            # Template syntax only in filename, just use basename
            return f"{basename}:{lineno}: {message}"

        # For very long paths, use basename
        if len(filename) > 80:
            return f"{basename}:{lineno}: {message}"
        # Standard format for simple paths
        return f"{filename}:{lineno}: {message}"

    def _needs_file_uri(self, filename):
        """Check if filename contains characters that break terminal clickability."""
        # Always use file URI format for paths with spaces (even inside template syntax)
        # This ensures clickability in terminals while keeping error messages clean
        return " " in filename

    def _create_file_uri(self, filename, lineno):
        """Create a clickable file URI with proper URL encoding."""
        # Convert to absolute path if not already
        if not filename.startswith("/"):
            # For relative paths, we'll use them as-is since we don't have context
            # to resolve them properly here
            abs_path = filename
        else:
            abs_path = filename

        # URL encode the path for proper file URI format
        # This includes encoding spaces and template syntax for clickability
        encoded_path = quote(abs_path, safe="/:")

        # Create file URI
        file_uri = f"file://{encoded_path}:{lineno}"
        return file_uri


class ManualSectionError(TemplateRendererException):
    """
    Exception raised when MANUAL SECTION validation fails.

    This occurs when there are issues with section structure,
    duplicate section IDs, or incompatible manual sections.
    """

    def __init__(self, filename, lineno, message="MANUAL SECTION validation failed"):
        super().__init__(filename, lineno, message)


def _remove_last_suffix(filename: str, extensions: Set[str]) -> str:
    """
    Remove the last suffix from a filename if it matches one of the given extensions.

    Args:
        filename: The filename to process
        extensions: Set of extensions to check against (without leading dot)

    Returns:
        The filename without the matched extension, or the original filename if no match
    """
    parts = filename.rsplit(".", 1)
    if len(parts) > 1 and parts[1] in extensions:
        return parts[0]
    return filename


class TemplateRenderer:
    """
    Template rendering helper class for Jinja2 templates.

    This class provides functionality to:
    - Render templates from strings or files
    - Preserve manually edited sections between template renders
    - Inject content into existing files using regex patterns
    - Process template directories to generate output directories
    """

    MANUAL_SECTION_START = "MANUAL SECTION START"
    MANUAL_SECTION_END = "MANUAL SECTION END"
    MANUAL_SECTION_ID = "[a-zA-Z0-9_-]+"
    MANUAL_SECTION_PATTERN = re.compile(
        rf"{MANUAL_SECTION_START}: ({MANUAL_SECTION_ID}(?:\s|$))(.*?){MANUAL_SECTION_END}",
        re.DOTALL,
    )
    # patterns to validate sections
    MANUAL_SECTION_CHECK_PATTERN = re.compile(
        rf"{MANUAL_SECTION_START}.*?{MANUAL_SECTION_END}",
        re.DOTALL,
    )

    INJECTION_TAG_START = "<!--"
    INJECTION_TAG_END = "-->"
    INJECTION_PATTERN = rf"{INJECTION_TAG_START} injection-pattern: " rf"(?P<name>[a-zA-Z0-9_-]+) {INJECTION_TAG_END}"
    INJECTION_STRING_START = f"{INJECTION_TAG_START} injection-string-start {INJECTION_TAG_END}"
    INJECTION_STRING_END = f"{INJECTION_TAG_START} injection-string-end {INJECTION_TAG_END}"

    def __init__(self, data: Any, data_name: str = "", filters: Dict[str, Callable] = None) -> None:
        """
        Initialize the TemplateRenderer with data for template rendering.

        Args:
            data: Object or dictionary containing the data for rendering
            data_name: If provided, data will be accessible in templates as data_name.attribute
            filters: Optional dictionary of custom Jinja2 filters

        Raises:
            ValueError: If data is not a dictionary or object with __dict__ attribute
        """
        self._env = Environment(keep_trailing_newline=True, undefined=StrictUndefined)
        if not isinstance(data, dict) and not hasattr(data, "__dict__"):
            raise ValueError("Object or dictionary expected")
        self._data: Dict[str, Any] = {data_name: data} if data_name else data
        self.add_data({"raise_exception": self._raise_exception})
        if filters:
            self.add_filters(filters)

    def _raise_exception(self, message: str) -> None:
        """Raise exception with message"""
        raise TemplateRendererException("", 1, message)

    def _check_manual_section_ids(self, data_string: str, data_name: str, context: RenderContext = None) -> List[str]:
        """
        Check manual section ids for invalid or duplicated ids
        """
        # Use finditer so we can map offending spans back to line numbers
        possible_iter = list(self.MANUAL_SECTION_CHECK_PATTERN.finditer(data_string))
        sections_iter = list(self.MANUAL_SECTION_PATTERN.finditer(data_string))
        if len(possible_iter) != len(sections_iter):
            # find the first possible-section that did not match the proper pattern
            bad_match = None
            for m in possible_iter:
                # check whether this span contains a proper section
                span_text = data_string[m.start() : m.end()]
                if not self.MANUAL_SECTION_PATTERN.search(span_text):
                    bad_match = m
                    break
            lineno = 1
            if bad_match is not None:
                lineno = data_string[: bad_match.start()].count("\n") + 1
            if context:
                context.update(filename=data_name, lineno=lineno)
            raise ManualSectionError(data_name, lineno, f"{data_name} has invalid section")
        sids = [m.group(1) for m in sections_iter]
        # check for duplicates
        duplicates = {sid for sid in sids if sids.count(sid) > 1}
        if duplicates:
            # try to locate first duplicate occurrence to show a meaningful line
            dup_sid = next(iter(duplicates))
            dup_match = None
            for m in sections_iter:
                if m.group(1) == dup_sid:
                    dup_match = m
                    break
            lineno = 1
            if dup_match is not None:
                lineno = data_string[: dup_match.start()].count("\n") + 1
            if context:
                context.update(filename=data_name, lineno=lineno)
            raise ManualSectionError(data_name, lineno, f"{data_name} has duplicated id: {duplicates}")
        # return list of ids
        return sids

    def _check_manual_section_structure(self, data_string: str, data_name: str, context: RenderContext = None) -> None:
        """
        Check manual section structure for completeness and nesting
        """
        # iterate matches with spans so we can compute lineno for nested problems
        matches = list(self.MANUAL_SECTION_CHECK_PATTERN.finditer(data_string))
        for m in matches:
            section = data_string[m.start() : m.end()]
            if section.count(self.MANUAL_SECTION_START) > 1 or section.count(self.MANUAL_SECTION_END) > 1:
                lineno = data_string[: m.start()].count("\n") + 1
                if context:
                    context.update(filename=data_name, lineno=lineno)
                raise ManualSectionError(data_name, lineno, f"Nested section in {data_name}: {section}")
        start_count = data_string.count(self.MANUAL_SECTION_START)
        end_count = data_string.count(self.MANUAL_SECTION_END)
        if start_count != end_count:
            # try to point to beginning of file or first unmatched marker
            lineno = 1
            # find first start/end mismatch by scanning markers
            start_positions = [m.start() for m in re.finditer(self.MANUAL_SECTION_START, data_string)]
            end_positions = [m.start() for m in re.finditer(self.MANUAL_SECTION_END, data_string)]
            if start_count > end_count and start_positions:
                lineno = data_string[: start_positions[-1]].count("\n") + 1
            elif end_count > start_count and end_positions:
                lineno = data_string[: end_positions[-1]].count("\n") + 1
            if context:
                context.update(filename=data_name, lineno=lineno)
            raise ManualSectionError(
                data_name,
                lineno,
                f"Incomplete section in {data_name}: start={start_count}, end={end_count}",
            )

    def _validate_manual_sections(
        self,
        temp: str,
        rendered: str,
        prev_rendered: str,
        context: RenderContext = None,
    ) -> None:
        """
        Validate manual sections in template, current rendered and previously rendered
        """
        self._check_manual_section_structure(temp, "template", context)
        self._check_manual_section_structure(rendered, "rendered", context)
        curr_sids = self._check_manual_section_ids(rendered, "rendered", context)
        if prev_rendered:
            self._check_manual_section_structure(prev_rendered, "prev_rendered", context)
            prev_sids = self._check_manual_section_ids(prev_rendered, "prev_rendered", context)
            for sid in prev_sids:
                if sid not in curr_sids:
                    # try to locate the missing section in the previous rendered string
                    lineno = 1
                    m = re.search(rf"{self.MANUAL_SECTION_START}: {re.escape(sid)}", prev_rendered)
                    if m:
                        lineno = prev_rendered[: m.start()].count("\n") + 1
                    else:
                        # fallback to template location if present
                        m2 = re.search(rf"{self.MANUAL_SECTION_START}: {re.escape(sid)}", temp)
                        if m2:
                            lineno = temp[: m2.start()].count("\n") + 1
                    if context:
                        context.update(filename="template", lineno=lineno)
                    raise ManualSectionError("template", lineno, f"New template lost manual section: {sid}")

    def add_types(self, *custom_types: Union[Type, Callable]) -> None:
        """
        Add types as global variables to the Jinja environment
        This is useful to make enum variants accessible
        """
        type_map = {ty.__name__: ty for ty in custom_types}
        self._env.globals.update(type_map)

    def add_data(self, data: Dict[str, Any]) -> None:
        """
        Add dictionary data to the Jinja environment
        """
        self._env.globals.update(**data)

    def add_filters(self, filters: Dict[str, Callable]) -> None:
        """
        Add custom filters to the Jinja2 environment

        Args:
            filters: Dictionary mapping filter names to filter functions
        """
        self._env.filters.update(filters)

    def _extract_jinja2_location(self, exc, default_filename, default_lineno=1):
        """Extract filename and lineno from Jinja2 exception or its cause/context."""
        for err in (
            exc,
            getattr(exc, "__cause__", None),
            getattr(exc, "__context__", None),
        ):
            if err is not None:
                filename = getattr(err, "filename", None)
                lineno = getattr(err, "lineno", None)
                if filename is not None and lineno is not None:
                    return filename, lineno
        return default_filename, default_lineno

    def _find_error_line(self, template_str: str, exc: Exception) -> int:
        """
        Try to find the line number where an error occurred in the template.

        Args:
            template_str: The template string
            exc: The exception that was raised

        Returns:
            Line number where error likely occurred, or 0 if not found
        """
        error_msg = str(exc)

        # Special handling for UndefinedError (missing variables)
        if isinstance(exc, UndefinedError):
            match = re.search(r"'(.+)' is undefined", error_msg)
            if match:
                missing_var = match.group(1)
                for idx, line in enumerate(template_str.splitlines(), 1):
                    if f"{{{{ {missing_var} }}}}" in line or f"{{{{{missing_var}}}}}" in line:
                        return idx

        # General approach: look for keywords from the error message in template lines
        # This helps with method call errors, attribute errors, etc.
        error_keywords = self._extract_error_keywords(error_msg)
        if error_keywords:
            for idx, line in enumerate(template_str.splitlines(), 1):
                if any(keyword in line for keyword in error_keywords):
                    return idx

        # Fallback: if no keywords found in error message, use template method names
        # This helps when the error message is generic but we can still locate method calls
        template_methods = self._find_template_methods(template_str)
        if template_methods:
            for idx, line in enumerate(template_str.splitlines(), 1):
                if any(method in line for method in template_methods):
                    return idx

        return 0  # Could not determine line number

    def _extract_error_keywords(self, error_msg: str) -> List[str]:
        """
        Extract relevant keywords from an error message that might help locate
        the error in the template.
        """
        keywords = []

        # Look for method names (e.g., "getter_expression")
        method_match = re.search(r"(\w+)\s*\(\)", error_msg)
        if method_match:
            keywords.append(method_match.group(1))

        # Look for attribute names (e.g., "specialValueADAS_Long_AebAxReqDetailedState")
        # Match identifiers that are likely to be unique in the template
        identifier_matches = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]{3,}\b", error_msg)
        for identifier in identifier_matches:
            # Filter out common English words and focus on technical identifiers
            if not identifier.lower() in {
                "must",
                "have",
                "defined",
                "call",
                "error",
                "exception",
                "missing",
                "generic",
                "message",
            }:
                keywords.append(identifier)

        return keywords

    def _find_template_methods(self, template_str: str) -> List[str]:
        """
        Extract method names from template expressions to help locate errors
        when the error message doesn't contain useful keywords.
        """
        # Find all method calls in Jinja2 expressions: {{ obj.method() }}
        method_pattern = re.compile(r"{{\s*[\w.]*\.(\w+)\s*\([^}]*\)\s*}}")
        methods = []
        for match in method_pattern.finditer(template_str):
            methods.append(match.group(1))
        return methods

    def __render_from_string(self, template_str: str, template_path: str = "", context: RenderContext = None) -> str:
        """Render template from string with filename set correctly in case of exception"""

        name = f'Inline template: "{template_str}"' if not template_path else str(template_path)
        if context is None:
            context = RenderContext(name, 1)
        else:
            context.update(filename=name)

        global_vars = self._env.make_globals(None)
        template_class: Type[Template] = getattr(self._env, "template_class")
        try:
            template = template_class.from_code(
                self._env,
                self._env.compile(template_str, filename=name, name=name),
                global_vars,
                None,
            )
            return template.render(**self._data)
        except Exception as exc:
            filename, lineno = self._extract_jinja2_location(exc, name)
            context.update(filename=filename, lineno=lineno)

            # If Jinja2 didn't provide line info, try to find it ourselves
            if lineno == 1:  # Default lineno means no line info was found
                detected_lineno = self._find_error_line(template_str, exc)
                if detected_lineno:
                    context.update(lineno=detected_lineno)

            raise TemplateRendererException(context.filename, context.lineno, str(exc)) from exc

    def render_string(
        self,
        temp: str,
        prev_rendered_string: str = "",
        template_path: str = "",
        context: RenderContext = None,
    ) -> str:
        """
        Render template string; preserve manual sections if they exist
        `template_path` is shown in the exception when Jinja2 fails. If it is `None`,
        the exception will instead print the entire template.
        """
        if context is None:
            context = RenderContext(template_path or "inline", 1)
        rendered_string = self.__render_from_string(temp, template_path, context)
        self._validate_manual_sections(temp, rendered_string, prev_rendered_string)
        if prev_rendered_string:
            manual_sections = self.MANUAL_SECTION_PATTERN.findall(prev_rendered_string)
            if manual_sections:
                for section_id, content in manual_sections:
                    section_pattern = re.compile(
                        rf"{self.MANUAL_SECTION_START}: {section_id}.*?{self.MANUAL_SECTION_END}",
                        re.DOTALL,
                    )
                    rendered_string = section_pattern.sub(
                        f"{self.MANUAL_SECTION_START}: {section_id}" + content + f"{self.MANUAL_SECTION_END}",
                        rendered_string,
                    )
        return rendered_string

    def _validate_tag_spacing(
        self, template_str: str, tag_match: re.Match, tag_name: str, context: RenderContext
    ) -> None:
        """Validate spacing around a tag."""
        lineno = template_str[: tag_match.start()].count("\n") + 1
        tag_start, tag_end = tag_match.start(), tag_match.end()

        if tag_start > 0 and not template_str[tag_start - 1].isspace():
            context.update(lineno=lineno)
            raise TemplateRendererException(
                context.filename, context.lineno, f"No space before {tag_name} - whitespace required"
            )
        if tag_end < len(template_str) and not template_str[tag_end].isspace():
            context.update(lineno=lineno)
            raise TemplateRendererException(
                context.filename, context.lineno, f"No space after {tag_name} - whitespace required"
            )

    def _validate_injection_start_tag(self, val_ctx: ValidationContext) -> re.Match:
        """Find and validate injection-string-start tag."""
        pattern_lineno = val_ctx.template_str[: val_ctx.pattern_match.start()].count("\n") + 1

        start_match = re.search(re.escape(self.INJECTION_STRING_START), val_ctx.remaining_content)
        if not start_match:
            val_ctx.render_context.update(lineno=pattern_lineno)
            raise TemplateRendererException(
                val_ctx.render_context.filename,
                val_ctx.render_context.lineno,
                f"Missing '{self.INJECTION_STRING_START}' after injection pattern",
            )

        # Validate spacing around start tag
        start_pos_in_template = val_ctx.pattern_offset + start_match.start()
        start_lineno = val_ctx.template_str[:start_pos_in_template].count("\n") + 1

        if start_match.start() > 0 and not val_ctx.remaining_content[start_match.start() - 1].isspace():
            val_ctx.render_context.update(lineno=start_lineno)
            raise TemplateRendererException(
                val_ctx.render_context.filename,
                val_ctx.render_context.lineno,
                f"No space before '{self.INJECTION_STRING_START}' - whitespace required",
            )

        if (
            start_match.end() < len(val_ctx.remaining_content)
            and not val_ctx.remaining_content[start_match.end()].isspace()
        ):
            val_ctx.render_context.update(lineno=start_lineno)
            raise TemplateRendererException(
                val_ctx.render_context.filename,
                val_ctx.render_context.lineno,
                f"No space after '{self.INJECTION_STRING_START}' - whitespace required",
            )
        return start_match

    def _validate_injection_end_tag(self, val_ctx: ValidationContext, start_match: re.Match) -> None:
        """Find and validate injection-string-end tag."""
        end_match = re.search(re.escape(self.INJECTION_STRING_END), val_ctx.remaining_content[start_match.end() :])
        if not end_match:
            start_pos_in_template = val_ctx.pattern_offset + start_match.start()
            start_lineno = val_ctx.template_str[:start_pos_in_template].count("\n") + 1
            val_ctx.render_context.update(lineno=start_lineno)
            raise TemplateRendererException(
                val_ctx.render_context.filename,
                val_ctx.render_context.lineno,
                f"Missing '{self.INJECTION_STRING_END}' after '{self.INJECTION_STRING_START}'",
            )

        # Validate spacing around end tag
        end_pos_in_template = val_ctx.pattern_offset + start_match.end() + end_match.start()
        end_lineno = val_ctx.template_str[:end_pos_in_template].count("\n") + 1

        if end_match.start() > 0:
            content_between = val_ctx.remaining_content[start_match.end() : start_match.end() + end_match.start()]
            if content_between and not content_between[-1].isspace():
                val_ctx.render_context.update(lineno=end_lineno)
                raise TemplateRendererException(
                    val_ctx.render_context.filename,
                    val_ctx.render_context.lineno,
                    f"No space before '{self.INJECTION_STRING_END}' - whitespace required",
                )

        end_end_pos = start_match.end() + end_match.end()
        if end_end_pos < len(val_ctx.remaining_content) and not val_ctx.remaining_content[end_end_pos].isspace():
            val_ctx.render_context.update(lineno=end_lineno)
            raise TemplateRendererException(
                val_ctx.render_context.filename,
                val_ctx.render_context.lineno,
                f"No space after '{self.INJECTION_STRING_END}' - whitespace required",
            )

    def _validate_injection_pattern_block(
        self, template_str: str, pattern_match: re.Match, context: RenderContext
    ) -> None:
        """Validate a single injection pattern block."""
        # Validate pattern tag spacing
        self._validate_tag_spacing(
            template_str, pattern_match, "injection pattern tag '<!-- injection-pattern: ...'", context
        )

        # Create validation context to reduce parameter passing
        val_ctx = ValidationContext(template_str, pattern_match, context)

        # Find and validate start tag
        start_match = self._validate_injection_start_tag(val_ctx)

        # Find and validate end tag
        self._validate_injection_end_tag(val_ctx, start_match)

    def _validate_injection_syntax(self, template_str: str, context: RenderContext = None) -> None:
        """
        Validate the complete syntax of an injection file before processing.

        Args:
            template_str: The template string to validate
            context: Render context for error reporting

        Raises:
            TemplateRendererException: If injection file syntax is invalid
        """
        if context is None:
            context = RenderContext("inline", 1)

        injection_patterns = list(re.finditer(self.INJECTION_PATTERN, template_str))
        for pattern_match in injection_patterns:
            self._validate_injection_pattern_block(template_str, pattern_match, context)

    def inject_string(
        self,
        temp: str,
        prev_rendered_string: str,
        template_path: str = "",
        context: RenderContext = None,
    ) -> str:
        """
        Render template & inject content to the previous rendered string.

        This method processes injection patterns in the template and applies them
        to matching sections in the previous rendered string.

        Args:
            temp: The template string containing injection patterns
            prev_rendered_string: The previously rendered string to modify
            template_path: Optional path to the template (for error reporting)

        Returns:
            The modified string with injections applied

        Raises:
            TemplateRendererException: If injection patterns are invalid
        """
        if context is None:
            context = RenderContext(template_path or "inline", 1)

        # Validate injection syntax before rendering
        self._validate_injection_syntax(temp, context)

        rendered_string = self.__render_from_string(temp, template_path, context)
        modifications: List[Tuple[int, int, str]] = []

        for match in re.finditer(self.INJECTION_PATTERN, rendered_string):
            label = match.group("name")
            section_bodies = rendered_string[match.end() :].split(self.INJECTION_STRING_START)
            pattern_text = section_bodies[0].strip()
            # validate the regex pattern
            try:
                re.compile(pattern_text)
            except re.error as e:
                # compute lineno from match position in rendered_string
                lineno = rendered_string[: match.start()].count("\n") + 1
                if context:
                    context.update(lineno=lineno)
                raise TemplateRendererException(
                    context.filename,
                    context.lineno,
                    f"Invalid regex pattern '{pattern_text}': {e}",
                ) from e
            # validate if 'injection' named capture group exists
            if "(?P<injection>" not in pattern_text:
                lineno = rendered_string[: match.start()].count("\n") + 1
                if context:
                    context.update(lineno=lineno)
                raise TemplateRendererException(
                    context.filename,
                    context.lineno,
                    f"Invalid regex pattern '{pattern_text}': no 'injection' named capture group",
                )
            injection_string = section_bodies[1].split(self.INJECTION_STRING_END)[0]
            self._apply_injections(prev_rendered_string, pattern_text, injection_string, modifications)
            if not modifications:
                logging.warning("Failed to inject '%s':\n%s", label, pattern_text)

        return self._apply_modifications(prev_rendered_string, modifications)

    def _apply_injections(
        self,
        prev_rendered_string: str,
        pattern_text: str,
        injection_string: str,
        modifications: List[Tuple[int, int, str]],
    ) -> None:
        """
        Apply injections based on the pattern and injection string.

        Args:
            prev_rendered_string: The previously rendered string to modify
            pattern_text: The regex pattern to match in the string
            injection_string: The string to inject
            modifications: List to collect the modifications (start, end, replacement)
        """
        for m in re.finditer(pattern_text, prev_rendered_string):
            injection_start = m.start("injection")
            injection_end = m.end("injection")
            modifications.append((injection_start, injection_end, injection_string))

    def _apply_modifications(self, prev_rendered_string: str, modifications: List[Tuple[int, int, str]]) -> str:
        """
        Apply modifications to the previous rendered string.

        Args:
            prev_rendered_string: The string to modify
            modifications: List of tuples (start, end, replacement)

        Returns:
            The modified string with all replacements applied
        """
        modifications.sort(key=lambda x: x[0])
        modified_buffer = []
        last_pos = 0

        for injection_start, injection_end, injection_string in modifications:
            modified_buffer.append(prev_rendered_string[last_pos:injection_start])
            modified_buffer.append(injection_string)
            last_pos = injection_end

        # append the remaining part of the original string
        modified_buffer.append(prev_rendered_string[last_pos:])

        return "".join(modified_buffer)

    def render_file(
        self,
        temp_filepath: Union[Path, str],
        prev_rendered_string: str = "",
        context: RenderContext = None,
    ) -> str:
        """
        Render template with given template file path; preserve manual sections if they exist
        """
        temp_filepath = Path(temp_filepath)
        if not isinstance(temp_filepath, Path):
            temp_filepath = Path(temp_filepath)
        if context is None:
            context = RenderContext(str(temp_filepath), 1)
        with temp_filepath.open(mode="r", encoding="utf-8") as temp_file:
            temp_string = temp_file.read()
            rendered_string = self.render_string(temp_string, prev_rendered_string, str(temp_filepath), context)
        return rendered_string

    def _is_text_file(self, filepath: Path) -> bool:
        """
        Check if the file is a text file by attempting to read it as UTF-8.

        Args:
            filepath: Path to the file to check

        Returns:
            True if file can be read as UTF-8 text and is not empty, False otherwise
        """
        try:
            content = filepath.read_bytes()
            if not content:
                return False
            if b"\x00" in content:
                return False
            content.decode("utf-8")
            return True
        except (UnicodeDecodeError, IOError):
            return False

    def generate_file(
        self,
        temp_filepath: Union[Path, str],
        output_filepath: Union[Path, str],
        only_template_files: bool = True,
        context: RenderContext = None,
    ) -> None:
        """
        Render the given template file and generate the output file.

        This method handles different template types:
        - .j2 files: Jinja2 templates that get rendered
        - .inj files: Templates for injecting content into existing files
        - Other files: Can be copied as-is depending on only_template_files flag

        Special feature: Empty output filenames (rendered as "") are skipped.
        This allows conditional file generation through template naming, e.g.:
        {{"interface" if temp_data.has_interface else ""}}.hpp.j2

        Args:
            temp_filepath: Path to the template file
            output_filepath: Path to the output file
            only_template_files: When True, only render files with .j2 or .inj extensions

        Raises:
            TemplateRendererException: If injection target doesn't exist
        """
        temp_filepath = Path(temp_filepath)
        output_filepath = Path(output_filepath)

        # Initialize context if not provided
        if context is None:
            context = RenderContext(str(temp_filepath), 1)

        output_filename = output_filepath.stem
        if not output_filename:
            logging.info("skip output filename: %s", output_filepath)
            return
        if not self._is_text_file(temp_filepath):
            logging.error("Invalid template file: %s", temp_filepath)
            return

        temp_string = self._read_file(temp_filepath)
        self._env.loader = FileSystemLoader(temp_filepath.parent)
        prev_rendered_string = self._read_file(output_filepath) if output_filepath.exists() else ""

        if temp_filepath.suffix == ".inj":
            if not prev_rendered_string:
                context.update(filename=str(output_filepath), lineno=1)
                raise TemplateRendererException(
                    context.filename,
                    context.lineno,
                    f"{output_filepath} is required for injection",
                )
            rendered_string = self.inject_string(temp_string, prev_rendered_string, str(temp_filepath), context)
        elif temp_filepath.suffix != ".j2" and only_template_files:
            rendered_string = temp_string
        else:
            rendered_string = self.render_string(temp_string, prev_rendered_string, str(temp_filepath), context)

        output_filepath.parent.mkdir(parents=True, exist_ok=True)
        self._write_file(output_filepath, rendered_string)
        logging.info("=> %s generated!", output_filepath)

    def _read_file(self, filepath: Path) -> str:
        """
        Read the content of a file.

        Args:
            filepath: Path to the file to read

        Returns:
            The file content as string, or empty string if file doesn't exist
        """
        if filepath.exists():
            with filepath.open(mode="r", encoding="utf-8") as file:
                return file.read()
        return ""

    def _write_file(self, filepath: Path, content: str) -> None:
        """
        Write content to a file.

        Args:
            filepath: Path to the file to write
            content: Content to write to the file
        """
        with filepath.open(mode="w", encoding="utf-8") as file:
            file.write(content)

    def generate(
        self,
        temp_path: Union[Path, str],
        output_dir: Union[Path, str],
        only_template_files: bool = True,
    ) -> None:
        """
        Main function to render template files and generate output files.

        This function handles both file and directory templates. For directories,
        it recursively processes all files and subdirectories.

        Args:
            temp_path: Path to the template file or directory
            output_dir: Path to the output directory
            only_template_files: When True, only render files with .j2 or .inj extensions
                but still copy other files from the template folder

        Raises:
            FileNotFoundError: If the template path doesn't exist
        """
        temp_path = Path(temp_path)
        if not temp_path.exists():
            temp_path = Path(self.render_string(str(temp_path)))
        output_dir = Path(output_dir)

        if temp_path.exists():
            if temp_path.is_file():
                output_filename = _remove_last_suffix(self.render_string(str(temp_path.name)), {"j2", "inj"})
                if output_filename:
                    output_filepath = output_dir / output_filename
                    self.generate_file(temp_path, output_filepath, only_template_files)
            elif temp_path.is_dir():
                filename_pattern = "*"
                temp_files = [file for file in temp_path.rglob(filename_pattern) if file.is_file()]
                for temp_filepath in temp_files:
                    # render folder or file name in Path and remove j2 suffix
                    output_filename = _remove_last_suffix(self.render_string(str(temp_filepath.name)), {"j2", "inj"})
                    if output_filename:
                        output_filepath = Path(
                            _remove_last_suffix(
                                self.render_string(str(temp_filepath)),
                                {"j2", "inj"},
                            )
                        )
                        output_filepath = output_dir / output_filepath.relative_to(temp_path)
                        self.generate_file(temp_filepath, output_filepath, only_template_files)
        else:
            raise FileNotFoundError(f"File not found: {temp_path}")
