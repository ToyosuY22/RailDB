$(document).ready(function () {
    $("[class*='dt-detail']").dataTable({
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.12.1/i18n/ja.json"
        },
        "fixedColumns": {
            "left": 1,
        },
        "order": [[0, 'asc']],
        "columnDefs": [{
            "targets": 0,
            "visible": false
        }],
        "scrollCollapse": true, "scrollX": true, "paging": false,
        "searching": false, "bInfo": false, "ordering": false
    });
});
