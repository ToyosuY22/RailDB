$(document).ready(function () {
    $('#datatable_railway').dataTable({
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.12.1/i18n/ja.json"
        },
        "processing": true,
        "serverSide": true,
        "ajax": "/library/json/line",
        "fixedColumns": {
            "left": 1,
        },
        "scrollCollapse": true,
        "scrollX": true,
        "order": [[12, 'asc']],
        "columnDefs": [
            {
                "target": 0,
                "render":
                    function (data, _, row) {
                        return `<span class="wrap-column"><a href="/library/database/detail_line/${row[11]}">${data ? data : '（路線名なし）'}</a></span>`
                    },
            },
            {
                "target": 1,
                "render":
                    function (data) {
                        return data ? data : '（路線名なし）'
                    },
            },
            {
                "targets": [2, 3, 5, 7, 8, 9],
                "searchable": false
            },
            {
                "target": 4,
                "render":
                    function (data) {
                        return data ? data : '─'
                    },
                "searchable": false
            },
            {
                "target": 10,
                "render":
                    function (data) {
                        if (data.length == 0) {
                            return '0.0'
                        } else if (data.length == 1) {
                            return `0.${data.slice(-1)}`
                        } else {
                            return `${data.slice(0, -1)}.${data.slice(-1)}`
                        }
                    },
                "searchable": false, "orderable": false,
                "className": "dt-body-right"
            },
            {
                "targets": [11, 12],
                "visible": false,
            },
        ]
    });
});
