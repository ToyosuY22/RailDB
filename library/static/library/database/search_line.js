$(document).ready(function () {
    $('#datatable_railway').dataTable({
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.12.1/i18n/ja.json"
        },
        "processing": true,
        "serverSide": true,
        "ajax": "/library/json/line",
        "order": [[12, 'asc']],
        "columnDefs": [
            {
                "targets": [0, 1],
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
                "targets": [4],
                "render":
                    function (data) {
                        return data ? data : '─'
                    },
                "searchable": false
            },
            {
                "targets": [10],
                "render":
                    function (data) {
                        if (data == '0') {
                            return '0.0'
                        } else {
                            return `${data.slice(0, -1)}.${data.slice(-1)}`
                        }
                    },
                "searchable": false, "orderable": false
            },
            {
                "targets": [11],
                "render":
                    function (data) {
                        return `<a href="/library/database/detail_line/${data}" class="btn btn-primary btn-sm"><i class="fa-solid fa-eye"></i> 詳細</a>`
                    },
                "searchable": false, "orderable": false
            },
            {
                "targets": [12],
                "visible": false,
            },
        ]
    });
});
