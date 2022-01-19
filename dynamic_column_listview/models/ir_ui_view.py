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
from lxml import etree
from odoo import api, models
from odoo.exceptions import AccessError
import logging
logger = logging.getLogger(__name__)

# For including fields that causes performance issues when loading a tree view
BLACKLISTED_FIELDS = {
    # model     : [fields]
    'stock.move': ['availability']
}


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    def has_access(self, model_fields, field):

        if field in model_fields and model_fields.get(field).get('relation'):
            model_obj = self.env[model_fields.get(field).get('relation')]

            return model_obj.check_access_rights('read', raise_exception=False)
        return True

    def get_forbidden_fields(self, model_obj):
        """
        Return the computed fields of the given model for which the user
        doesn't have read access
        """
        computed_fields = set(
            [name for name, field in model_obj._fields.iteritems()
             if field.compute]
        )
        record = model_obj.search([], limit=1)
        forbidden_fields = set()
        for name in computed_fields:
            try:
                record.env.invalidate_all()
                getattr(record, name)
            except AccessError:  # pragma: no cover
                forbidden_fields.add(name)
            except Exception as e:  # pragma: no cover
                logger.warning(
                    "Unexpected error while reading '%s' field from '%s' model"
                    ". %s" % (name, model_obj._name, e))

        return forbidden_fields

    @api.model
    def postprocess_and_fields(self, model, node, view_id):
        """
        Override Odoo's original method so when a Tree view is being loaded,
        every available field for the tree view's model is included in it's
        architecture, making them available for dynamic display

        Fields are only included for tree achitectures that are not part of a
        Wizard and are not embedded in a Form view.
        """
        model_obj = self.env[model]

        if node.tag == 'tree' and not model_obj.is_transient():
            context = self.env.context
            form_view_ref = context.get('form_view_ref')
            view = self.env['ir.ui.view'].browse(view_id)
            view_type = view.type
            action = context.get('params', {}).get('action')
            is_embedded_view = (form_view_ref or view_type == 'form')

            if not is_embedded_view and action:
                model_fields = model_obj.fields_get()
                all_fields = set(model_fields.keys())

                # Fields that were not defined in the model but were included
                #  in the view (like 'in_group_<id>' or 'sel_groups_<id1>' for
                # res.users)
                fake_fields = set([
                    key for key, values in model_fields.iteritems()
                    if 'selectable' in values and
                    not values.get('selectable')])
                tree_view_fields = set([
                    child.attrib.get('name') for child in node
                    if child.tag == 'field'])
                forbidden_fields = self.get_forbidden_fields(model_obj)

                blacklisted_fields = set(BLACKLISTED_FIELDS.get(model) or [])
                missing_fields = list(all_fields - tree_view_fields -
                                      forbidden_fields - fake_fields -
                                      blacklisted_fields)

                for field in missing_fields:
                    if self.has_access(model_fields, field):
                        node.append(etree.Element('field', {
                            'name': field, 'invisible': '1'
                            }
                        ))
        return super(IrUiView, self).postprocess_and_fields(model, node,
                                                            view_id)
