odoo.define('lumitec_chatter.composer_send', function (require) {
"use strict";
const { Composer } = require("@mail/components/composer/composer")
const { Component } = owl;
const { patch } = require('web.utils');


patch(Composer.prototype, 'ComposerLead',{
    _onClickSend() {
        if ($('.custom-control-input')[0].checked === true){
            var email = $('.custom-control-input')[0].nextElementSibling.innerHTML
            var content = $('.o_ComposerTextInput_textarea')[0].textContent
            this.rpc({
                model: 'mail.mail',
                method: 'send_mail_to_non_contact',
                args: [, email, content],

            }).then(function(result){});
            this._postMessage();
            this.composerView.update({ doFocus: true });
        }
        else {
             this._postMessage();
             this.composerView.update({ doFocus: true });
        }
    }

})

})