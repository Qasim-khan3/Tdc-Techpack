# -*- coding: utf-8 -*-
{
    'name': 'TDC Techpack - Fashion Specification Sheet',
    'version': '18.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Professional Tech Pack for Fashion Brands – Linked to Sale & MRP',
    'description': """
        Full Tech Pack module for Odoo 18.
        - Construction details with multi-line BOM
        - Hardware, trims, stitching notes
        - Front/back view image uploads
        - Linked to Sale Order and Manufacturing Order
        - Costing & pricing section
        - Professional PDF report (QWeb)
    """,
    'author': 'Techno Digi Codes',
    'images': ['static/description/banner.png'],
    'depends': ['sale_management', 'mrp', 'stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/tdc_techpack_views.xml',
        'views/tdc_techpack_bom_line_views.xml',
        'views/tdc_techpack_menu.xml',
        'views/sale_order_views.xml',
        'views/mrp_production_views.xml',
        'report/techpack_report.xml',
        'report/techpack_report_template.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
