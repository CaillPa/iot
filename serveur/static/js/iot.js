$(document).ready(function() {
    bindValue("ledr");
    bindValue("ledg");
    bindValue("lcd");
    bindValue("buzzer");
    bindValue("servo");

    // update span from server automagically
    function updateValue(key) {
        $.getJSON($SCRIPT_ROOT + '/get?key='+key,
            null,
            function(data) {
                $("span#"+key).text(data[key]);
            }.bind(key));
        return false;
    }

    // query the server to update displayed values
    setInterval(() => {
        //updateValue("ledr");
        //updateValue("ledg");
        //updateValue("buzzer");
        //updateValue("servo");
        updateValue("rfid");
        //updateValue("lcd");
    }, 3000);
        
});

function checkCheckbox(elem) {
    if(elem.checked == true) {
        elem.value = '1';
    } else {
        elem.value = '0';
    }
}

function bindValue(id) {
    $("input#"+id).change(function() {
        $.post($SCRIPT_ROOT+'/put',
        {
            key: id,
            value: $('input#'+id).val()
        });
    });
}

