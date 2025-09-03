/* global afatSettings, moment, AFAT_DATETIME_FORMAT, fetchGet */

$(document).ready(() => {
    'use strict';

    const dtLanguage = afatSettings.dataTable.language;

    /**
     * DataTable :: FAT link list
     */
    fetchGet({url: afatSettings.url.logs})
        .then((data) => {
            $('#afat-logs').DataTable({
                language: dtLanguage,
                data: data,
                columns: [
                    {
                        data: 'log_time',
                        render: {
                            display: (data) => {
                                return moment(data.time).utc().format(AFAT_DATETIME_FORMAT);
                            },
                            _: 'timestamp'
                        }
                    },
                    {data: 'log_event'},
                    {data: 'user'},
                    {
                        data: 'fatlink',
                        render: {
                            display: 'html',
                            _: 'hash'
                        }
                    },
                    {data: 'description'}
                ],

                order: [
                    [0, 'desc']
                ],

                filterDropDown: {
                    columns: [
                        {
                            idx: 1
                        },
                        {
                            idx: 2
                        }
                    ],
                    autoSize: false,
                    bootstrap: true,
                    bootstrap_version: 5
                },

                stateSave: true,
                stateDuration: -1
            });
        })
        .catch((error) => {
            console.error('Error fetching FAT logs:', error);
        });
});
