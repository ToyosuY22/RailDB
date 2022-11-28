$(document).ready(function () {
    $('.table').filter(function () {
        return this.id.match(/dt/);
    }).dataTable({
        "order": [[0, 'asc']],
        "columnDefs": [{
            "targets": 0,
            "searchable": false, "visible": false
        }],
        "paging": false, "info": false, "searching": false
    });
});
