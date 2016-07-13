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

function getNumEnding(iNumber, aEndings) {
    var sEnding, i;
    iNumber = iNumber % 100;
    if (iNumber>=11 && iNumber<=19) {
        sEnding=aEndings[2];
    }
    else {
        i = iNumber % 10;
        switch (i)
        {
            case (1): sEnding = aEndings[0]; break;
            case (2):
            case (3):
            case (4): sEnding = aEndings[1]; break;
            default: sEnding = aEndings[2];
        }
    }
    return sEnding;
}

var timezone = getCookie('timezone');

if (timezone == null) {
    setCookie("timezone", jstz.determine().name());
}


function activate_chat(user_name, user_id) {
    $("div.chat form.message_form div.compose textarea").focus();

    function scroll_chat_window() {
        $("div.chat div.conversation").scrollTop($("div.chat div.conversation")[0].scrollHeight);
    }

    function show_message_notification(sender, message_data.text) {

    }

    scroll_chat_window();

    var ws;
    var thread_id = -1;
    function start_chat_ws() {
        ws = new WebSocket("ws://127.0.0.1:8888/ws/" + user_id + "/");

        ws.onopen = function(event) {
            var url_path = window.location.pathname.split( '/' );
            if (url_path[2] == 'chat') {
                thread_id = url_path[3];
                ws.send(JSON.stringify({
                  "type" : "open_dialog",
                  "thread_id" : thread_id,
                }));
            }
        }

        ws.onmessage = function(event) {
            var message_data = JSON.parse(event.data);

            // console.log("type = " + message_data.type);
            if (message_data.type == "message") {
                if (thread_id == message_data.thread_id) {
                    var date = new Date(message_data.timestamp*1000);
                    var time = $.map([date.getHours(), date.getMinutes(), date.getSeconds()], function(val, i) {
                        return (val < 10) ? '0' + val : val;
                    });

                    var status = (message_data.has_read) ? "" : " not_read";
                    var input_html = '<div id="' + message_data.message_id + '" class="message' + status + '">';
                    if (message_data.sender == user_name) {
                        $(".mess-new .message:first-child").remove();
                        input_html += '<div class="author we">';
                    } else {
                        input_html += '<div class="author partner">';
                    }
                    $("div.mess-old").append(input_html + '<span class="datetime">' + time[0] + ':' + time[1] + ':' + time[2] + '</span> ' + message_data.sender + ':</div><p class="message">' + message_data.text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g, '<br />') + '</p></div>');
                    scroll_chat_window();
                } else {
                    show_message_notification(message_data.sender, message_data.text);
                }

            } else if (message_data.type == "message_status") {
                $("#" + message_data.message_id).removeClass("not_read");
            } else if (message_data.type == "person_status") {
                if (message_data.user_id != user_id) {
                    if (message_data.typing) {
                        var text = message_data.username + " набирает сообщение...";
                        $("div.chat div.conversation div.typing").append('<div class="person" name="' + message_data.username + '">' + text + "</div>");
                        scroll_chat_window();
                    } else {
                        $("div.chat div.conversation div.typing div[name='" + message_data.username + "']").slideUp();
                        setTimeout(function() {
                            $("div.chat div.conversation div.typing div[name='" + message_data.username + "']").remove();
                        }, 1000)
                    }
                }
            } else if (message_data.type == "message_error") {

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
