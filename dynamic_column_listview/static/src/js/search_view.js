odoo.define('dynamic_column_listview.SearchView', function (require) {
"use strict";

var Model = require('web.DataModel');
var core = require('web.core');
var SearchView = require('web.SearchView');
var FavoriteMenu = require('web.FavoriteMenu');
var FilterMenu = require('web.FilterMenu');
var GroupByMenu = require('web.GroupByMenu');
var DynamicColumnMenu = require('web.DynamicColumnMenu');

var QWeb = core.qweb;

SearchView.include({
    defaults: _.extend({}, SearchView.prototype.defaults, {
       disable_dynamic_column_listview: false
    }),
    init: function() {
        this._super.apply(this, arguments);
        this.dynamic_column_menu = undefined;
    },

    start: function () {
        return $.when(this._super.apply(this, arguments)).then(this.proxy('show_dynamic_columns_menu'));
    },

    show_dynamic_columns_menu: function() {
        var menu_defs = []
        if (this.$buttons && !this.options.disable_dynamic_column_listview) {
            this.dynamic_column_menu = new DynamicColumnMenu(this);
            menu_defs.push(this.dynamic_column_menu.appendTo(this.$buttons));
        }
        return $.when.apply($, menu_defs);
    }

});


});
