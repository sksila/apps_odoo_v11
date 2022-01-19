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
{
    'name': 'Dynamic Column Listview',
    'version': '1.1',
    'author': 'Eezee-It',
    'category': 'Dynamic Column Listview',
    'website': 'http://www.eezee-it.com',
    'summary': 'Dynamic Column Listview',
    'description': """

Dynamic Column Listview
============
Dynamic Column Listview module is made to show/hide the column(s) on the
list/tree view of ODOO. After installing the module a "Select Columns" button
will be show to the list view before the pagination.

    """,
    'images': [
    ],
    'depends': ['web'],
    'data': [
        'security/ir.model.access.csv',
        'views/listview_button.xml',
    ],
    'demo': [],
    'test': [
    ],
    'qweb': ['static/src/xml/listview_button_view.xml'],
}
