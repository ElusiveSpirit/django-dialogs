/*
NotificationHandler class

Shows notification array and organize it's
*/

function NotificationHandler() {
    this._queue = [];
    this._timeout = 2000;

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
    var id_to_remove;
    handler._queue.forEach(function(item, i, arr) {
        if (item.getIndex() == index) {
            item.hide();
            id_to_remove = i;
            return false;
        }
    });
    delete handler._queue[id_to_remove];
    handler._queue.forEach(function(item, i, arr) {
        item.moveUp(i);
    });
}

NotificationHandler.prototype.show = function(obj) {
    this._container.appendChild(obj);
}


function Notification(text) {
    this._text = text;
    // TODO Get object's height instead
    this._moving_length = 50;
    this._template_top = "";
    this._template_bot = "";

    this._obj = document.createElement('div');
    this._obj.className = "notification";
    this._obj.setAttribute("style", "opacity: 0.0;");
    this._obj.innerHTML = this._template_top + this._text + this._template_bot;
}

Notification.prototype.getObj = function(level) {
    this._level = level;
    this._obj.setAttribute("style", "margin-top:" + (level * this._moving_length).toString() + "px; opacity: 0.0;");
    return this._obj;
}

Notification.prototype.setIndex = function(index) {
    this._index = index;
    this._obj.id = index;
}

Notification.prototype.getIndex = function() {
    return this._index;
}

Notification.prototype.moveUp = function(level) {
    if (this._level > level) {
        move("#" + this._index)
          .sub('margin-top', (this._level - level) * this._moving_length)
          .end();
    }
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

Notification.prototype.hide = function() {
    var timer;
    var obj = document.getElementById(this._index);
    function dissaper() {
        var opacity = parseFloat(window.getComputedStyle(obj).getPropertyValue("opacity"));
        if (opacity > 0) {
            obj.style.opacity = opacity - 0.1;
            timer = setTimeout(dissaper, 20);
        } else {
            obj.remove();
        }
    }
    timer = setTimeout(dissaper, 20);
}
