$(document).ready(function () {
    $('#dt').dataTable({
        "order": [[0, 'asc']],
        "columnDefs": [{
            "targets": 0,
            "searchable": false, "visible": false
        }],
        "paging": false, "info": false, "searching": false
    });
});
