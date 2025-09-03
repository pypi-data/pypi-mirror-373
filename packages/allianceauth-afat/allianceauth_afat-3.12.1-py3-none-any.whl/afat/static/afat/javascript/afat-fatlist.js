/* global afatSettings, moment, manageModal, AFAT_DATETIME_FORMAT, fetchGet */

$(document).ready(() => {
    'use strict';

    const dtLanguage = afatSettings.dataTable.language;
    const hasPermissions = afatSettings.permissions.addFatLink || afatSettings.permissions.manageAfat;

    // Base columns configuration
    const linkListTableColumns = [
        {data: 'fleet_name'},
        {data: 'fleet_type'},
        {data: 'doctrine'},
        {data: 'creator_name'},
        {
            data: 'fleet_time',
            render: {
                display: (data) => moment(data.time).utc().format(AFAT_DATETIME_FORMAT),
                _: 'timestamp'
            }
        },
        {data: 'fats_number'},
        {data: 'via_esi'},
        {data: 'hash'}
    ];

    // Add actions column if user has permissions
    if (hasPermissions) {
        linkListTableColumns.splice(-2, 0, {
            data: 'actions',
            render: (data) => {
                return data;
            }
        });
    }

    // Column definitions based on permissions
    const linkListTableColumnDefs = [
        {
            targets: [5],
            createdCell: (td) => {
                $(td).addClass('text-end');
            }
        },
        {
            targets: hasPermissions ? [7, 8] : [6, 7],
            visible: false
        }
    ];

    if (hasPermissions) {
        linkListTableColumnDefs.splice(1, 0, {
            targets: [6],
            orderable: false,
            createdCell: (td) => {
                $(td).addClass('text-end');
            }
        });
    }

    const linkListTable = $('#link-list');
    const RELOAD_INTERVAL = 60000;
    let expectedReloadTime = Date.now() + RELOAD_INTERVAL;

    // Initialize DataTable
    const initializeDataTable = (data) => {
        return linkListTable.DataTable({
            language: dtLanguage,
            data: data,
            columns: linkListTableColumns,
            columnDefs: linkListTableColumnDefs,
            order: [[4, 'desc']],
            filterDropDown: {
                columns: [
                    {idx: 1},
                    {
                        idx: 7,
                        title: afatSettings.translation.dataTable.filter.viaEsi
                    }
                ],
                autoSize: false,
                bootstrap: true,
                bootstrap_version: 5
            }
        });
    };

    // Reload DataTable data
    const reloadDataTable = () => {
        const drift = Date.now() - expectedReloadTime;

        if (drift > RELOAD_INTERVAL) {
            const currentPath = window.location.pathname + window.location.search + window.location.hash;

            if (currentPath.startsWith('/')) {
                window.location.replace(currentPath);

                return;
            }

            console.error('Invalid redirect URL');
        }

        fetchGet({url: afatSettings.url.linkList})
            .then((newData) => {
                linkListTable.DataTable().clear().rows.add(newData).draw();
            })
            .catch((error) => {
                console.error('Error fetching updated data:', error);
            });

        expectedReloadTime += RELOAD_INTERVAL;

        setTimeout(reloadDataTable, Math.max(0, RELOAD_INTERVAL - drift));
    };

    // Initialize table and auto-reload
    fetchGet({url: afatSettings.url.linkList})
        .then((data) => {
            initializeDataTable(data);

            setTimeout(reloadDataTable, RELOAD_INTERVAL);
        })
        .catch((error) => {
            console.error('Error fetching link list:', error);
        });

    // Initialize modals
    [
        afatSettings.modal.cancelEsiFleetModal.element,
        afatSettings.modal.deleteFatLinkModal.element,
    ].forEach((modalElement) => {
        manageModal($(modalElement));
    });
});
