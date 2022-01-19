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
from odoo.tests.common import TransactionCase
from lxml import etree


class TestIrUiViewView(TransactionCase):

    def setUp(self):
        super(TestIrUiViewView, self).setUp()
        self.ir_ui_view_obj = self.env['ir.ui.view']
        self.model_name = 'res.partner'
        self.model_obj = self.env[self.model_name]
        self.view_id = self.env.ref('base.view_partner_tree')

    def test_postprocess_and_fields(self):
        original_arch = self.view_id.read_combined(fields=['arch'])['arch']

        node = etree.fromstring(original_arch)
        original_node = etree.fromstring(original_arch)
        public_user = self.env['res.users'].search([
            ('login', '=', 'public'),
            ('active', '=', False)
        ])

        context = {'params': {'view_type': 'tree', 'action': 1}}
        ir_ui_view_obj = self.ir_ui_view_obj.sudo(public_user).with_context(
            context)
        result = ir_ui_view_obj.postprocess_and_fields(self.model_name, node,
                                                       self.view_id.id)
        result_node = etree.fromstring(result[0])

        original_fields = [child.attrib.get('name') for child in original_node
                           if child.tag == 'field']

        result_fields = [child.attrib.get('name') for child in result_node
                         if child.tag == 'field']

        difference = set(result_fields) - set(original_fields)
        self.assertTrue(difference, "All Model fields were not loaded")
