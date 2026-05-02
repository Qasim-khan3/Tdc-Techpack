# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TdcTechpackBomLine(models.Model):
    _name = 'tdc.techpack.bom.line'
    _description = 'Tech Pack BOM Line'
    _order = 'sequence, id'

    techpack_id = fields.Many2one(
        'tdc.techpack', string='Tech Pack',
        required=True, ondelete='cascade', index=True
    )
    sequence = fields.Integer(string='Sequence', default=10)

    # ── Item Identity ─────────────────────────────────────────────────────────
    product_id = fields.Many2one(
        'product.product', string='Product / Component'
    )
    name = fields.Char(
        string='Description', required=True,
        compute='_compute_name', store=True, readonly=False
    )
    item_type = fields.Selection([
        ('fabric',    'Fabric'),
        ('lining',    'Lining'),
        ('interlining','Interlining'),
        ('zipper',    'Zipper'),
        ('button',    'Button'),
        ('snap',      'Snap Fastener'),
        ('label',     'Label'),
        ('thread',    'Thread'),
        ('elastic',   'Elastic'),
        ('trim',      'Trim / Hardware'),
        ('packaging', 'Packaging'),
        ('other',     'Other'),
    ], string='Item Type', required=True, default='trim')

    # ── Specs ─────────────────────────────────────────────────────────────────
    color           = fields.Char(string='Colour / Finish')
    size_spec       = fields.Char(string='Size / Spec')
    logo_engraving  = fields.Char(string='Logo / Engraving')
    placement       = fields.Char(string='Placement')

    # ── Quantity & Cost ───────────────────────────────────────────────────────
    qty = fields.Float(string='Qty per Unit', default=1.0, digits=(12, 3))
    uom_id = fields.Many2one(
        'uom.uom', string='UoM',
        default=lambda self: self.env.ref('uom.product_uom_unit', raise_if_not_found=False)
    )
    unit_cost = fields.Float(string='Unit Cost', digits=(12, 4))
    subtotal  = fields.Float(
        string='Subtotal', compute='_compute_subtotal', store=True
    )
    currency_id = fields.Many2one(
        related='techpack_id.currency_id', string='Currency'
    )

    # ── Notes ─────────────────────────────────────────────────────────────────
    note = fields.Char(string='Notes / Remarks')

    # ─────────────────────────────────────────────────────────────────────────
    @api.depends('product_id')
    def _compute_name(self):
        for line in self:
            if line.product_id and not line.name:
                line.name = line.product_id.display_name

    @api.depends('qty', 'unit_cost')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.unit_cost

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.display_name
            self.uom_id = self.product_id.uom_id
            self.unit_cost = self.product_id.standard_price
