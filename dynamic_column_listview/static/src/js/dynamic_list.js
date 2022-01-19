odoo.define('dynamic_column_listview.shcolumns', function (require) {
"use strict";

var core = require('web.core');
var ListView = require('web.ListView');
var WebData = require('web.data');
var WebManager = require('web.ViewManager');
var QWeb = core.qweb;
var utils = require('web.utils');


/**
 * Serializes concurrent calls to this asynchronous method. The method must
 * return a deferred or promise.
 *
 * Current-implementation is class-serialized (the mutex is common to all
 * instances of the list view). Can be switched to instance-serialized if
 * having concurrent list views becomes possible and common.
 */
function synchronized(fn) {
	console.log("synchronized");
    var fn_mutex = new utils.Mutex();
    console.log("synchronized 1");
    return function () {
    	console.log("synchronized 2");
        var obj = this;
        var args = _.toArray(arguments);
        return fn_mutex.exec(function () {
        	console.log("synchronized 3");
            if (obj.isDestroyed()) { return $.when(); }
            console.log("synchronized end middle");
            return fn.apply(obj, args);
        });
    };
}

ListView.include({
    load_list: function() {
    	console.log("load_list");
        self = this;
        var result = this._super();

        if (!self.ViewManager) {
            return result;
        }
        if (!self.ViewManager.active_view) {
            return result;
        }

        if (!self.ViewManager.active_view.controller) {
            return result;
            console.log("load_list end 1");
        }

        $('#dynamic_column_dropdown').toggle(true);
        $('#select_columns,#save_dynamic_columns,#showcb,.dynamic_columns_saving_options').unbind('click');

        $('#select_columns').click($.proxy(self.ViewManager.active_view.controller, 'my_setup_columns'));
        $('#save_dynamic_columns').click($.proxy(self.ViewManager.active_view.controller, 'hide_show_columns'));
        $('#showcb,.dynamic_columns_saving_options').click($.proxy(self.ViewManager.active_view.controller, 'stop_event'));
        return result;
        console.log("load_list end 2");
    },

    consistent_column_order: function () {
    	console.log("consistent_column_order  1");
        // Check if tree view columns are ordered as expected
        var columns = _.pluck(this.columns, 'id');

        // Removes '_group' field that is included when a 'group_by' filter is applied
        columns = _.without(columns, '_group');
        var children = _.map(this.fields_view.arch.children, function (child) {
                                return child.attrs.name
                             });
        return _.isEqual(columns, children);
        console.log("consistent_column_order end 1");
    },

    // Override reload_content function to guarantee setup_columns code is
    // executed before loading content in the tree view.
    // This ensures that all column headers and all data gets displayed
    reload_content: synchronized(function () {
    	 console.log("reload_content  1");
        var self = this;
        var current_scroll = $('.table-responsive').scrollLeft();
        if (self.scroll_left != current_scroll && current_scroll > 0) {
            self.scroll_left = current_scroll;
        }
        this.setup_columns(this.fields_view.fields, this.grouped).then(function () {
            if (!self.consistent_column_order()) {
                self.ViewManager.switch_mode('list');
                return
            }
            var reloaded = self.original_reload_content();
            $.when(reloaded).then(function() {
                // Prevent ordering columns when group_by filter is active and
                // when the list view is embedded inside another view
                var $tree_table = $('.o_list_view');
                var $form_view = $('.o_form_view');
                var $table_responsive = $('.table-responsive');
                var not_sortable = ['one2many', 'many2many', 'binary'];

                if (!self.embedded_view && $form_view.length == 0) {
                    var data_id;

                    // Fixes wrong display of helper element when changing order of columns in Google Chrome
                    $table_responsive.css('overflow-x', 'inherit');

                    $tree_table.find('thead th').each(function (index) {
                        if (!self.grouped) {
                            index = index + 1;
                        }
                        data_id = $(this).data('id');
                        $(this).attr("id", data_id);

                        var field = self.fields_view.fields[data_id];
                        if (field) {
                            if (!self.grouped) {
                                $(this).addClass('dragable');
                                $(this).prepend('<span class="column_handle fa fa-arrows"/>');
                            }

                            if (not_sortable.indexOf(field.type) > -1) {
                                $(this).removeClass('o_column_sortable');
                            }
                        }
                    });

                    $tree_table.dragtable({
                        dragaccept:'.dragable',
                        dragHandle:'.column_handle',
                        persistState: function(table) {
                          table.el.find('th').each(function(i) {
                            if($(this).data("id")) {
                                // Keep order of columns while user is still in the tree view
                                // after applying filters and/or group by
                                self.ViewManager.views.list.columnsSortOrder[$(this).attr("id")]= i;
                                self.ViewManager.views.list.columnsSortOrderGrouped[$(this).attr("id")]= i + 1;
                            }
                          });
                        },
                        restoreState: !self.grouped ? self.ViewManager.views.list.columnsSortOrder : self.ViewManager.views.list.columnsSortOrderGrouped
                    });
                    $table_responsive.scrollLeft(self.scroll_left || 0);
                }
                return reloaded;
                console.log("reload_content end 1");
            });
        });
    }),

    // Original load_content function from ListView, without calling
    // setup_columns function at the beginning.
    original_reload_content: function () {
    	console.log("original_reload_content  1");
        if (!this.grouped && this.groups.original_columns) {
            this.groups.columns = this.groups.original_columns;
        }
        var self = this;
        this.$('tbody .o_list_record_selector input').prop('checked', false);
        this.records.reset();
        var reloaded = $.Deferred();
        this.groups.render(function () {
            if (self.dataset.index === null) {
                if (self.records.length) {
                    self.dataset.index = 0;
                }
            } else if (self.dataset.index >= self.records.length) {
                self.dataset.index = self.records.length ? 0 : null;
            }
            self.load_list().then(function () {
                if (!self.grouped && self.display_nocontent_helper()) {
                    self.no_result();
                }
                reloaded.resolve();
            });
        });
        this.do_push_state({
            min: this.current_min,
            limit: this._limit
        });
        return reloaded.promise();
        console.log("original_reload_content end 1");
    },

    render_buttons: function($node) {
    	console.log("render_buttons");
        var self = this;
        $.when(this.session.user_has_group('base.group_configuration'))
        .then(function(is_admin) {
            var view_id = self.view_id || self.fields_view.view_id;
            if (!is_admin || !view_id) {
                $('#apply_for_all').remove();
            }
        });
        this._super($node);
        console.log("render_buttons end");
    },

    my_setup_columns: function (fields, grouped) {
    	console.log("my_setup_columns");
        var $dropdown_menu = $("#dynamic_dropdown_menu");
        $dropdown_menu.toggle();
        if (!$dropdown_menu.is(":visible")) {
            return
        }
        $("#showcb > li.dynamic_column_checkbox").remove();
        $('#save_for_all_users').prop('checked', false);
        $('#save_column_order').prop('checked', false);
        var $showcb = $('#showcb');

        this.visible_columns = _.filter(this.ordered_columns, function (column) {
            var $firstcheck = $showcb.find("input[data-id='" + column.id + "']");
            if($firstcheck.length == 0)
            {
                var $li= $("<li></li>").addClass("dynamic_column_checkbox");
                if (column.string) {
                    var $description = $("<span> " + column.string + " </span>");
                    var $checkbox = $("<input type='checkbox' name='cb' class='column_checkbox' data-id='" + column.id + "'/>");

                    if(column.invisible !== '1')
                    {
                        $checkbox.prop("checked", true);
                    }
                    $li.append($checkbox);
                    $li.append($description);
                    $showcb.append($li);
                }
            }
            else
            {
                if(column.invisible !== '1')
                {
                    $firstcheck.prop("checked", true);
                }
                else
                {
                    $firstcheck.prop("checked", false);
                }
            }
            console.log("my_setup_columns end");
        });
        $('#select_all_columns, #unselect_all_columns').on('click',function (event) {
            if (event.target.id == 'select_all_columns') {
                $('.column_checkbox').prop("checked", true);
            } else if (event.target.id == 'unselect_all_columns') {
                $('.column_checkbox').prop("checked", false);
            }
            $(this).blur();
            event.stopPropagation();
        });
    },
    stop_event : function(e)
      {
          e.stopPropagation();
      },

    hide_show_columns : function(event)
    {
    	console.log("hide_show_columns");
        var self = this;
        self.scroll_left = $('.table-responsive').scrollLeft();
        self.ViewManager.views.list.columnsSortOrder = {}
        self.ViewManager.views.list.columnsSortOrderGrouped = {}

        var $save_for_all_users = $('#save_for_all_users');
        var $save_column_order = $('#save_column_order');

        var ordered_columns = []
        if ($save_column_order.is(":checked")) {
            $('.o_list_view th:not(:first)').each(function (index, column) {
                if ($(column).data("id")){
                    ordered_columns.push($(column).data("id"));
                }
            });
        }
        $("#dynamic_column_dropdown").removeClass('open');
        $("#dynamic_dropdown_menu").hide();
        this.setup_columns(this.fields_view.fields, this.grouped);
        this.$el.html(QWeb.render(this._template, this));

        var Model = window.openerp.web.Model;
        var DynamicColumnModel = new Model('dynamic.column.listview');
        var visible_columns = [];
        $('#showcb input:checked').each(function() {
            visible_columns.push($(this).data('id'));
        });

        var view_id = self.view_id || self.fields_view.view_id;
        DynamicColumnModel.call('save_visible_columns', [view_id, this.model, visible_columns, $save_for_all_users.is(":checked"), $save_column_order.is(":checked"), ordered_columns]).then(function (result) {
            return self.reload_content();
        })
        console.log("hide_show_columns end");
    },

    setup_columns: function (fields, grouped) {
    	console.log("setup_columns");
        var colums_setted = $.Deferred();
        var self = this
        self._super(fields, grouped);
        var dynamic_visible_columns;
        var Model = window.openerp.web.Model;
        var DynamicColumnModel = new Model('dynamic.column.listview');
        var view_id = self.view_id || self.fields_view.view_id;
        this.ordered_columns = _.sortBy(this.columns, function (field) {return field.string});
        DynamicColumnModel.call('get_visible_columns', [view_id]).then(function (result) {
            var dynamic_visible_columns = result[0];
            var is_ordered = result[1];
            self.visible_columns = _.filter(self.ordered_columns, function (column) {
                var cbid = document.getElementById(column.id);
                if (dynamic_visible_columns.length > 0) {
                    if (_.contains(dynamic_visible_columns, column.id)) {
                        column.invisible = '2';
                    } else {
                        column.invisible = '1';
                    }

                }
                else {
                    var cbid = document.getElementById(column.id);
                    if(cbid !== null)
                    {
                      var cbid = cbid.checked;
                      if(cbid !== false)
                        {
                            column.invisible = '2';
                        }
                        else
                        {
                            column.invisible = '1';
                        }
                    }
                }
                return column.invisible !== '1';
            });
            if (is_ordered && dynamic_visible_columns) {
                var index;
                var children_length = self.fields_view.arch.children.length;
                self.fields_view.arch.children = _.sortBy(self.fields_view.arch.children, function (child) {
                    index = dynamic_visible_columns.indexOf(child.attrs.name);
                    if (index == -1) { index = children_length}
                        return index;
                });
            }

            var columns_length = self.visible_columns.length;
            var ordered_visible_columns = _.pluck(self.columns, 'id');
            self.visible_columns = _.sortBy(self.visible_columns, function (visible_column) {
                index = ordered_visible_columns.indexOf(visible_column.id);
                if (index == -1) { index = columns_length}
                    return index;
            });

            self.aggregate_columns = _(self.visible_columns).invoke('to_aggregate');

            // Fixes problem displaying footer with aggregates when group_by filter is active and columns were set dynamically
            if (grouped && dynamic_visible_columns.length > 0) {self.aggregate_columns.unshift({})};
            colums_setted.resolve();
        });
        return colums_setted.promise(self);
        console.log("setup_columns end");
    },

});

ListView.Groups.include({
    render_groups: function (datagroups) {
    	console.log("render_groups");
        self = this;
        var columnsSortOrder = self.view.ViewManager.views.list.columnsSortOrder;
        if (!self.original_columns) {
            self.original_columns = self.columns;
        }

        var index;
        if (!$.isEmptyObject(columnsSortOrder)) {
            self.columns = _.sortBy(self.columns, function (column) {
                index = columnsSortOrder[column.id];
                if (!index) {
                    index = 1000
                }
                return index;
            });
        } else if (self.original_columns) {
            self.columns = self.original_columns;
        }
        var result = this._super(datagroups);
        return result;
        console.log("render_groups end");
    }
});


$(document).click(function(event){
  if (event.which != 3) { //If it's not a right click
    $("#dynamic_dropdown_menu").hide();
  }
});


});
