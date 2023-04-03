$(document).ready(function () {
    $('#datatable_railway').dataTable({
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.12.1/i18n/ja.json"
        },
        "processing": true,
        "serverSide": true,
        "ajax": "/library/json/station",
        "order": [[7, 'asc'], [8, 'asc']],
        "columnDefs": [
            {
                "targets": [2, 3],
                "searchable": false
            },
            {
                "targets": [4],
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
                "targets": [6],
                "render":
                    function (data) {
                        return `<a href="/library/database/detail_station/${data}" class="btn btn-primary btn-sm"><i class="fa-solid fa-eye"></i> 詳細</a>`
                    },
                "searchable": false, "orderable": false
            },
            {
                "targets": [7, 8],
                "visible": false,
            },
        ]
    });
});
