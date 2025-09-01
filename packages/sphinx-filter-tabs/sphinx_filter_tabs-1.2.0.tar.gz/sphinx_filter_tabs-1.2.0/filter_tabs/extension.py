# filter_tabs/extension.py
"""
Core extension module for sphinx-filter-tabs.
Consolidated version containing directives, data models, nodes, and Sphinx integration.
"""

from __future__ import annotations
import copy
import shutil
from pathlib import Path
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.writers.html import HTML5Translator

from typing import TYPE_CHECKING, Any, Dict, List, Optional
from dataclasses import dataclass, field
from . import __version__

if TYPE_CHECKING:
    from sphinx.environment import BuildEnvironment

# =============================================================================
# Custom Docutils Nodes
# =============================================================================

class ContainerNode(nodes.General, nodes.Element): pass
class FieldsetNode(nodes.General, nodes.Element): pass
class LegendNode(nodes.General, nodes.Element): pass
class RadioInputNode(nodes.General, nodes.Element): pass
class LabelNode(nodes.General, nodes.Element): pass
class PanelNode(nodes.General, nodes.Element): pass
class DetailsNode(nodes.General, nodes.Element): pass
class SummaryNode(nodes.General, nodes.Element): pass


# =============================================================================
# Data Models and Configuration
# =============================================================================

