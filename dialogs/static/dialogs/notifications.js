function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function setCookie(key, value) {
    document.cookie = escape(key) + '=' + escape(value);
}

var timezone = getCookie('timezone');

if (timezone == null) {
    setCookie("timezone", jstz.determine().name());
}

function activate_notifications(thread_id, user_name, user_id, number_of_messages) {
    var ws;
    function start_chat_ws() {
        ws = new WebSocket("ws://127.0.0.1:8888/user/" + getCookie('sessionid') + "/");

        ws.onmessage = function(event) {
            var message_data = JSON.parse(event.data);

            // console.log("type = " + message_data.type);
            if (message_data.type == "message") {

            } else if (message_data.type == "message_status") {
              
            } else if (message_data.type == "error") {

            }
      };

        ws.onclose = function(){
            // Try to reconnect in 5 seconds
            // TODO random time!
            setTimeout(function() {start_chat_ws()}, 5000);
        };
    }

    if ("WebSocket" in window) {
        start_chat_ws();
    } else {
        $("form.message_form").html('<div class="outdated_browser_message"><p><em>Ой!</em> Вы используете устаревший браузер. Пожалуйста, установите любой из современных:</p><ul><li>Для <em>Android</em>: <a href="http://www.mozilla.org/ru/mobile/">Firefox</a>, <a href="http://www.google.com/intl/en/chrome/browser/mobile/android.html">Google Chrome</a>, <a href="https://play.google.com/store/apps/details?id=com.opera.browser">Opera Mobile</a></li><li>Для <em>Linux</em>, <em>Mac OS X</em> и <em>Windows</em>: <a href="http://www.mozilla.org/ru/firefox/fx/">Firefox</a>, <a href="https://www.google.com/intl/ru/chrome/browser/">Google Chrome</a>, <a href="http://ru.opera.com/browser/download/">Opera</a></li></ul></div>');
        return false;
    }
    function update_status(message) {
        //$(this).slideUp();
        if (ws.readyState != WebSocket.OPEN) {
            // TODO Error = "Нет подключения к серверу. Проверьте соединение с сетью."
            return;
        }
        if ($(this).children().hasClass("we"))
          return;

        var data = JSON.stringify({
          "type" : "message_status",
          "message_id" : this.id,
          "message_status" : true,
        });

        ws.send(data);
    }
    $("div.chat div.conversation div.message.not_read").live("hover", update_status);

    var typing = false;

    function send_status_typing(status) {
        ws.send(JSON.stringify({
          "type" : "person_status",
          "typing" : status,
        }));
    }

    function send_message() {
        var textarea = $("textarea#message_textarea");
        if (textarea.val() == "") {
            return false;
        }

        if (ws.readyState != WebSocket.OPEN) {
            return false;
        }

        // Adding message block
        var date = new Date(Date.now());
        var time = $.map([date.getHours(), date.getMinutes(), date.getSeconds()], function(val, i) {
            return (val < 10) ? '0' + val : val;
        });
        $("div.mess-new").append('<div class="message not_read"><div class="author we"><span class="datetime">' + time[0] + ':' + time[1] + ':' + time[2] + '</span> ' + user_name + ':<div class="spinner"><div class="bounce1"></div><div class="bounce2"></div><div class="bounce3"></div></div></div><p class="message">' + textarea.val()) + '</p></div>';
        scroll_chat_window();
        number_of_messages["total"]++;
        number_of_messages["sent"]++;
        $("div.chat p.messages").html('<span class="total">' + number_of_messages["total"] + '</span> ' + getNumEnding(number_of_messages["total"], ["сообщение", "сообщения", "сообщений"]) + ' (<span class="received">' + number_of_messages["received"] + '</span> получено, <span class="sent">' + number_of_messages["sent"] + '</span> отправлено)');

        var data = JSON.stringify({
          "type" : "message",
          "text" : textarea.val()
        });

        ws.send(data);
        textarea.val("");
        // TODO Lags when user send message and continue typing
        typing = false;
        send_status_typing(typing);
    }

    $("form.message_form div.send button").click(send_message);

    function update_messages() {
        // TODO Async process
        var mess_list = $("div.chat div.conversation div.message.not_read").trigger('mouseenter');
    }

    $("textarea#message_textarea").focus(update_messages);
    $("textarea#message_textarea").focusout(function (e) {
        if (typing) {
            typing = false;
            send_status_typing(typing);
        }
    });

    $("textarea#message_textarea").keydown(function (e) {
        // Ctrl + Enter
        if (e.ctrlKey && e.keyCode == 13) {
            send_message();
        }
        if (!typing && e.keyCode >= 32) {
            typing = true;
            send_status_typing(typing);
        }
        update_messages();
    });
}
