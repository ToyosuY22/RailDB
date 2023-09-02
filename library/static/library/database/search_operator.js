$(document).ready(function () {
    $('#datatable_railway').dataTable({
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.12.1/i18n/ja.json"
        },
        "processing": true,
        "serverSide": true,
        "ajax": "/library/json/operator",
        "fixedColumns": {
            "left": 1,
        },
        "scrollCollapse": true,
        "scrollX": true,
        "order": [[3, 'asc']],
        "columnDefs": [{
            "targets": 0,
            "render":
                function (data, _, row) {
                    return `<span class="wrap-column"><a href="/library/database/detail_operator/${row[2]}">${data}</a></span>`
                },
        }, {
            "target": 2,
            "visible": false
        }, {
            "target": 3,
            "visible": false
        }
        ]
    });
});
