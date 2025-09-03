import Autocomplete from '/static/afat/libs/bootstrap5-autocomplete/1.1.33/autocomplete.min.js';

document.addEventListener('DOMContentLoaded', () => {
    'use strict';

    /**
     * Initialize autocomplete dropdown
     *
     * @param {HTMLElement} element
     */
    const initializeAutocomplete = (element) => {
        const datalistId = element.getAttribute('data-datalist');
        const datalist = document.getElementById(datalistId);

        if (!datalist) {
            return;
        }

        const autoComplete = new Autocomplete(element, { // eslint-disable-line no-unused-vars
            onSelectItem: console.log,
            onRenderItem: (item, label) => {
                return `<l-i set="fl" name="${item.value.toLowerCase()}" size="16"></l-i> ${label}`;
            }
        });
    };

    // Initialize all autocomplete dropdowns
    document.querySelectorAll('[data-datalist]')
        .forEach(initializeAutocomplete);
});
