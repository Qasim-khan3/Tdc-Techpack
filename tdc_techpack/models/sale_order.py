
# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Saleorder(models.Model):
    
    _inherit = 'sale.order'
    _description = 'Fashion Tech Pack'
    color = fields.Char(string='Colour')
    