from __future__ import annotations

import json
from dataclasses import dataclass, is_dataclass
from typing import Any, Callable, Dict, List

import markdown

from h2o_mlops import _core, _utils


class SchemaDocumentation:
    """Wrapper for schema objects to provide rich documentation in Jupyter."""

    def __init__(self, schema: Dict):
        """
        Initialize with a schema object.

        Args:
            schema (dict): The JSON schema dictionary
        """
        self.schema: Dict = schema
        self.name = schema.get("title", "Schema")
        self.description = schema.get("description", "")

    def _repr_html_(self) -> str:
        """
        Generate HTML representation for Jupyter.
        This method is automatically called when the object is displayed in Jupyter.
        """
        css = """
        <style>
            .schema-container {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.5;
                color: #24292e;
                background-color: #fff;
                max-width: 800px;
                margin: 0 auto;
                padding: 10px 20px;
                border-radius: 5px;
                border: 1px solid #e1e4e8;
            }
            .schema-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding-bottom: 8px;
                border-bottom: 1px solid #e1e4e8;
                margin-bottom: 16px;
            }
            .schema-title {
                font-size: 1.5em;
                font-weight: 600;
                margin: 0;
                color: #24292e;
            }
            .schema-type {
                font-size: 0.9em;
                color: #6a737d;
                margin: 0;
                padding: 4px 8px;
                background-color: #f6f8fa;
                border-radius: 3px;
            }
            .schema-description {
                margin: 8px 0 16px;
                padding-bottom: 8px;
                border-bottom: 1px solid #e1e4e8;
            }
            .properties-container {
                margin-top: 16px;
            }
            .property-row {
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #f0f0f0;
            }
            .property-row:hover {
                background-color: #f6f8fa;
            }
            .property-name {
                flex: 1;
                font-weight: 500;
                color: #0366d6;
            }
            .property-type {
                flex: 1;
                font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
                color: #6f42c1;
            }
            .property-required {
                font-weight: 600;
                color: #d73a49;
            }
            .property-details {
                flex: 2;
                color: #24292e;
            }
            .toggle-button {
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                padding: 2px 8px;
                border-radius: 3px;
                font-size: 0.8em;
                cursor: pointer;
                margin-left: 8px;
            }
            .example-container {
                margin-top: 16px;
                padding: 16px;
                background-color: #f6f8fa;
                border-radius: 5px;
                border: 1px solid #e1e4e8;
            }
            .example-header {
                font-weight: 600;
                margin-bottom: 8px;
            }
            .example-code {
                font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
                font-size: 0.9em;
                white-space: pre;
                background-color: transparent;
                padding: 0;
                margin: 0;
            }
            .collapsible-header {
                cursor: pointer;
                padding: 8px;
                width: 100%;
                border: none;
                text-align: left;
                outline: none;
                font-size: 15px;
                margin-bottom: 1px;
                background-color: #f6f8fa;
                border-radius: 3px;
            }
            .active, .collapsible-header:hover {
                background-color: #e1e4e8;
            }
            .collapsible-content {
                padding: 0 8px;
                max-height: 0;
                overflow: hidden;
                transition: max-height 0.2s ease-out;
            }
            .schema-footer {
                margin-top: 16px;
                padding-top: 8px;
                border-top: 1px solid #e1e4e8;
                font-size: 0.9em;
                color: #6a737d;
            }
        </style>
        """  # noqa: E501

        schema_type = self.schema.get("type", "object")

        html = f"""
        {css}
        <div class="schema-container">
            <div class="schema-header">
                <h3 class="schema-title">{self.name}</h3>
                <span class="schema-type">{schema_type}</span>
            </div>
            <div class="schema-description">{self.description}</div>
        """

        # Generate properties section
        if "properties" in self.schema:
            required_props = self.schema.get("required", [])

            html += """
            <div class="properties-container">
                <h4>Properties</h4>
            """

            for prop_name, prop_details in self.schema["properties"].items():
                prop_type = prop_details.get("type", "any")
                if isinstance(prop_type, list):
                    prop_type = " | ".join(prop_type)
                description = markdown.markdown(prop_details.get("description", ""))
                required = prop_name in required_props
                required_text = (
                    '<span class="property-required">Required</span>'
                    if required
                    else ""
                )

                default_value = ""
                if "default" in prop_details:
                    default_val = prop_details["default"]
                    if default_val is None:
                        default_value = "Default: None"
                    elif isinstance(default_val, (str, int, float, bool)):
                        default_value = f"Default: {default_val}"
                    else:
                        default_value = f"Default: {type(default_val).__name__}"

                html += f"""
                <div class="property-row">
                    <div class="property-name">{prop_name} {required_text}</div>
                    <div class="property-type">{prop_type}</div>
                    <div class="property-details">
                        {description}
                        {f'<br><small>{default_value}</small>' if default_value else ''}
                    </div>
                </div>
                """

            html += "</div>"  # Close properties-container

        # Create example section
        example_obj = {}
        if "properties" in self.schema:
            for prop_name, prop_details in self.schema["properties"].items():
                if "example" in prop_details:
                    example_obj[prop_name] = prop_details["example"]
                elif prop_details.get("type") == "string":
                    example_obj[prop_name] = "string_value"
                elif prop_details.get("type") == "integer":
                    example_obj[prop_name] = 42
                elif prop_details.get("type") == "number":
                    example_obj[prop_name] = 42.5
                elif prop_details.get("type") == "boolean":
                    example_obj[prop_name] = True
                elif prop_details.get("type") == "array":
                    example_obj[prop_name] = []
                elif prop_details.get("type") == "object":
                    example_obj[prop_name] = {}

        if example_obj:
            example_json = json.dumps(example_obj, indent=2)
            html += f"""
            <div class="example-container">
                <div class="example-header">Example:</div>
                <pre class="example-code">{example_json}</pre>
            </div>
            """

        # Add raw schema toggle
        html += f"""
        <div class="schema-footer">
            <button class="collapsible-header">Show Raw Schema</button>
            <div class="collapsible-content">
                <pre class="example-code">{json.dumps(self.schema, indent=2)}</pre>
            </div>
        </div>
        """

        # Add JavaScript for collapsible content
        html += """
        <script>
            (function() {
                var coll = document.getElementsByClassName("collapsible-header");
                for (var i = 0; i < coll.length; i++) {
                    coll[i].addEventListener("click", function() {
                        this.classList.toggle("active");
                        var content = this.nextElementSibling;
                        if (content.style.maxHeight) {
                            content.style.maxHeight = null;
                        } else {
                            content.style.maxHeight = content.scrollHeight + "px";
                        }
                    });
                }
            })();
        </script>
        """

        html += "</div>"  # Close schema-container
        return html

    def _repr_markdown_(self) -> str:
        """Generate Markdown representation for environments that don't support HTML."""
        markdown = f"# {self.name}\n\n{self.description}\n\n"

        if "properties" in self.schema:
            required_props = self.schema.get("required", [])
            markdown += "## Properties\n\n"

            for prop_name, prop_details in self.schema["properties"].items():
                prop_type = prop_details.get("type", "any")
                if isinstance(prop_type, list):
                    prop_type = " | ".join(prop_type)
                description = prop_details.get("description", "")
                required = prop_name in required_props
                required_text = " (Required)" if required else ""

                default_value = ""
                if "default" in prop_details:
                    default_val = prop_details["default"]
                    if default_val is None:
                        default_value = "Default: None"
                    elif isinstance(default_val, (str, int, float, bool)):
                        default_value = f"Default: {default_val}"
                    else:
                        default_value = f"Default: {type(default_val).__name__}"

                markdown += f"### {prop_name}{required_text}\n"
                markdown += f"**Type:** {prop_type}\n\n"
                markdown += f"{description}\n\n"
                if default_value:
                    markdown += f"{default_value}\n\n"

        return markdown

    def __repr__(self) -> str:
        """String representation for non-notebook environments."""
        return f"{self.name} Schema: {self.description}"


