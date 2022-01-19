odoo.define('web.DynamicColumnMenu', function (require) {
"use strict";

var Widget = require('web.Widget');
var core = require('web.core');
var data_manager = require('web.data_manager');
var search_inputs = require('web.search_inputs');

var QWeb = core.qweb;

return Widget.extend({
    template: 'SearchView.DynamicColumnMenu',
    events: {
        'click #select_columns': function (event) {
            event.preventDefault();
        },
        'hidden.bs.dropdown': function () {
            $('#dynamic_dropdown_menu').hide();
        },
    },
});

});
