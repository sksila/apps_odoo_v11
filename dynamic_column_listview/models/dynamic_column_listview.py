# -*- coding: utf-8 -*-
# ############################################################################
#
#    Copyright Eezee-It (C) 2017
#    Author: Eezee-It <info@eezee-it.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models


class DynamicColumnListviewIrModelFieldsRel(models.Model):
    _name = 'dynamic.column.fields.rel'

    dynamic_column_listview_id = fields.Many2one(
        'dynamic.column.listview', ondelete='cascade')
    field_id = fields.Many2one('ir.model.fields', ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=100)


class DynamicColumnListview(models.Model):
    _name = 'dynamic.column.listview'

    user_id = fields.Many2one('res.users', string="User")
    view_id = fields.Many2one('ir.ui.view', string="View")
    visible_field_ids = fields.Many2many(
        "ir.model.fields",
        "dynamic_column_fields_rel",
        "dynamic_column_listview_id",
        "field_id",
        string="Visible fields")

    @api.multi
    def is_ordered(self):
        """
        Returns True if any of the visible fields has a display order
        """
        column_fields_rel_obj = self.env['dynamic.column.fields.rel']
        column_fields_rel = column_fields_rel_obj.search([
            ('dynamic_column_listview_id', '=', self.id),
            ('sequence', '=', True),
        ])

        return bool(column_fields_rel)

    @api.model
    def get_columns(self):
        column_fields_rel_obj = self.env['dynamic.column.fields.rel']
        column_fields_rel = column_fields_rel_obj.search([
            ('dynamic_column_listview_id', '=', self.id)
        ], order='sequence asc')

        columns = []
        for record in column_fields_rel:
            columns.append(record.field_id.name)
        return columns

    @api.model
    def get_visible_columns(self, view_id):
        dynamic_listview = self.search([
            ('view_id', '=', view_id),
            ('user_id', 'in', [self.env.user.id, False]),
        ], order="write_date desc", limit=1)

        columns = dynamic_listview.get_columns()
        is_ordered = dynamic_listview.is_ordered()
        return columns, is_ordered

    @api.multi
    def save_visible_column_order(self, ordered_columns):
        column_fields_rel = self.env['dynamic.column.fields.rel']
        column_fields = column_fields_rel.search([
            ('dynamic_column_listview_id', '=', self.id),
        ])
        low_priority = len(column_fields)
        for record in column_fields:
            field_name = record.field_id.name
            sequence = field_name in ordered_columns and (
                (ordered_columns.index(field_name) + 1)) or low_priority
            record.write({'sequence': sequence})

    @api.multi
    def delete_not_visible_columns(self, visible_columns):
        column_fields_rel = self.env['dynamic.column.fields.rel']
        not_visible_fields = column_fields_rel.search([
            ('dynamic_column_listview_id', '=', self.id),
            ('field_id.name', 'not in', visible_columns)
        ])
        not_visible_fields.unlink()

    @api.model
    def save_visible_columns(self, view_id, model, visible_columns,
                             apply_for_all=False, save_column_order=False,
                             ordered_columns=[]):

        if view_id:
            user_id = self.env.user.id
            if apply_for_all:
                user_id = False

            field_ids = self.env['ir.model.fields'].search([
                ('model', '=', model),
                ('name', 'in', visible_columns),
            ])

            visible_field_ids = field_ids and [(4, field_ids.ids)] or [(5,)]
            values = {
                'user_id': user_id,
                'view_id': view_id,
                'visible_field_ids': visible_field_ids,
            }

            dynamic_listview = self.search([
                ('view_id', '=', view_id),
                ('user_id', '=', user_id)
            ])

            result = dynamic_listview and dynamic_listview.write(
                values) or self.create(values).id

            dynamic_listview = dynamic_listview or self.browse(result)
            dynamic_listview.delete_not_visible_columns(visible_columns)
            if save_column_order:
                dynamic_listview.save_visible_column_order(ordered_columns)

            return result
