# tests/test_extension.py

import pytest
from bs4 import BeautifulSoup
from sphinx.testing.util import SphinxTestApp


@pytest.mark.sphinx('html')
def test_basic_filter_tabs(app: SphinxTestApp):
    """Test basic filter tabs functionality."""
    content = """
Test Document
=============

.. filter-tabs::

    This is general content that appears regardless of selection.
    
    .. tab:: Python
    
        Python specific content.
        
    .. tab:: JavaScript (default)
    
        JavaScript specific content.
        
    .. tab:: Rust
    
        Rust specific content.
"""
    app.srcdir.joinpath('index.rst').write_text(content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    
    # Check container structure
    container = soup.select_one('.sft-container')
    assert container, "Container should exist"
    assert container.get('role') == 'region', "Container should have region role"
    
    # Check radiogroup
    fieldset = soup.select_one('.sft-fieldset[role="radiogroup"]')
    assert fieldset, "Fieldset should have radiogroup role"
    
    # Check visible legend
    legend = soup.select_one('.sft-legend')
    assert legend, "Legend should exist"
    legend_text = legend.get_text().strip()
    assert 'Choose' in legend_text, "Legend should have meaningful text"
    
    # Check tabs were created
    radios = soup.select('.sft-radio-group input[type="radio"]')
    assert len(radios) == 3, f"Expected 3 tabs, found {len(radios)}"
    
    # Check tab names from labels
    labels = soup.select('.sft-radio-group label')
    tab_names = [label.text.strip() for label in labels]
    assert tab_names == ['Python', 'JavaScript', 'Rust']
    
    # Check JavaScript is default (second radio should be checked)
    assert radios[1].get('checked') is not None, "JavaScript tab should be default"
    
    # Check panels have proper roles
    panels = soup.select('.sft-panel[role="region"]')
    assert len(panels) == 3, "Should have 3 panels with region role"
    
    # Check general content exists
    general_panel = soup.select_one('.sft-panel[data-filter="General"]')
    assert general_panel, "General panel not found"
    assert "general content that appears" in general_panel.text


@pytest.mark.sphinx('html')
def test_aria_label_option(app: SphinxTestApp):
    """Test that the :aria-label: option adds proper ARIA attributes."""
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: CLI
       :aria-label: Command Line Interface installation instructions
       
        Install via command line.
        
    .. tab:: GUI (default)
       :aria-label: Graphical User Interface installation instructions
       
        Install via graphical interface.
"""
    app.srcdir.joinpath('index.rst').write_text(content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    
    # Find the radio inputs
    radios = soup.select('.sft-radio-group input[type="radio"]')
    
    # Check that aria-labels were added
    assert radios[0].get('aria-label') == "Command Line Interface installation instructions"
    assert radios[1].get('aria-label') == "Graphical User Interface installation instructions"
    
    # Verify the visual labels are still short
    labels = soup.select('.sft-radio-group label')
    assert labels[0].text.strip() == 'CLI'
    assert labels[1].text.strip() == 'GUI'


@pytest.mark.sphinx('html')
def test_mixed_general_and_tab_content(app: SphinxTestApp):
    """Test that content outside tab directives becomes general content."""
    content = """
Test Document
=============

.. filter-tabs::

    This paragraph is general content.
    
    It can span multiple paragraphs.
    
    .. note::
    
        Even admonitions outside tabs are general.
    
    .. tab:: Option A
    
        Content for option A.
        
    Some more general content between tabs.
    
    .. tab:: Option B (default)
    
        Content for option B.
"""
    app.srcdir.joinpath('index.rst').write_text(content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    
    general_panel = soup.select_one('.sft-panel[data-filter="General"]')
    assert general_panel, "General panel not found"
    
    general_text = general_panel.text
    assert "This paragraph is general content" in general_text
    assert "It can span multiple paragraphs" in general_text
    assert "Even admonitions outside tabs are general" in general_text
    assert "Some more general content between tabs" in general_text
    
    # Ensure tab content is NOT in general panel
    assert "Content for option A" not in general_text
    assert "Content for option B" not in general_text


@pytest.mark.sphinx('html')
def test_accessibility_features(app: SphinxTestApp):
    """Test accessibility features are properly implemented."""
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Python (default)
        Python content
    .. tab:: JavaScript
        JS content
"""
    app.srcdir.joinpath('index.rst').write_text(content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    
    # Check ARIA relationships
    container = soup.select_one('.sft-container')
    legend = soup.select_one('.sft-legend')
    
    # Container should reference legend
    assert container.get('aria-labelledby') == legend.get('id')
    
    # --- START of updated section ---

    # Check that each radio button has a corresponding screen reader description
    radios = soup.select('input[type="radio"]')
    assert len(radios) == 2

    for radio in radios:
        describedby_id = radio.get('aria-describedby')
        assert describedby_id, "Radio button should have aria-describedby"
        
        desc_element = soup.select_one(f'#{describedby_id}')
        assert desc_element, f"Description element #{describedby_id} should exist"
        assert 'sr-only' in desc_element.get('class', []), "Description should be sr-only"

    # Check panels are focusable (with typo corrected)
    panels = soup.select('.sft-panel[role="region"]')
    for panel in panels:
        if panel.get('data-filter') != 'General':  # General panel doesn't need tabindex
            assert panel.get('tabindex') == '0', "Panels should be focusable"


@pytest.mark.sphinx('html')
def test_nested_tabs(app: SphinxTestApp):
    """Test that nested tabs work correctly."""
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Windows
    
        Windows instructions:
        
        .. filter-tabs::
        
            .. tab:: Pip (default)
                pip install package
            .. tab:: Conda  
                conda install package
                
    .. tab:: Mac (default)
    
        Mac instructions here.
"""
    app.srcdir.joinpath('index.rst').write_text(content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    
    # Should have multiple filter-tabs containers
    containers = soup.select('.sft-container')
    assert len(containers) == 2, "Should have 2 nested containers"
    
    # Each should have their own radio groups
    radiogroups = soup.select('[role="radiogroup"]')
    assert len(radiogroups) == 2, "Should have 2 radiogroups"
    
    # Check unique group names
    radios = soup.select('input[type="radio"]')
    group_names = {radio.get('name') for radio in radios}
    assert len(group_names) == 2, "Should have 2 unique radio group names"


@pytest.mark.sphinx('latex') 
def test_latex_fallback(app: SphinxTestApp):
    """Test that LaTeX fallback behavior works."""
    content = """
Test Document
=============

.. filter-tabs::

    General content.

    .. tab:: Python
        Python content
    .. tab:: JavaScript
        JS content
"""
    app.srcdir.joinpath('index.rst').write_text(content)
    app.build()
    
    # Find the actual generated LaTeX file
    latex_files = list(app.outdir.glob('*.tex'))
    assert len(latex_files) > 0, "Should generate at least one LaTeX file"
    
    # Read the main LaTeX file (usually the first one alphabetically)
    latex_file = sorted(latex_files)[0]
    latex_content = latex_file.read_text()
    
    # Should contain content for each tab
    assert 'Python' in latex_content, "Python tab should appear in LaTeX"
    assert 'JavaScript' in latex_content, "JavaScript tab should appear in LaTeX"
    assert 'General content' in latex_content, "General content should appear in LaTeX"


@pytest.mark.sphinx('html')
def test_configuration_theming(app: SphinxTestApp):
    """Test that theming configuration options work."""
    # Use the correct simplified config option name
    app.config.filter_tabs_highlight_color = '#ff0000'
    
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Test
        Test content
"""
    app.srcdir.joinpath('index.rst').write_text(content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    container = soup.select_one('.sft-container')
    
    style = container.get('style', '')
    # Test that the highlight color CSS variable is set correctly
    assert '--sft-highlight-color: #ff0000' in style, f"CSS custom property should be set. Got: {style}"


@pytest.mark.sphinx('html')
def test_unique_ids_multiple_groups(app: SphinxTestApp):
    """Test that IDs are unique across multiple tab groups."""
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: Python
        Python 1
    .. tab:: JavaScript
        JS 1

.. filter-tabs::

    .. tab:: Python  
        Python 2
    .. tab:: JavaScript
        JS 2
"""
    app.srcdir.joinpath('index.rst').write_text(content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    
    # Collect all IDs
    all_elements_with_ids = soup.select('[id]')
    all_ids = [elem.get('id') for elem in all_elements_with_ids]
    
    # Check for duplicates
    duplicates = [id_val for id_val in set(all_ids) if all_ids.count(id_val) > 1]
    assert not duplicates, f"Duplicate IDs found: {duplicates}"


@pytest.mark.sphinx('html')
def test_default_tab_selection(app: SphinxTestApp):
    """Test that default tab selection works properly."""
    app.config.filter_tabs_debug_mode = True
    content = """
Test Document
=============

.. filter-tabs::

    .. tab:: First
        First tab content
        
    .. tab:: Second (default)
        Second tab content
        
    .. tab:: Third
        Third tab content
"""
    app.srcdir.joinpath('index.rst').write_text(content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    
    # Check that the second radio button is checked
    radios = soup.select('input[type="radio"]')
    assert len(radios) == 3
    
    # Find which radio has the checked attribute
    checked_radios = []
    for i, radio in enumerate(radios):
        if radio.get('checked') is not None:
            checked_radios.append(i)
    
    # Debug output if the test fails
    if checked_radios != [1]:
        labels = soup.select('.sft-radio-group label')
        label_texts = [label.text.strip() for label in labels]
        print(f"Label texts: {label_texts}")
        print(f"Checked radios: {checked_radios}")
        
        # Check the tab data to see which one was marked as default
        for i, radio in enumerate(radios):
            print(f"Radio {i} checked: {radio.get('checked') is not None}")
    
    assert checked_radios == [1], f"Expected second tab to be checked, but got: {checked_radios}"


@pytest.mark.sphinx('html')
def test_error_handling_no_tabs(app: SphinxTestApp):
    """Test that filter-tabs without any tab directives logs an error."""
    content = """
Test Document
=============

.. filter-tabs::

    This has no tab directives, should cause an error.
"""
    app.srcdir.joinpath('index.rst').write_text(content)
    
    # Run the build and expect Sphinx to log an error
    app.build()
    
    # Check the captured warnings/errors for our specific message
    warnings = app._warning.getvalue()
    assert "No `.. tab::` directives found inside `.. filter-tabs::`" in warnings

@pytest.mark.sphinx('html')
def test_custom_legend_option(app: SphinxTestApp):
    """Test that the :legend: option provides a custom legend."""
    content = """
Test Document
=============

.. filter-tabs::
   :legend: My Custom Test Legend

   .. tab:: One
      Content One
"""
    app.srcdir.joinpath('index.rst').write_text(content)
    app.build()
    
    soup = BeautifulSoup((app.outdir / 'index.html').read_text(), 'html.parser')
    
    legend = soup.select_one('.sft-legend')
    assert legend, "Legend should exist"
    assert legend.get_text().strip() == "My Custom Test Legend"
