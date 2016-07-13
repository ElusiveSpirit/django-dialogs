/*
    NotificationHandler class
----------------------------------------------------
Required:
    jquery,
    move

Shows notification array and organize it's
*/

function NotificationHandler() {
    this._queue = [];
    this._timeout = 3000;

    this._container = document.createElement('div');
    this._container.className = "notification-container";
    document.body.appendChild(this._container);
}

NotificationHandler.prototype.addNotification = function(notification) {
    this._queue.push(notification);
    var index = setTimeout(this.removeNotification, this._timeout, this, notification);
    notification.setIndex(index);
    this.show(notification.getObj(this._queue.length - 1));
    notification.show();
}

NotificationHandler.prototype.removeNotification = function(handler, notification) {
    var index = notification.getIndex();
    handler._queue.forEach(function(item, i, arr) {
        if (item.getIndex() == index) {
            var removing_obj = item;
            delete handler._queue[i];
            removing_obj.hide(handler._queue[i + 1]);
            return false;
        }
    });
}

NotificationHandler.prototype.show = function(obj) {
    this._container.appendChild(obj);
}


function Notification(text) {
    this._text = text;
    // TODO Get object's height instead
    this._moving_length = 50;
    this._template_top = '';
    this._template_bot = '';

    this._obj = document.createElement('div');
    this._obj.className = "notification";
    this._obj.setAttribute("style", "opacity: 0.0;");
    this._obj.innerHTML = this._template_top + this._text + this._template_bot;
}

Notification.prototype.getObj = function(level) {
    this._level = level;
    return this._obj;
}

Notification.prototype.setIndex = function(index) {
    this._index = index;
    this._obj.id = index;
}

Notification.prototype.getIndex = function() {
    return this._index;
}

Notification.prototype.getHeight = function() {
    return $('#' + this._index).height();
}

Notification.prototype.moveUp = function(height) {
    var obj = document.getElementById(this._index);
    $(obj).css('margin-top', parseInt(window.getComputedStyle(obj).getPropertyValue("margin-top")) + height);

    move(obj)
      .sub('margin-top', height)
      .end();
}

Notification.prototype.show = function() {
    var timer;
    var obj = document.getElementById(this._index);
    function appear() {
        var opacity = parseFloat(window.getComputedStyle(obj).getPropertyValue("opacity"));
        if (opacity < 1) {
                obj.style.opacity = opacity + 0.1;
            timer = setTimeout(appear, 20);
        }
    }
    timer = setTimeout(appear, 20);
}

Notification.prototype.hide = function(bottom_obj) {
    var timer;
    var obj = document.getElementById(this._index);
    var height = this.getHeight();
    function dissaper() {
        var opacity = parseFloat(window.getComputedStyle(obj).getPropertyValue("opacity"));
        if (opacity > 0) {
            obj.style.opacity = opacity - 0.1;
            timer = setTimeout(dissaper, 20);
        } else {
            obj.remove();
            if (typeof bottom_obj !== "undefined") {
                bottom_obj.moveUp(height);
            }
        }
    }
    timer = setTimeout(dissaper, 20);
}
