odoo.define('dynamic_column_listview.ViewManager', function (require) {
"use strict";

var core = require('web.core');
var ListView = require('web.ListView');
var SearchView = require('web.SearchView');
var ViewManager = require('web.ViewManager');
var QWeb = core.qweb;


ViewManager.include({

    _display_view: function (view_options, old_view) {
        self = this;
        return $.when(self._super(view_options, old_view)).done(function () {
            $('#dynamic_column_dropdown').toggle(self.active_view.type == 'list');
            if (self.active_view.type == 'list') {
                $('#select_columns,#save_dynamic_columns,#showcb,.dynamic_columns_saving_options').unbind('click');

                $('#select_columns').click($.proxy(self.active_view.controller, 'my_setup_columns'));
                $('#save_dynamic_columns').click($.proxy(self.active_view.controller, 'hide_show_columns'));
                $('#showcb,.dynamic_columns_saving_options').click($.proxy(self.active_view.controller, 'stop_event'));
            }
        });
    },

    switch_mode: function(view_type, no_store, view_options) {
        if (view_type == 'list') {
            this.views.list.columnsSortOrder = {}
            this.views.list.columnsSortOrderGrouped = {}
        }
        return this._super(view_type, no_store, view_options);
    },

});


});