@dataclass
class TabData:
    """
    Represents a single tab's data within a filter-tabs directive.
    
    Attributes:
        name: Display name of the tab
        is_default: Whether this tab should be selected by default
        aria_label: Optional ARIA label for accessibility
        content: List of docutils nodes containing the tab's content
    """
    name: str
    is_default: bool = False
    aria_label: Optional[str] = None
    content: List[nodes.Node] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate tab data after initialization."""
        if not self.name:
            raise ValueError("Tab name cannot be empty")
        
        # Ensure content is a list
        if self.content is None:
            self.content = []


@dataclass
class FilterTabsConfig:
    """
    Simplified configuration settings for filter-tabs rendering.
    Reduced from 9 options to 2 essential ones.
    """
    # Essential theming - only the highlight color is commonly customized
    highlight_color: str = '#007bff'
    
    # Development option
    debug_mode: bool = False
    
    @classmethod
    def from_sphinx_config(cls, app_config) -> 'FilterTabsConfig':
        """Create a FilterTabsConfig from Sphinx app.config."""
        return cls(
            highlight_color=getattr(
                app_config, 'filter_tabs_highlight_color', cls.highlight_color
            ),
            debug_mode=getattr(
                app_config, 'filter_tabs_debug_mode', cls.debug_mode
            ),
        )
    
    def to_css_properties(self) -> str:
        """Convert config to CSS custom properties string."""
        # Generate CSS variables - the highlight color drives all other colors
        return f"--sft-highlight-color: {self.highlight_color};"


@dataclass
class IDGenerator:
    """
    Centralized ID generation for consistent element identification.
    
    This ensures all IDs follow a consistent pattern and are unique
    within their filter-tabs group.
    """
    group_id: str
    
    def radio_id(self, index: int) -> str:
        """Generate ID for a radio button."""
        return f"{self.group_id}-radio-{index}"
    
    def panel_id(self, index: int) -> str:
        """Generate ID for a content panel."""
        return f"{self.group_id}-panel-{index}"
    
    def desc_id(self, index: int) -> str:
        """Generate ID for a screen reader description."""
        return f"{self.group_id}-desc-{index}"
    
    def legend_id(self) -> str:
        """Generate ID for the fieldset legend."""
        return f"{self.group_id}-legend"
    
    def label_id(self, index: int) -> str:
        """Generate ID for a label (if needed)."""
        return f"{self.group_id}-label-{index}"


# =============================================================================
# Directive Classes
# =============================================================================

# --- Constants ---
COLLAPSIBLE_SECTION = "collapsible-section"
COLLAPSIBLE_CONTENT = "collapsible-content"
CUSTOM_ARROW = "custom-arrow"

logger = logging.getLogger(__name__)


class TabDirective(Directive):
    """Handles the `.. tab::` directive, capturing its content and options."""
    has_content = True
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {'aria-label': directives.unchanged}

    def run(self) -> list[nodes.Node]:
        """Process the tab directive and return container node."""
        env = self.state.document.settings.env
        
        # Validate context
        if not hasattr(env, 'sft_context') or not env.sft_context:
           raise self.error("`tab` can only be used inside a `filter-tabs` directive.")
        
        # Parse tab argument - moved from parsers.py
        try:
            tab_name, is_default = self._parse_tab_argument(self.arguments[0])
        except ValueError as e:
            raise self.error(f"Invalid tab argument: {e}")
        
        # Create container with parsed data
        container = nodes.container(classes=["sft-temp-panel"])
        container['filter_name'] = tab_name
        container['is_default'] = is_default
        container['aria_label'] = self.options.get('aria-label', None)
        
        # Parse the content
        self.state.nested_parse(self.content, self.content_offset, container)
        
        return [container]
    
    def _parse_tab_argument(self, argument: str) -> tuple[str, bool]:
        """Parse a tab argument string to extract name and default status."""
        import re
        
        logger.debug(f"Parsing tab argument: '{argument}'")
        if not argument:
            raise ValueError("Tab argument cannot be empty")
        
        lines = argument.strip().split('\n')
        first_line = lines[0].strip()
        
        if len(lines) > 1:
            logger.debug(
                f"Tab argument contains multiple lines, using only first: '{first_line}'"
            )
        
        DEFAULT_PATTERN = re.compile(r"^(.*?)\s*\(\s*default\s*\)$", re.IGNORECASE)
        match = DEFAULT_PATTERN.match(first_line)
        if match:
            tab_name = match.group(1).strip()
            if not tab_name:
                raise ValueError("Tab name cannot be empty")
            return tab_name, True
        
        return first_line, False


class FilterTabsDirective(Directive):
    """Handles the main `.. filter-tabs::` directive."""
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    option_spec = {'legend': directives.unchanged}

    def run(self) -> list[nodes.Node]:
        """Process the filter-tabs directive."""
        env = self.state.document.settings.env
        
        # Set up context
        if not hasattr(env, 'sft_context'):
            env.sft_context = []
        env.sft_context.append(True)

        # Parse content
        temp_container = nodes.container()
        self.state.nested_parse(self.content, self.content_offset, temp_container)
        
        env.sft_context.pop()
        
        # Get the custom legend option
        custom_legend = self.options.get('legend')

        # Separate general content from tabs using TabData
        general_content = []
        tab_data_list: List[TabData] = []
        
        for node in temp_container.children:
            if isinstance(node, nodes.Element) and "sft-temp-panel" in node.get('classes', []):
                # Create TabData object instead of dictionary
                tab_data = TabData(
                    name=node.get('filter_name', 'Unknown'),
                    is_default=node.get('is_default', False),
                    aria_label=node.get('aria_label', None),
                    content=list(node.children)
                )
                tab_data_list.append(tab_data)
            else:
                general_content.append(node)
        
        # Validate tabs - moved from parsers.py
        if not tab_data_list:
            error_message = (
                "No `.. tab::` directives found inside `.. filter-tabs::`. "
                "You must include at least one tab."
            )
            if general_content:
                error_message += (
                    " Some content was found, but it was not part of a `.. tab::` block."
                )
            raise self.error(error_message)

        try:
            self._validate_tabs(tab_data_list, skip_empty_check=True)
        except ValueError as e:
            raise self.error(str(e))
        
        # Set first tab as default if none specified
        if not any(tab.is_default for tab in tab_data_list):
            tab_data_list[0].is_default = True
        
        # Import renderer here to avoid circular imports
        from .renderer import FilterTabsRenderer
        renderer = FilterTabsRenderer(self, tab_data_list, general_content, custom_legend=custom_legend)
        
        # Render based on builder
        if env.app.builder.name == 'html':
            return renderer.render_html()
        else:
            return renderer.render_fallback()
    
    def _validate_tabs(self, tab_data_list: List[TabData], skip_empty_check: bool = False) -> None:
        """Validate tab data list - moved from parsers.py"""
        if not tab_data_list and not skip_empty_check:
            raise ValueError(
                "No tab directives found inside filter-tabs. "
                "Add at least one .. tab:: directive."
            )
        names = []
        for tab in tab_data_list:
            name = tab.name
            if name in names:
                raise ValueError(
                    f"Duplicate tab name '{name}'. Each tab must have a unique name."
                )
            names.append(name)
            if not tab.content:
                logger.warning(f"Tab '{name}' has no content.")    
        
        default_count = 0
        default_names = []
        for tab in tab_data_list:
            if tab.is_default:
                default_count += 1
                default_names.append(tab.name)
        
        if default_count > 1:
            logger.warning(
                f"Multiple tabs marked as default: {', '.join(default_names)}. "
                f"Using first default: '{default_names[0]}'"
            )


# =============================================================================
# Collapsible Admonitions Support
# =============================================================================

def setup_collapsible_admonitions(app: Sphinx, doctree: nodes.document, docname: str):
    """Convert admonitions with 'collapsible' class to details/summary elements."""
    # Simplified: always enabled for HTML builds, no config needed
    if app.builder.name != 'html':
        return
        
    for node in list(doctree.findall(nodes.admonition)):
        if 'collapsible' not in node.get('classes', []):
            continue
            
        is_expanded = 'expanded' in node.get('classes', [])
        title_node = next(iter(node.findall(nodes.title)), None)
        summary_text = title_node.astext() if title_node else "Details"
        
        if title_node:
            title_node.parent.remove(title_node)

        details_node = DetailsNode(classes=[COLLAPSIBLE_SECTION])
        if is_expanded:
            details_node['open'] = 'open'
        
        summary_node = SummaryNode()
        arrow_span = nodes.inline(classes=[CUSTOM_ARROW])
        arrow_span += nodes.Text("▶")
        summary_node += arrow_span
        summary_node += nodes.Text(summary_text)
        details_node += summary_node
        
        content_node = nodes.container(classes=[COLLAPSIBLE_CONTENT])
        content_node.extend(copy.deepcopy(node.children))
        details_node += content_node
        
        node.replace_self(details_node)


# =============================================================================
# HTML Visitor Functions
# =============================================================================

def _get_html_attrs(node: nodes.Element) -> Dict[str, Any]:
    """Extract HTML attributes from a docutils node, excluding internal attributes."""
    attrs = node.attributes.copy()
    for key in ('ids', 'backrefs', 'dupnames', 'names', 'classes', 'id', 'for_id'):
        attrs.pop(key, None)
    return attrs


def visit_container_node(self: HTML5Translator, node: ContainerNode) -> None:
    self.body.append(self.starttag(node, 'div', **_get_html_attrs(node)))

def depart_container_node(self: HTML5Translator, node: ContainerNode) -> None:
    self.body.append('</div>')

def visit_fieldset_node(self: HTML5Translator, node: FieldsetNode) -> None:
    attrs = _get_html_attrs(node)
    if 'role' in node.attributes:
        attrs['role'] = node['role']
    self.body.append(self.starttag(node, 'fieldset', CLASS="sft-fieldset", **attrs))

def depart_fieldset_node(self: HTML5Translator, node: FieldsetNode) -> None:
    self.body.append('</fieldset>')

def visit_legend_node(self: HTML5Translator, node: LegendNode) -> None:
    self.body.append(self.starttag(node, 'legend', CLASS="sft-legend"))

def depart_legend_node(self: HTML5Translator, node: LegendNode) -> None:
    self.body.append('</legend>')

def visit_radio_input_node(self: HTML5Translator, node: RadioInputNode) -> None:
    attrs = _get_html_attrs(node)
    for key in ['type', 'name', 'checked', 'aria-label']:
        if key in node.attributes:
            attrs[key] = node[key]
    self.body.append(self.starttag(node, 'input', **attrs))

def depart_radio_input_node(self: HTML5Translator, node: RadioInputNode) -> None:
    pass  # Self-closing tag

def visit_label_node(self: HTML5Translator, node: LabelNode) -> None:
    attrs = _get_html_attrs(node)
    if 'for_id' in node.attributes:
        attrs['for'] = node['for_id']
    self.body.append(self.starttag(node, 'label', **attrs))

def depart_label_node(self: HTML5Translator, node: LabelNode) -> None:
    self.body.append('</label>')

def visit_panel_node(self: HTML5Translator, node: PanelNode) -> None:
    attrs = _get_html_attrs(node)
    for key in ['role', 'aria-labelledby', 'tabindex']:
        if key in node.attributes:
            attrs[key] = node[key]
    self.body.append(self.starttag(node, 'div', CLASS="sft-panel", **attrs))

def depart_panel_node(self: HTML5Translator, node: PanelNode) -> None:
    self.body.append('</div>')

def visit_details_node(self: HTML5Translator, node: DetailsNode) -> None:
    attrs = _get_html_attrs(node)
    if 'open' in node.attributes:
        attrs['open'] = 'open'
    self.body.append(self.starttag(node, 'details', **attrs))

def depart_details_node(self: HTML5Translator, node: DetailsNode) -> None:
    self.body.append('</details>')

def visit_summary_node(self: HTML5Translator, node: SummaryNode) -> None:
    self.body.append(self.starttag(node, 'summary', **_get_html_attrs(node)))

def depart_summary_node(self: HTML5Translator, node: SummaryNode) -> None:
    self.body.append('</summary>')


# =============================================================================
# Static File Handling
# =============================================================================

def copy_static_files(app: Sphinx):
    """Copy CSS and JS files to the build directory."""
    if app.builder.name != 'html':
        return
        
    static_source_dir = Path(__file__).parent / "static"
    dest_dir = Path(app.outdir) / "_static"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Only copy the consolidated CSS file
    css_file = static_source_dir / "filter_tabs.css"
    if css_file.exists():
        shutil.copy(css_file, dest_dir)
    
    # Copy JS file if it exists
    js_file = static_source_dir / "filter_tabs.js"
    if js_file.exists():
        shutil.copy(js_file, dest_dir)


# =============================================================================
# Extension Setup
# =============================================================================

def setup(app: Sphinx) -> Dict[str, Any]:
    """Setup the Sphinx extension with minimal configuration."""
    
    # ONLY essential configuration options (down from 9 to 2)
    app.add_config_value('filter_tabs_highlight_color', '#007bff', 'html', [str])
    app.add_config_value('filter_tabs_debug_mode', False, 'html', [bool])
    
    # Add static files
    app.add_css_file('filter_tabs.css')
    app.add_js_file('filter_tabs.js')
    
    # Register custom nodes (keep existing node registration code)
    app.add_node(ContainerNode, html=(visit_container_node, depart_container_node))
    app.add_node(FieldsetNode, html=(visit_fieldset_node, depart_fieldset_node))
    app.add_node(LegendNode, html=(visit_legend_node, depart_legend_node))
    app.add_node(RadioInputNode, html=(visit_radio_input_node, depart_radio_input_node))
    app.add_node(LabelNode, html=(visit_label_node, depart_label_node))
    app.add_node(PanelNode, html=(visit_panel_node, depart_panel_node))
    app.add_node(DetailsNode, html=(visit_details_node, depart_details_node))
    app.add_node(SummaryNode, html=(visit_summary_node, depart_summary_node))
    
    # Register directives
    app.add_directive('filter-tabs', FilterTabsDirective)
    app.add_directive('tab', TabDirective)
    
    # Connect event handlers
    app.connect('builder-inited', copy_static_files)
    app.connect('doctree-resolved', setup_collapsible_admonitions)
    
    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
