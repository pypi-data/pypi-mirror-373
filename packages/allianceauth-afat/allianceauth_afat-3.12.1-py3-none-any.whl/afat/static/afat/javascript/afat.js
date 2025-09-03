/* global afatJsSettingsOverride, afatJsSettingsDefaults, bootstrap, objectDeepMerge */

/* jshint -W097 */
'use strict';

// Build the settings object
let afatSettings = typeof afatJsSettingsDefaults !== 'undefined' ? afatJsSettingsDefaults : null;

if (afatSettings && typeof afatJsSettingsOverride !== 'undefined') {
    afatSettings = objectDeepMerge(
        afatJsSettingsDefaults,
        afatJsSettingsOverride
    );
}

/**
 * Datetime format for AFAT
 *
 * @type {string}
 */
const AFAT_DATETIME_FORMAT = afatSettings.datetimeFormat; // eslint-disable-line no-unused-vars

/**
 * Convert a string to a slug
 * @param {string} text
 * @returns {string}
 */
const convertStringToSlug = (text) => { // eslint-disable-line no-unused-vars
    return text.toLowerCase()
        .replace(/[^\w ]+/g, '')
        .replace(/ +/g, '-');
};

/**
 * Sorting a table by its first columns alphabetically
 * @param {element} table
 * @param {string} order
 */
const sortTable = (table, order) => { // eslint-disable-line no-unused-vars
    const asc = order === 'asc';
    const tbody = table.find('tbody');

    tbody.find('tr').sort((a, b) => {
        if (asc) {
            return $('td:first', a).text().localeCompare($('td:first', b).text());
        } else {
            return $('td:first', b).text().localeCompare($('td:first', a).text());
        }
    }).appendTo(tbody);
};

/**
 * Manage a modal window
 *
 * @param {element} modalElement The modal element
 */
const manageModal = (modalElement) => { // eslint-disable-line no-unused-vars
    /**
     * Update modal elements
     *
     * @param {string} bodyText Modal body text
     * @param {string} confirmButtonText Text for the confirm action button
     * @param {string} cancelButtonText Text for the cancel action button
     * @param {string} confirmActionUrl URL for the confirm action button
     */
    const updateModal = ({bodyText, confirmButtonText, cancelButtonText, confirmActionUrl}) => {
        modalElement.find('#confirm-action').text(confirmButtonText).attr('href', confirmActionUrl);
        modalElement.find('#cancel-action').text(cancelButtonText);
        modalElement.find('.modal-body').html(bodyText);
    };

    /**
     * Clear modal elements
     */
    const clearModal = () => {
        modalElement.find('#confirm-action').text('').attr('href', '');
        modalElement.find('#cancel-action').text('');
        modalElement.find('.modal-body').html('');
    };

    modalElement.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('url');
        const bodyText = button.data('body-text');
        const confirmButtonText = button.data('confirm-text') || modalElement.find('#confirmButtonDefaultText').text();
        const cancelButtonText = button.data('cancel-text') || modalElement.find('#cancelButtonDefaultText').text();

        updateModal({
            bodyText: bodyText,
            confirmButtonText: confirmButtonText,
            cancelButtonText: cancelButtonText,
            url: url
        });
    }).on('hide.bs.modal', () => {
        clearModal();
    });
};

/**
 * Bootstrap tooltip
 *
 * @param {string} [selector=body] Selector for the tooltip elements, defaults to 'body'
 *                                 to apply to all elements with the data-bs-tooltip attribute.
 *                                 Example: 'body', '.my-tooltip-class', '#my-tooltip-id'
 *                                 If you want to apply it to a specific element, use that element's selector.
 *                                 If you want to apply it to all elements with the data-bs-tooltip attribute,
 *                                 use 'body' or leave it empty.
 * @param {string} [namespace=afat] Namespace for the tooltip
 * @returns {void}
 */
const afatBootstrapTooltip = ({selector = 'body', namespace = 'afat'}) => { // eslint-disable-line no-unused-vars
    document.querySelectorAll(`${selector} [data-bs-tooltip="${namespace}"]`)
        .forEach((tooltipTriggerEl) => {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
};
