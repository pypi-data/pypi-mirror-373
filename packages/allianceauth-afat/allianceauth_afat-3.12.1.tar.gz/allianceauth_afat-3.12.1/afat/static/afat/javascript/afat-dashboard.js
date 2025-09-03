/* global afatSettings, characters, moment, manageModal, AFAT_DATETIME_FORMAT, fetchGet */

$(document).ready(() => {
    'use strict';

    const dtLanguage = afatSettings.dataTable.language;

    /**
     * Common date renderer for DataTables
     */
    const dateRenderer = {
        display: (data) => moment(data.time).utc().format(AFAT_DATETIME_FORMAT),
        _: 'timestamp'
    };

    /**
     * Common DataTable configuration
     */
    const commonTableConfig = {
        language: dtLanguage,
        paging: false,
        ordering: false,
        searching: false,
        info: false
    };

    /**
     * Initialize character FAT tables
     */
    const initCharacterFatTables = () => {
        const characterTableColumns = [
            {data: 'fleet_name'},
            {data: 'fleet_type'},
            {data: 'doctrine'},
            {data: 'system'},
            {data: 'ship_type'},
            {data: 'fleet_time', render: dateRenderer}
        ];

        characters.forEach((character) => {
            const table = $('#recent-fats-character-' + character.charId);
            const url = afatSettings.url.characterFats.replace('0', character.charId);

            fetchGet({url})
                .then((data) => {
                    table.DataTable({
                        ...commonTableConfig,
                        data,
                        columns: characterTableColumns
                    });
                })
                .catch((error) => {
                    console.error('Error fetching recent FATs for character:', character.charId, error);
                });
        });
    };

    /**
     * Initialize recent FAT links table
     */
    const initRecentFatLinksTable = () => {
        const columns = [
            {data: 'fleet_name'},
            {data: 'fleet_type'},
            {data: 'doctrine'},
            {data: 'creator_name'},
            {data: 'fleet_time', render: dateRenderer}
        ];

        const columnDefs = [];
        const hasPermissions = afatSettings.permissions.addFatLink || afatSettings.permissions.manageAfat;

        if (hasPermissions) {
            columns.push({
                data: 'actions',
                render: (data) => data
            });

            columnDefs.push({
                targets: [5],
                orderable: false,
                createdCell: (td) => $(td).addClass('text-end')
            });
        }

        dtLanguage.emptyTable = `<div class="aa-callout aa-callout-warning" role="alert">
            <p>${afatSettings.translation.dataTable.noFatlinksWarning}</p>
        </div>`;

        fetchGet({url: afatSettings.url.recentFatLinks})
            .then((data) => {
                $('#dashboard-recent-fatlinks').DataTable({
                    ...commonTableConfig,
                    data: data,
                    columns: columns,
                    columnDefs: columnDefs
                });
            })
            .catch((error) => {
                console.error('Error fetching recent FAT links:', error);
            });
    };

    /**
     * Initialize modals
     */
    const initModals = () => {
        const modals = [
            afatSettings.modal.cancelEsiFleetModal.element,
            afatSettings.modal.deleteFatLinkModal.element
        ];

        modals.forEach(modalElement => {
            manageModal($(modalElement));
        });
    };

    // Initialize components
    if (characters.length > 0) {
        initCharacterFatTables();
    }

    initRecentFatLinksTable();
    initModals();
});
