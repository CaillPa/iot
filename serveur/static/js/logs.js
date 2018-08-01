$(document).ready(function() {
    var messages = null;
    var logs = null;
    var auths = null;
    var i = 0;  // messages
    var j = 0;  // rfid
    var k = 0;  // auth

    $("#aj_badge").click(function(){
        $.post($SCRIPT_ROOT+'/putbadge',
            {
                key: 'badge',
                value: $('input#n_badge').val()
            });
    });

    $("#aj_message").click(function(){
        $.post($SCRIPT_ROOT+'/put',
            {
                key: 'lcd',
                value: $('input#n_msg').val()
            });
    });

    function add_rows_msg() {
        if(messages == null) {
            return;
        }
        while(i < messages.length) {
            add_row_msg(messages[i][0], messages[i][1]);
            i++;
        }
    }

    function add_rows_log() {
        if(logs == null) {
            return;
        }
        while(j < logs.length) {
            add_row_log(logs[j][0], logs[j][1]);
            j++;
        }
    }

    function add_rows_auth() {
        if(auths == null) {
            return;
        }
        while(k < auths.length) {
            add_row_auth(auths[k], auths[k]);
            k++;
        }
    }

    function add_row_msg(date, msg) {
        $('#msg_table').append('<tr><td>'+date+'</td><td>'+msg+'</td></tr>');
    }

    function add_row_log(date, badge) {
        $('#rfid_table').append('<tr><td>'+date+'</td><td>'+badge+'</td></tr>');
    }

    function add_row_auth(badge) {
        $('#auth_table').append('<tr><td><span id="row'+k+'">'+badge+'</span></td><td><button type="button" class="btn btn-danger btn-sm" id="btn'+k+'">suppr.</button></td></tr>');
        $('button#btn'+k).click(function() {
            $.post($SCRIPT_ROOT+'/rmbadge',
            {
                key: 'badge',
                value: this.parentNode.parentNode.firstChild.textContent
            });
            $("#auth_table tbody tr").remove();
            auths = null;
            k = 0;
        });
    }

    function rem_row(id) {
        $.post($SCRIPT_ROOT+'/rmbadge',
            {
                key: 'badge',
                value: $('span#row'+id).val()
            });
        auths = null;
        k = 0;
        $("#auth_table tbody tr").remove();
    }

    function fetch_messages() {
        $.getJSON($SCRIPT_ROOT + '/getmsg',
            null,
            function(result) {
                messages = result.messages;
            });
        return false;
    }

    function fetch_logs() {
        $.getJSON($SCRIPT_ROOT + '/getlog',
            null,
            function(result) {
                logs = result.logs;
            });
        return false;
    }

    function fetch_auths() {
        $.getJSON($SCRIPT_ROOT + '/getauth',
            null,
            function(result) {
                auths = result.auths;
            });
        return false;
    }

    setInterval(() => {
        fetch_messages();
        fetch_logs();
        fetch_auths();
        add_rows_msg();
        add_rows_log();
        add_rows_auth();
    }, 1000);

});