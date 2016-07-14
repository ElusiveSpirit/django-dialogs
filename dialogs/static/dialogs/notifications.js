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
    // For history..
    this._storage = [];
    this._timeout = 3000;

    this._container = document.createElement('div');
    this._container.className = "notification-container";
    document.body.appendChild(this._container);
}

NotificationHandler.prototype.addNotification = function(notification) {
    this._queue.push(notification);
    var index = setTimeout(this.removeNotification, this._timeout, this, notification);
    this._storage.push({
        'id' : index,
        'notification' : notification,
        'time' : Date.now(),
        'has_read' : false,
    });
    notification.setIndex(index);
    this.addObj(notification.getObj());
    notification.show();
}

NotificationHandler.prototype.removeNotification = function(handler, notification) {
    handler._queue.forEach(function(item, i, arr) {
        if (item.getIndex() == notification.getIndex()) {
            var removing_obj = item;
            delete handler._queue[i];
            removing_obj.hide();
            return false;
        }
    });
}

NotificationHandler.prototype.addObj = function(obj) {
    this._container.appendChild(obj);
}


function Notification(text) {
    this._text = text;
    this._moving_length = 50;
    this._template_top = '';
    this._template_bot = '';

    this._obj = document.createElement('div');
    this._obj.className = "notification";
    this._obj.setAttribute("style", "opacity: 0.0;");
    this._obj.innerHTML = this._template_top + this._text + this._template_bot;
}

Notification.prototype.getObj = function() {
    return this._obj;
}

Notification.prototype.setIndex = function(index) {
    this._index = index;
    this._obj.id = "notification_" + index;
}

Notification.prototype.getIndex = function() {
    return this._index;
}

Notification.prototype.getID = function() {
    return "notification_" + this.getIndex();
}

Notification.prototype.getHeight = function() {
    return $('#notification_' + this._index).outerHeight(true);
}

Notification.prototype.show = function() {
    var obj = document.getElementById(this.getID());
    function appear() {
        var opacity = parseFloat(window.getComputedStyle(obj).getPropertyValue("opacity"));
        if (opacity < 1) {
            obj.style.opacity = opacity + 0.1;
            setTimeout(appear, 20);
        }
    }
    setTimeout(appear, 20);
}

Notification.prototype.hide = function() {
    var obj = document.getElementById(this.getID());
    var height = this.getHeight();
    function dissaper() {
        var opacity = parseFloat(window.getComputedStyle(obj).getPropertyValue("opacity"));
        if (opacity > 0) {
            obj.style.opacity = opacity - 0.1;
            setTimeout(dissaper, 20);
        } else {
            move(obj)
              .sub('margin-top', height)
              .end(function (){
                obj.remove();
              });
        }
    }
    setTimeout(dissaper, 20);
}
