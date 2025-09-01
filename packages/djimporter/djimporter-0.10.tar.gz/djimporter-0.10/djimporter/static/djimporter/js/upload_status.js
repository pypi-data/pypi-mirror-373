let current_status = $('#js-data').data('importlog-status');
if (['running', 'created'].includes(current_status)){
    getData();
}

function getData() {
    let url = $('#js-data').data('importlog-status-url');
        $.ajax({
        url : url,
        dataType: "json",
        success : function(data) {
            let status = data['status'];
            if (current_status != status)
                location.reload();
            if (current_status == 'created'){
                setTimeout(getData, 1000);
            } else if (current_status == 'running'){
                setTimeout(getData, 10000);
            }
        }
    });
}
