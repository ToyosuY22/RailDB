$(document).ready(function () {
    $('#datatable_railway').dataTable({
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.12.1/i18n/ja.json"
        },
        "processing": true,
        "serverSide": true,
        "ajax": "/library/json/operator",
        "order": [[3, 'asc']],
        "columnDefs": [{
            "targets": 2,
            "render":
                function (data) {
                    return `<a href="/library/database/detail_operator/${data}" class="btn btn-primary btn-sm"><i class="fa-solid fa-eye"></i> 詳細</a>`
                },
            "searchable": false, "orderable": false
        },
        {
            target: 3,
            visible: false,
        }]
    });
});
