/* global afatSettings, convertStringToSlug, sortTable, ClipboardJS, manageModal, fetchGet */

$(document).ready(() => {
    'use strict';

    const dtLanguage = afatSettings.dataTable.language;
    const fatListTable = $('#fleet-edit-fat-list');
    const shipTypeOverviewTable = $('#fleet-edit-ship-types');

    // Helper function to update ship type counts
    const updateShipTypeCounts = (data) => {
        const shipTypeCounts = {};

        // Count ship types
        data.forEach((item) => {
            shipTypeCounts[item.ship_type] = (shipTypeCounts[item.ship_type] || 0) + 1;
        });

        // Clear and rebuild ship type overview
        shipTypeOverviewTable.find('tbody').empty();

        Object.entries(shipTypeCounts).forEach(([shipType, count]) => {
            const shipTypeSlug = convertStringToSlug(shipType);

            shipTypeOverviewTable.append(
                `<tr class="shiptype-${shipTypeSlug}"><td class="ship-type">${shipType}</td><td class="ship-type-count text-end">${count}</td></tr>`
            );
        });

        sortTable(shipTypeOverviewTable, 'asc');
    };

    // Initialize DataTable
    const initializeDataTable = (data) => {
        fatListTable.DataTable({
            language: dtLanguage,
            data: data,
            columns: [
                {data: 'character_name'},
                {data: 'system'},
                {data: 'ship_type'},
                {data: 'actions'}
            ],
            columnDefs: [
                {
                    targets: [3],
                    orderable: false,
                    createdCell: (td) => {
                        $(td).addClass('text-end');
                    }
                }
            ],
            order: [[0, 'asc']],
            stateSave: true,
            stateDuration: -1
        });

        updateShipTypeCounts(data);
    };

    // Load initial data
    fetchGet({url: afatSettings.url})
        .then(initializeDataTable)
        .catch((error) => {
            console.error('Error fetching FAT list:', error);
        });

    // Auto-reload functionality
    if (afatSettings.reloadDatatable === true) {
        const intervalReloadDatatable = 15000;
        let expectedReloadTime = Date.now() + intervalReloadDatatable;

        const reloadDataTable = () => {
            const drift = Date.now() - expectedReloadTime;

            if (drift > intervalReloadDatatable) {
                const currentPath = window.location.pathname + window.location.search + window.location.hash;

                if (currentPath.startsWith('/')) {
                    window.location.replace(currentPath);

                    return;
                } else {
                    console.error('Invalid redirect URL');
                }
            }

            fetchGet({url: afatSettings.url})
                .then((newData) => {
                    const dataTable = fatListTable.DataTable();

                    dataTable.clear().rows.add(newData).draw();
                    updateShipTypeCounts(newData);
                })
                .catch((error) => {
                    console.error('Error reloading data:', error);
                });

            expectedReloadTime += intervalReloadDatatable;

            setTimeout(reloadDataTable, Math.max(0, intervalReloadDatatable - drift));
        };

        setTimeout(reloadDataTable, intervalReloadDatatable);
    }

    // Initialize clipboard and modals
    const clipboard = new ClipboardJS('.copy-btn');
    clipboard.on('success', () => {
        $('.copy-btn').tooltip('show');
    });

    [
        afatSettings.modal.cancelEsiFleetModal.element,
        afatSettings.modal.deleteFatModal.element,
        afatSettings.modal.reopenFatLinkModal.element
    ].forEach((modalElement) => {
        manageModal($(modalElement));
    });
});
