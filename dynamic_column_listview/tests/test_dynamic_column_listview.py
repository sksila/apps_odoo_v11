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


class TestDynamicColumnListView(TransactionCase):

    def setUp(self):
        super(TestDynamicColumnListView, self).setUp()
        self.dynamic_column_obj = self.env['dynamic.column.listview']
        self.res_user_obj = self.env['res.users']
        self.group_public_id = self.ref('base.group_public')

    def test_save_visible_columns(self):
        view_id = self.env.ref('base.view_users_tree').id
        model = "res.users"
        visible_columns = ["name", "login"]
        visible_columns.sort()
        self.dynamic_column_obj.search([]).unlink()
        public_user = self.res_user_obj.search([
            ('login', '=', 'public'),
            ('active', '=', False)
        ])

        # Admin saves as visible columns 'name' and 'login' for res.users
        # Tree View. The change is applied for all users
        self.dynamic_column_obj.save_visible_columns(
            view_id=view_id, model=model, visible_columns=visible_columns,
            apply_for_all=True)

        # Checks visible columns for Admin user for res.users Tree View
        admin_visible_columns, is_ordered = \
            self.dynamic_column_obj.get_visible_columns(view_id)
        admin_visible_columns.sort()

        self.assertEqual(visible_columns, admin_visible_columns,
                         "Columns mismatch after saving visible columns for "
                         "all users")

        # Check that Public User gets the columns established previously by
        # Admin user for All users
        test_visible_columns, is_ordered = self.dynamic_column_obj.sudo(
            public_user).get_visible_columns(view_id)
        test_visible_columns.sort()

        self.assertEqual(visible_columns, test_visible_columns,
                         "New user doesn't get visible columns previously "
                         "saved for all users")

        # Public User saves as visible columns 'login' and 'login_date' for
        # res.users Tree View. The change is applied for Public User only
        new_visible_columns = ["login", "login_date"]
        new_visible_columns.sort()

        save_id = self.dynamic_column_obj.sudo(
            public_user).save_visible_columns(
            view_id=view_id, model=model, visible_columns=new_visible_columns,
            apply_for_all=False)

        # Check that Public User gets the columns established previously by
        # himself
        test_visible_columns = self.dynamic_column_obj.sudo(
            public_user).browse(save_id).get_columns()
        test_visible_columns.sort()

        self.assertEqual(new_visible_columns, test_visible_columns,
                         "Column mismatch after saving visible columns for "
                         "own user")

        # Checks visible columns for Admin user for res.users Tree View
        # (Must be the same that were established as visible in the beginning)
        admin_visible_columns, is_ordered = \
            self.dynamic_column_obj.get_visible_columns(view_id)
        admin_visible_columns.sort()

        self.assertEqual(visible_columns, admin_visible_columns,
                         "Global visible columns were overriden by changes "
                         "saved for only one user")

    def test_save_visible_columns_with_order(self):
        view_id = self.env.ref('base.view_users_tree').id
        model = "res.users"
        visible_columns = ["id", "name", "login", "company_id"]
        alphabetically_ordered_columns = sorted(visible_columns)

        self.dynamic_column_obj.search([]).unlink()

        # Admin saves as visible columns 'name' and 'login' for res.users
        # Tree View. The change is saved with order
        self.dynamic_column_obj.save_visible_columns(
            view_id=view_id, model=model, visible_columns=visible_columns,
            save_column_order=True,
            ordered_columns=alphabetically_ordered_columns)

        # Checks visible columns for Admin user for res.users Tree View
        result_visible_columns, is_ordered = \
            self.dynamic_column_obj.get_visible_columns(view_id)

        self.assertTrue(is_ordered, "Column order was not saved")
        self.assertEqual(alphabetically_ordered_columns,
                         result_visible_columns, "Column order was not saved")
