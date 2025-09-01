# filter_tabs/renderer.py
"""
Renders the HTML and fallback output for the filter-tabs directive.
Consolidated version including parsing utilities and content type inference.
"""

from __future__ import annotations

import copy
from docutils import nodes
from sphinx.util import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

# Import models from extension.py (after consolidation)
from .extension import TabData, FilterTabsConfig, IDGenerator
from .extension import ContainerNode, FieldsetNode, LegendNode, RadioInputNode, LabelNode, PanelNode

if TYPE_CHECKING:
    from sphinx.environment import BuildEnvironment
    from docutils.parsers.rst import Directive

logger = logging.getLogger(__name__)

# Constants
SFT_CONTAINER = "sft-container"
SFT_FIELDSET = "sft-fieldset"
SFT_LEGEND = "sft-legend"
SFT_RADIO_GROUP = "sft-radio-group"
SFT_CONTENT = "sft-content"
SFT_PANEL = "sft-panel"


# =============================================================================
# Content Type Inference Utilities (moved from parsers.py)
# =============================================================================

class ContentTypeInferrer:
    """
    Infers the type of content based on tab names to generate meaningful legends.
    """
    PATTERNS = [
        (['python', 'javascript', 'java', 'c++', 'rust', 'go', 'ruby', 'php'], 'programming language'),
        (['windows', 'mac', 'macos', 'linux', 'ubuntu', 'debian', 'fedora'], 'operating system'),
        (['pip', 'conda', 'npm', 'yarn', 'cargo', 'gem', 'composer'], 'package manager'),
        (['cli', 'gui', 'terminal', 'command', 'console', 'graphical'], 'interface'),
        (['development', 'staging', 'production', 'test', 'local'], 'environment'),
        (['source', 'binary', 'docker', 'manual', 'automatic'], 'installation method'),
    ]
    
    @classmethod
    def infer_type(cls, tab_names: List[str]) -> str:
        """
        Infer content type from a list of tab names.
        
        Args:
            tab_names: List of tab names to analyze
            
        Returns:
            Inferred content type string (e.g., 'programming language', 'operating system')
        """
        lower_names = [name.lower() for name in tab_names]
        
        # First pass: exact matches
        for keywords, content_type in cls.PATTERNS:
            if any(name in keywords for name in lower_names):
                return content_type
        
        # Second pass: substring matches
        for keywords, content_type in cls.PATTERNS:
            for name in lower_names:
                if any(keyword in name for keyword in keywords):
                    return content_type
        
        # Default fallback
        return 'option'


# =============================================================================
# Main Renderer Class
# =============================================================================

