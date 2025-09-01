// Progressive enhancement for keyboard navigation and accessibility.
// This file ensures proper keyboard navigation and focus management,
// while maintaining a CSS-only fallback.

(function() {
    'use strict';
    
    // Only enhance if the extension's HTML is present on the page.
    if (!document.querySelector('.sft-container')) return;
    
    /**
     * Moves focus to the content panel associated with a given radio button.
     * This improves accessibility by directing screen reader users to the new content.
     * @param {HTMLInputElement} radio The radio button that was selected.
     */
    function focusOnPanel(radio) {
        if (!radio.checked) return;
        
        // Derive the panel's ID from the radio button's ID.
        // e.g., 'filter-group-1-radio-0' becomes 'filter-group-1-panel-0'
        const panelId = radio.id.replace('-radio-', '-panel-');
        const panel = document.getElementById(panelId);
        
        if (panel) {
            panel.focus();
        }
    }

    /**
     * Creates or updates a live region to announce tab changes to screen readers.
     * @param {string} tabName The name of the selected tab.
     */
    function announceTabChange(tabName) {
        // Create or find the live region for screen reader announcements.
        let liveRegion = document.getElementById('tab-live-region');
        if (!liveRegion) {
            liveRegion = document.createElement('div');
            liveRegion.id = 'tab-live-region';
            liveRegion.setAttribute('role', 'status');
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.setAttribute('aria-atomic', 'true');
            // Hide the element visually but keep it accessible.
            liveRegion.style.position = 'absolute';
            liveRegion.style.left = '-10000px';
            liveRegion.style.width = '1px';
            liveRegion.style.height = '1px';
            liveRegion.style.overflow = 'hidden';
            document.body.appendChild(liveRegion);
        }
        
        // Update the announcement text.
        liveRegion.textContent = `${tabName} tab selected`;
        
        // Clear the announcement after a short delay to prevent clutter.
        setTimeout(() => {
            liveRegion.textContent = '';
        }, 1000);
    }

    /**
     * Initializes keyboard navigation for all filter-tab components on the page.
     */
    function initTabKeyboardNavigation() {
        const containers = document.querySelectorAll('.sft-container');
        
        containers.forEach(container => {
            const tabBar = container.querySelector('.sft-radio-group');
            if (!tabBar) return;
            
            const radios = tabBar.querySelectorAll('input[type="radio"]');
            const labels = tabBar.querySelectorAll('label');
            
            if (radios.length === 0 || labels.length === 0) return;
            
            // Make labels focusable to act as keyboard navigation targets.
            labels.forEach(label => {
                if (!label.hasAttribute('tabindex')) {
                    label.setAttribute('tabindex', '0');
                }
            });

            // Handle keyboard navigation on the tab labels.
            labels.forEach((label, index) => {
                label.addEventListener('keydown', (event) => {
                    let targetIndex = index;
                    let handled = false;
                    
                    switch (event.key) {
                        case 'ArrowRight':
                            event.preventDefault();
                            targetIndex = (index + 1) % labels.length;
                            handled = true;
                            break;
                            
                        case 'ArrowLeft':
                            event.preventDefault();
                            targetIndex = (index - 1 + labels.length) % labels.length;
                            handled = true;
                            break;
                            
                        case 'Home':
                            event.preventDefault();
                            targetIndex = 0;
                            handled = true;
                            break;
                            
                        case 'End':
                            event.preventDefault();
                            targetIndex = labels.length - 1;
                            handled = true;
                            break;
                            
                        case 'Enter':
                        case ' ':
                            // Activate the associated radio button on Enter/Space.
                            event.preventDefault();
                            if (radios[index]) {
                                radios[index].checked = true;
                                radios[index].dispatchEvent(new Event('change', { bubbles: true }));
                            }
                            return;
                            
                        default:
                            return;
                    }
                    
                    if (handled) {
                        // Move focus to the target label and activate its radio button.
                        labels[targetIndex].focus();
                        if (radios[targetIndex]) {
                            radios[targetIndex].checked = true;
                            radios[targetIndex].dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }
                });
            });
            
            // Add listeners for announcements and focus management.
            radios.forEach((radio, index) => {
                radio.addEventListener('change', () => {
                    if (radio.checked) {
                        // Announce the change to screen readers.
                        if (labels[index]) {
                            announceTabChange(labels[index].textContent.trim());
                        }
                        // Move focus to the newly visible panel.
                        focusOnPanel(radio);
                    }
                });
            });
        });
    }
    
    // Initialize the script once the DOM is ready.
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTabKeyboardNavigation);
    } else {
        initTabKeyboardNavigation();
    }
})();