class DisplayMixin:
    """
    A mixin class to provide rich display capabilities to dataclasses.

    This mixin adds _repr_html_ and _repr_markdown_ methods to any class it's mixed with,
    enabling rich display in Jupyter notebooks and other compatible environments.
    """  # noqa: E501

    def _get_css(self) -> str:
        """Return the CSS styles for HTML representation."""
        return """
        <style>
            .spec-container {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.5;
                max-width: 900px;
                margin: 0 auto;
                padding: 0;
            }
            .spec-header {
                background-color: #f5f5f5;
                border: 1px solid #e1e4e8;
                border-radius: 5px 5px 0 0;
                padding: 12px 16px;
                margin-bottom: 0;
            }
            .spec-title {
                font-size: 1.4em;
                font-weight: 600;
                margin: 0 0 4px 0;
                color: #24292e;
            }
            .spec-subtitle {
                font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
                font-size: 0.9em;
                color: #6a737d;
                margin: 0;
            }
            .spec-description {
                margin: 8px 0 0 0;
                color: #24292e;
            }
            .spec-body {
                border: 1px solid #e1e4e8;
                border-top: none;
                border-radius: 0 0 5px 5px;
                padding: 16px;
                background-color: #ffffff;
            }
            .spec-section {
                margin-bottom: 16px;
                padding-bottom: 16px;
                border-bottom: 1px solid #e1e4e8;
            }
            .spec-section:last-child {
                border-bottom: none;
                margin-bottom: 0;
                padding-bottom: 0;
            }
            .spec-section-title {
                font-size: 1.1em;
                font-weight: 600;
                margin: 0 0 8px 0;
                color: #24292e;
            }
            .spec-property {
                margin-bottom: 8px;
                display: flex;
                flex-wrap: wrap;
            }
            .spec-property-label {
                font-weight: 500;
                width: 200px;
                color: #24292e;
            }
            .spec-property-value {
                flex: 1;
                min-width: 200px;
                word-break: break-word;
            }
            .tag-container {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 4px;
            }
            .tag {
                display: inline-block;
                padding: 2px 8px;
                font-size: 0.85em;
                line-height: 1.6;
                border-radius: 3px;
                background-color: #f1f8ff;
                color: #0366d6;
                border: 1px solid #c8e1ff;
            }
            .path-tag {
                background-color: #f1f8e9;
                color: #43a047;
                border: 1px solid #c5e1a5;
            }
            .mime-tag {
                background-color: #e8f5e9;
                color: #2e7d32;
                border: 1px solid #a5d6a7;
            }
            .schema-tag {
                background-color: #fff3e0;
                color: #e65100;
                border: 1px solid #ffe0b2;
            }
            .toggle-button {
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                padding: 4px 10px;
                border-radius: 3px;
                font-size: 0.9em;
                cursor: pointer;
                color: #24292e;
                margin-top: 8px;
            }
            .toggle-button:hover {
                background-color: #e1e4e8;
            }
            .collapsible-content {
                padding: 0;
                max-height: 0;
                overflow: hidden;
                transition: max-height 0.3s ease-out;
            }
            .badge {
                display: inline-block;
                padding: 2px 6px;
                font-size: 0.75em;
                font-weight: 500;
                line-height: 1.4;
                border-radius: 10px;
                margin-left: 8px;
                vertical-align: middle;
            }
            .source-badge {
                background-color: #dff2fa;
                color: #0184bc;
            }
            .sink-badge {
                background-color: #ffd8b8;
                color: #cb5f00;
            }
        </style>
        """  # noqa: E501

    def _get_object_type_badge(self) -> str:
        """Return HTML for a badge indicating the object type."""
        class_name = self.__class__.__name__.lower()
        badge_type = ""

        if "source" in class_name:
            badge_type = "source-badge"
            label = "Source"
        elif "sink" in class_name:
            badge_type = "sink-badge"
            label = "Sink"
        else:
            # Default badge if type can't be determined
            badge_type = ""
            label = (
                class_name.replace("MLOps", "").replace("Batch", "").replace("Spec", "")
            )

        return f'<span class="badge {badge_type}">{label}</span>'

    def _generate_id(self) -> str:
        """Generate a unique ID for HTML elements."""
        # Use object id to ensure uniqueness
        return f"spec-{id(self)}"

    def _format_list_as_tags(self, items: List[str], tag_class: str = "") -> str:
        """Format a list of items as HTML tags."""
        if not items:
            return "<em>None</em>"

        return "".join(f'<span class="tag {tag_class}">{item}</span>' for item in items)

    def _render_schema_html(self, schema_obj: SchemaDocumentation) -> str:
        """Render schema object as HTML."""
        if hasattr(schema_obj, "_repr_html_"):
            return schema_obj._repr_html_()
        elif isinstance(schema_obj, dict):
            return f"<pre>{json.dumps(schema_obj, indent=2)}</pre>"
        else:
            return f"<pre>{str(schema_obj)}</pre>"

    def _get_display_fields(self) -> Dict[str, Any]:
        """
        Get fields to display, respecting any display configuration.

        Returns:
            Dict mapping field names to values
        """
        if not is_dataclass(self):
            raise TypeError("DisplayMixin can only be used with dataclasses")

        # Get all fields from the dataclass
        fields = {}
        for field_name, field_value in self.__dict__.items():
            # Skip private fields (starting with underscore)
            if not field_name.startswith("_"):
                fields[field_name] = field_value

        return fields

    def _get_header_fields(self) -> Dict[str, str]:
        """Return fields that should be displayed in the header."""
        # Default implementation - override in subclasses if needed
        header_fields = {}

        # Common fields that might be in header
        for field_name in ["uid", "id", "name", "description"]:
            if hasattr(self, field_name) and getattr(self, field_name) is not None:
                header_fields[field_name] = getattr(self, field_name)

        return header_fields

    def _get_special_field_renderers(self) -> Dict[str, Callable]:
        """
        Return special rendering functions for specific fields.

        Returns:
            Dict mapping field names to rendering functions
        """
        # Default renderers - override in subclasses if needed
        return {
            "supported_mime_types": lambda values: self._format_list_as_tags(
                values, "mime-tag"
            ),
            "supported_location_paths": lambda values: self._format_list_as_tags(
                values, "path-tag"
            ),
            "mime_types": lambda values: self._format_list_as_tags(values, "mime-tag"),
            "location_paths": lambda values: self._format_list_as_tags(
                values, "path-tag"
            ),
            "schema": lambda value: f"""
                <button class="toggle-button" id="schema-toggle-{self._generate_id()}">Show Schema</button>
                <div class="collapsible-content" id="schema-content-{self._generate_id()}">
                    {self._render_schema_html(value)}
                </div>
                <script>
                    (function() {{
                        var toggle = document.getElementById("schema-toggle-{self._generate_id()}");
                        var content = document.getElementById("schema-content-{self._generate_id()}");

                        toggle.addEventListener("click", function() {{
                            if (content.style.maxHeight) {{
                                content.style.maxHeight = null;
                                toggle.textContent = "Show Schema";
                            }} else {{
                                content.style.maxHeight = content.scrollHeight + "px";
                                toggle.textContent = "Hide Schema";
                            }}
                        }});
                    }})();
                </script>
            """,  # noqa: E501
        }

    def _render_field_html(self, field_name: str, field_value: Any) -> str:
        """Render a field value as HTML based on its type."""
        renderers = self._get_special_field_renderers()

        # Use special renderer if available
        if field_name in renderers:
            return renderers[field_name](field_value)

        # Handle different types
        if field_value is None:
            return "<em>None</em>"
        elif isinstance(field_value, (list, tuple)) and not field_value:
            return "<em>Empty list</em>"
        elif isinstance(field_value, (list, tuple)):
            items = [f"<li>{item}</li>" for item in field_value]
            return f'<ul>{"".join(items)}</ul>'
        elif isinstance(field_value, dict) and not field_value:
            return "<em>Empty dict</em>"
        elif isinstance(field_value, dict):
            return f"<pre>{json.dumps(field_value, indent=2)}</pre>"
        elif hasattr(field_value, "_repr_html_"):
            return field_value._repr_html_()
        else:
            return str(field_value)

    def _format_field_name(self, field_name: str) -> str:
        """Format a field name for display."""
        # Convert snake_case to Title Case
        return " ".join(word.capitalize() for word in field_name.split("_"))

    def _repr_html_(self) -> str:
        """
        Generate HTML representation for Jupyter notebooks.
        This will be automatically displayed when the object is the last line in a cell.
        """
        # Get fields for header and body
        header_fields = self._get_header_fields()
        all_fields = self._get_display_fields()

        # Remove header fields from body fields
        body_fields = {k: v for k, v in all_fields.items() if k not in header_fields}

        # Start building HTML
        html = f"""
        {self._get_css()}
        <div class="spec-container">
            <div class="spec-header">
        """

        # Add title if name is available
        if "name" in header_fields:
            html += f'<h3 class="spec-title">{header_fields["name"]}{self._get_object_type_badge()}</h3>'  # noqa: E501
        else:
            # Fallback to class name
            html += f'<h3 class="spec-title">{self.__class__.__name__}{self._get_object_type_badge()}</h3>'  # noqa: E501

        # Add ID/UID if available
        id_field = next((f for f in ["uid", "id"] if f in header_fields), None)
        if id_field:
            html += f'<div class="spec-subtitle">ID: {header_fields[id_field]}</div>'

        # Add description if available
        if "description" in header_fields and header_fields["description"]:
            html += (
                f'<div class="spec-description">{header_fields["description"]}</div>'
            )

        html += """
            </div>
            <div class="spec-body">
        """

        # Add body fields
        for field_name, field_value in body_fields.items():
            # Skip fields already in header
            if field_name in header_fields:
                continue

            html += f"""
            <div class="spec-section">
                <h4 class="spec-section-title">{self._format_field_name(field_name)}</h4>
                <div class="spec-property-value">
                    {self._render_field_html(field_name, field_value)}
                </div>
            </div>
            """  # noqa: E501

        html += """
            </div>
        </div>
        """

        return html

    def _format_field_markdown(self, field_name: str, field_value: Any) -> str:
        """Format a field value as Markdown based on its type."""
        if field_value is None:
            return "*None*"
        elif isinstance(field_value, (list, tuple)) and not field_value:
            return "*Empty list*"
        elif isinstance(field_value, (list, tuple)):
            return "\n".join(f"- {item}" for item in field_value)
        elif isinstance(field_value, dict) and not field_value:
            return "*Empty dict*"
        elif isinstance(field_value, dict):
            return f"```json\n{json.dumps(field_value, indent=2)}\n```"
        elif hasattr(field_value, "_repr_markdown_"):
            # Use object's own markdown representation
            md = field_value._repr_markdown_()
            # Increase heading levels to fit within our document hierarchy
            for i in range(5, 0, -1):
                md = md.replace("#" * i, "#" * (i + 2))
            return md
        else:
            return str(field_value)

    def _repr_markdown_(self) -> str:
        """
        Generate Markdown representation for environments that don't support HTML.
        """
        # Get fields for header and body
        header_fields = self._get_header_fields()
        all_fields = self._get_display_fields()

        # Start with title - use name or class name
        if "name" in header_fields:
            markdown = f"# {header_fields['name']}\n\n"
        else:
            markdown = f"# {self.__class__.__name__}\n\n"

        # Add ID/UID if available
        id_field = next((f for f in ["uid", "id"] if f in header_fields), None)
        if id_field:
            markdown += f"**ID:** `{header_fields[id_field]}`\n\n"

        # Add description if available
        if "description" in header_fields and header_fields["description"]:
            markdown += f"{header_fields['description']}\n\n"

        # Add other fields
        for field_name, field_value in all_fields.items():
            # Skip fields already in header
            if field_name in header_fields:
                continue

            markdown += f"## {self._format_field_name(field_name)}\n\n"
            markdown += f"{self._format_field_markdown(field_name, field_value)}\n\n"

        return markdown

    def __repr__(self) -> str:
        """String representation for non-notebook environments."""
        class_name = self.__class__.__name__

        # Get name and ID if available
        name = getattr(self, "name", None)
        id_val = getattr(self, "uid", getattr(self, "id", None))

        if name and id_val:
            return f"{class_name}(name='{name}', id='{id_val}')"
        elif name:
            return f"{class_name}(name='{name}')"
        elif id_val:
            return f"{class_name}(id='{id_val}')"
        else:
            return f"{class_name}()"