class FilterTabsRenderer:
    """
    Renders filter tabs with a focus on accessibility and browser compatibility.
    Consolidated version with integrated content type inference.
    """

    def __init__(self, directive: Directive, tab_data: List[TabData], general_content: List[nodes.Node], custom_legend: Optional[str] = None):
        self.directive = directive
        self.env: BuildEnvironment = directive.state.document.settings.env
        self.app = self.env.app
        self.tab_data = tab_data
        self.general_content = general_content
        self.custom_legend = custom_legend
        
        # 1. Load configuration first
        self.config = FilterTabsConfig.from_sphinx_config(self.app.config)
        
        # 2. Safely initialize the counter on the environment if it doesn't exist
        if not hasattr(self.env, 'filter_tabs_counter'):
            self.env.filter_tabs_counter = 0
            
        # 3. Increment the counter for this new tab group
        self.env.filter_tabs_counter += 1
        
        # 4. Generate the unique group ID and the ID generator instance
        self.group_id = f"filter-group-{self.env.filter_tabs_counter}"
        self.id_gen = IDGenerator(self.group_id)
        
        # 5. Perform debug logging now that config and group_id are set
        if self.config.debug_mode:
            logger.info(f"Initialized new tab group with id: '{self.group_id}'")

    def render_html(self) -> List[nodes.Node]:
        """Render HTML with a browser-compatible CSS approach."""
        if self.config.debug_mode:
            logger.info(f"Rendering filter-tabs group {self.group_id}")

        css_node = self._generate_compatible_css()

        container_attrs = self._get_container_attributes()
        container = ContainerNode(**container_attrs)

        fieldset = self._create_fieldset()
        container.children = [fieldset]
        
        return [css_node, container]

    def render_fallback(self) -> List[nodes.Node]:
        """Render for non-HTML builders (e.g., LaTeX)."""
        output_nodes: List[nodes.Node] = []
        
        if self.general_content:
            output_nodes.extend(copy.deepcopy(self.general_content))
        
        for tab in self.tab_data:
            admonition = nodes.admonition()
            admonition += nodes.title(text=tab.name)
            admonition.extend(copy.deepcopy(tab.content))
            output_nodes.append(admonition)
        
        return output_nodes

    def _get_container_attributes(self) -> Dict[str, Any]:
        """Get container attributes, including the style for custom properties."""
        return {
            'classes': [SFT_CONTAINER],
            'role': 'region',
            'aria-labelledby': self.id_gen.legend_id(),
            'style': self.config.to_css_properties()
        }

    def _generate_compatible_css(self) -> nodes.raw:
        """Generate CSS using sibling selectors to show/hide panels."""
        css_rules = []
        for i, tab in enumerate(self.tab_data):
            radio_id = self.id_gen.radio_id(i)
            panel_id = self.id_gen.panel_id(i)
            css_rules.append(
                f"#{radio_id}:checked ~ .{SFT_CONTENT} #{panel_id} {{ display: block; }}"
            )
        
        css_content = "\n".join(css_rules)
        return nodes.raw(text=f"<style>\n{css_content}\n</style>", format='html')

    def _create_fieldset(self) -> FieldsetNode:
        """Create the main fieldset containing the legend, radio buttons, and panels."""
        fieldset = FieldsetNode(role="radiogroup")
        
        fieldset += self._create_legend()
        
        radio_group = ContainerNode(classes=[SFT_RADIO_GROUP])
        self._populate_radio_group(radio_group)
        
        content_area = ContainerNode(classes=[SFT_CONTENT])
        self._populate_content_area(content_area)
        
        # This is the fix: place the content_area inside the radio_group.
        radio_group += content_area
        
        fieldset += radio_group
        
        return fieldset

    def _create_legend(self) -> LegendNode:
        """Create a meaningful, visible legend for the tab group."""
        legend = LegendNode(classes=[SFT_LEGEND], ids=[self.id_gen.legend_id()])
        
        # Use the custom legend if it exists
        if self.custom_legend:
            legend_text = self.custom_legend
        else:
            # Fallback to the auto-generated legend using content type inference
            tab_names = [tab.name for tab in self.tab_data]
            content_type = ContentTypeInferrer.infer_type(tab_names)
            legend_text = f"Choose {content_type}: {', '.join(tab_names)}"
        
        legend += nodes.Text(legend_text)
        return legend

    def _populate_radio_group(self, radio_group: ContainerNode) -> None:
        """Create and add all radio buttons and labels to the radio group container."""
        default_index = next((i for i, tab in enumerate(self.tab_data) if tab.is_default), 0)
     
        for i, tab in enumerate(self.tab_data):
            radio_group += self._create_radio_button(i, tab, is_checked=(i == default_index))
            radio_group += self._create_label(i, tab)
            radio_group += self._create_screen_reader_description(i, tab)

    def _create_radio_button(self, index: int, tab: TabData, is_checked: bool) -> RadioInputNode:
        """Create a single radio button input."""
        radio = RadioInputNode(
            classes=['sr-only'],
            type='radio',
            name=self.group_id,
            ids=[self.id_gen.radio_id(index)],
            **{'aria-describedby': self.id_gen.desc_id(index)}
        )
        if tab.aria_label:
            radio['aria-label'] = tab.aria_label
        if is_checked:
            radio['checked'] = 'checked'
        return radio

    def _create_label(self, index: int, tab: TabData) -> LabelNode:
        """Create a label for a radio button."""
        label = LabelNode(for_id=self.id_gen.radio_id(index))
        label += nodes.Text(tab.name)
        return label

    def _create_screen_reader_description(self, index: int, tab: TabData) -> ContainerNode:
        """Create the hidden description for screen readers."""
        desc_text = f"Show content for {tab.name}"
        description_node = ContainerNode(classes=['sr-only'], ids=[self.id_gen.desc_id(index)])
        description_node += nodes.Text(desc_text)
        return description_node

    def _populate_content_area(self, content_area: ContainerNode) -> None:
        """Create and add all general and tab-specific content panels."""
        if self.general_content:
            general_panel = PanelNode(classes=[SFT_PANEL], **{'data-filter': 'General'})
            general_panel.extend(copy.deepcopy(self.general_content))
            content_area += general_panel
        
        for i, tab in enumerate(self.tab_data):
            content_area += self._create_tab_panel(i, tab)

    def _create_tab_panel(self, index: int, tab: TabData) -> PanelNode:
        """Create a single content panel for a tab."""
        panel_attrs = {
            'classes': [SFT_PANEL],
            'ids': [self.id_gen.panel_id(index)],
            'role': 'region',
            'aria-labelledby': self.id_gen.radio_id(index),
            'tabindex': '0',
            'data-tab': tab.name.lower().replace(' ', '-')
        }
        panel = PanelNode(**panel_attrs)
        panel.extend(copy.deepcopy(tab.content))
        return panel
    