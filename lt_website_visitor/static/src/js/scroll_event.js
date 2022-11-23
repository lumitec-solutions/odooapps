odoo.define('lt_website_visitor.scroll_page', function (require) {
'use strict';
    var publicWidget = require('web.public.widget');
    publicWidget.registry.Scroll = publicWidget.Widget.extend({
        selector: '#wrapwrap',
        start: function () {
            var self = this;
            var timer = 0;
            console.log("START")
            self._rpc({
                route: '/website/update_visitor_last_connection',
                params: {
                },
            }).then(function (res) {
                console.log("Updated")
            });
            this._onScroll = function (ev) {
                timer++;
                console.log("timer================", timer)
                if(timer == 35){
                    self._rpc({
                        route: '/website/update_visitor_last_connection',
                        params: {
                        },
                    }).then(function (res) {
                        timer = 0;
                    });
                }
            };
            window.addEventListener('scroll', this._onScroll, true);
            return this._super.apply(this, arguments);
        },
    });
    return publicWidget.registry.Scroll;
});