@dataclass
class MLOpsBatchSourceSpec(DisplayMixin):
    uid: str
    name: str
    schema: SchemaDocumentation
    supported_mime_types: list[str]
    supported_location_paths: list[str]


@dataclass
class MLOpsBatchSinkSpec(DisplayMixin):
    uid: str
    name: str
    schema: SchemaDocumentation
    supported_mime_types: list[str]
    supported_location_paths: list[str]


class MLOpsBatchConnectors:

    def __init__(self, client: _core.Client):
        self._client = client

    @property
    def source_specs(self) -> MLOpsBatchSourceSpecs:
        return MLOpsBatchSourceSpecs(client=self._client)

    @property
    def sink_specs(self) -> MLOpsBatchSinkSpecs:
        return MLOpsBatchSinkSpecs(client=self._client)


class MLOpsBatchSourceSpecs:
    def __init__(self, client: _core.Client):
        self._client = client

    def list(self, **selectors: Any) -> _utils.Table:  # noqa A003
        source_specs = (
            self._client._backend.batch.source_spec.list_source_specs().source_specs
        )
        data_as_dicts = [
            {
                "name": source_spec.display_name,
                "uid": source_spec.name.split("/")[-1],
                "schema": SchemaDocumentation(json.loads(source_spec.schema)),
                "supported_mime_types": source_spec.supported_mime_types,
                "supported_location_paths": source_spec.supported_location_paths,
                "raw_info": source_spec,
            }
            for source_spec in source_specs
        ]
        return _utils.Table(
            data=data_as_dicts,
            keys=["name", "uid"],
            get_method=lambda x: MLOpsBatchSourceSpec(
                uid=x["uid"],
                name=x["name"],
                schema=x["schema"],
                supported_mime_types=x["supported_mime_types"],
                supported_location_paths=x["supported_location_paths"],
            ),
            **selectors,
        )


class MLOpsBatchSinkSpecs:
    def __init__(self, client: _core.Client):
        self._client = client

    def list(self, **selectors: Any) -> _utils.Table:  # noqa A003
        sink_specs = self._client._backend.batch.sink_spec.list_sink_specs().sink_specs
        data_as_dicts = [
            {
                "name": sink_spec.display_name,
                "uid": sink_spec.name.split("/")[-1],
                "schema": SchemaDocumentation(json.loads(sink_spec.schema)),
                "supported_mime_types": sink_spec.supported_mime_types,
                "supported_location_paths": sink_spec.supported_location_paths,
                "raw_info": sink_spec,
            }
            for sink_spec in sink_specs
        ]
        return _utils.Table(
            data=data_as_dicts,
            keys=["name", "uid"],
            get_method=lambda x: MLOpsBatchSinkSpec(
                uid=x["uid"],
                name=x["name"],
                schema=x["schema"],
                supported_mime_types=x["supported_mime_types"],
                supported_location_paths=x["supported_location_paths"],
            ),
            **selectors,
        )
