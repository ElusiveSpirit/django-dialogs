/*
    NotificationHandler class
----------------------------------------------------
Required:
    jquery,
    move

Base div class = notification-container

Shows notification array and organize it's
*/
class NotificationHandler {

    constructor() {
        this._queue = [];
        // For history..
        this._storage = [];
        this._default_timeout = 4000;

        this._container = document.createElement('div');
        this._container.className = "notification-container";
        document.body.appendChild(this._container);
    }

    addNotification(notification) {
        this._queue.push(notification);

        let timeout = notification.timeout;
        if (typeof timeout == 'undefined') {
            timeout = this._default_timeout;
        }

        if (notification.autoremove) {
            var index = setTimeout(
                this.removeNotification.bind(this)
            , timeout, notification);
        } else {
            var index = setTimeout(this.doNothing, 0);
        }

        this._storage.push({
            'id' : index,
            'notification' : notification,
            'time' : Date.now(),
            'has_read' : false,
        });
        notification.index = index;
        this.addObj(notification.obj);
        notification.show();
    }

    removeNotification(notification) {
        var that = this;
        clearTimeout(notification.index);
        that._queue.forEach(function(item, i, arr) {
            if (item.index == notification.index) {
                var removing_obj = item;
                delete that._queue[i];
                removing_obj.hide();
                return false;
            }
        });
    }

    addObj(obj) {
        this._container.appendChild(obj);
    }

    doNothing() {
        return;
    }
}


class BaseNotification {

    constructor(html, autoremove=true, timeout=1000) {
        this._timeout = timeout;
        this._autoremove = autoremove;

        this._obj = document.createElement('div');
        this._obj.className = "notification";
        this._obj.setAttribute("style", "opacity: 0.0;");
        this._obj.innerHTML = html;
    }

    set extra_classes(classes) {
        this._obj.className += ` ${classes}`;
    }

    set index(index) {
        this._index = index;
        this._obj.id = `notification_${index}`;
    }

    get index() {
        return this._index;
    }

    get obj_id() {
        return `notification_${this.index}`;
    }

    get autoremove() {
        return this._autoremove;
    }

    get timeout() {
        return this._timeout;
    }

    get element() {
        return document.getElementById(this.obj_id);
    }

    get obj() {
        return this._obj;
    }

    get obj_height() {
        return $(`#${this.obj_id}`).outerHeight(true);
    }

    get innerHTML() {
        return this._obj.innerHTML;
    }

    set click(func) {
        this._obj.onclick = func;
    }

    show() {
        var obj = this.element;
        function appear() {
            var opacity = parseFloat(window.getComputedStyle(obj).getPropertyValue("opacity"));
            if (opacity < 1) {
                obj.style.opacity = opacity + 0.1;
                setTimeout(appear, 20);
            }
        }
        setTimeout(appear, 20);
    }

    hide() {
        var obj = this.element;
        var height = this.obj_height;
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
}

class AlertNotification extends BaseNotification {

    constructor(text, timeout=3000) {
        super(text, true, timeout);
        this.extra_classes = 'alert';
    }
}

class ErrorNotification extends BaseNotification {

    constructor(text, autoremove=true, timeout=3000) {
        super(text, autoremove, timeout);
        this.extra_classes = 'error';
    }
}

class InfoNotification extends BaseNotification {

    constructor(text) {
        super(text, false);
        this.extra_classes = 'info';
        var that = this;
        this.click = function (){
            that.hide();
        }
    }
}

class MessageNotification extends BaseNotification {

    constructor(author, img, text, date, autoremove=true) {
        var template = `
            <div class="message">
              <img src="${img}" width="40" height="40" />
              <div class="content">
                <h4>${author}</h4>
                <p>${text}</p>
                <p class="date">${date}</p>
              </div>
              <div style="clear:both;"></div>
            </div>`;

        super(template, autoremove, 5000);

        var that = this;
        this.click = function (){
            that.hide();
        }
    }
}
