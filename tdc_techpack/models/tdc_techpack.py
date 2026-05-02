# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TdcTechpack(models.Model):
    _name = 'tdc.techpack'
    _description = 'Fashion Tech Pack'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    # ── Identity ──────────────────────────────────────────────────────────────
    name = fields.Char(
        string='Reference', required=True, copy=False,
        readonly=True, default=lambda self: _('New')
    )
    brand = fields.Char(string='Brand', required=True, tracking=True)
    style_no = fields.Char(string='Style No.', required=True, tracking=True)
    description = fields.Char(string='Description')
    season = fields.Char(string='Season')
    date = fields.Date(string='Date', default=fields.Date.today)

    state = fields.Selection([
        ('draft',    'Draft'),
        ('confirm',  'Confirmed'),
        ('approved', 'Approved'),
        ('cancel',   'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    # ── Product & Fabric ──────────────────────────────────────────────────────
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain=[('type', 'in', ['product', 'consu'])],
    )
    fabric = fields.Char(string='Fabric / Material', required=True)
    fabric_weight = fields.Char(string='Fabric Weight (GSM)')
    fabric_composition = fields.Char(string='Fabric Composition')
    color = fields.Char(string='Colour')
    size_range = fields.Char(string='Size Range', default='XS/S/M/L/XL')

    # ── Construction Details ──────────────────────────────────────────────────
    fit_type = fields.Selection([
        ('slim',    'Slim Fit'),
        ('regular', 'Regular Fit'),
        ('loose',   'Loose Fit'),
        ('oversized','Oversized'),
    ], string='Fit Type', default='slim')

    collar_detail   = fields.Char(string='Collar Detail')
    pocket_detail   = fields.Char(string='Pocket Detail')
    closure_type    = fields.Selection([
        ('zipper',   'Metal Zipper'),
        ('button',   'Button'),
        ('snap',     'Snap Fastener'),
        ('hook',     'Hook & Eye'),
        ('velcro',   'Velcro'),
        ('none',     'None'),
    ], string='Closure Type', default='zipper')
    closure_detail  = fields.Char(string='Closure Detail')
    hem_detail      = fields.Char(string='Hem Detail')
    elastic_detail  = fields.Char(string='Elastic / Cuff Detail')

    # ── Stitching ─────────────────────────────────────────────────────────────
    stitch_type = fields.Selection([
        ('single_needle_overlock', 'Single Needle + Overlock'),
        ('double_needle',          'Double Needle'),
        ('flatlock',               'Flatlock'),
        ('chain',                  'Chain Stitch'),
        ('blind',                  'Blind Stitch'),
    ], string='Stitch Type', default='single_needle_overlock')
    stitch_spi       = fields.Integer(string='SPI (Stitches per Inch)', default=12)
    top_stitching    = fields.Boolean(string='Top Stitching', default=True)
    top_stitch_color = fields.Char(string='Top Stitch Colour')
    seam_allowance   = fields.Char(string='Seam Allowance (cm)', default='1.0')
    stitching_notes  = fields.Text(string='Stitching Notes')

    # ── Hardware / Trims BOM ──────────────────────────────────────────────────
    bom_line_ids = fields.One2many(
        'tdc.techpack.bom.line', 'techpack_id', string='Bill of Materials'
    )

    # ── Images ────────────────────────────────────────────────────────────────
    image_front     = fields.Binary(string='Front View', attachment=True)
    image_back      = fields.Binary(string='Back View', attachment=True)
    image_detail_1  = fields.Binary(string='Detail Image 1', attachment=True)
    image_detail_2  = fields.Binary(string='Detail Image 2', attachment=True)
    construction_notes = fields.Html(string='Construction Notes')

    # ── Label Info ────────────────────────────────────────────────────────────
    label_position  = fields.Char(string='Label Position')
    label_content   = fields.Text(string='Label Content / Instructions')
    care_instructions = fields.Text(string='Care Instructions')

    # ── Costing & Pricing ─────────────────────────────────────────────────────
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    fabric_cost     = fields.Monetary(string='Fabric Cost', currency_field='currency_id')
    trim_cost       = fields.Monetary(string='Trim / Hardware Cost', currency_field='currency_id')
    labor_cost      = fields.Monetary(string='Labour Cost', currency_field='currency_id')
    overhead_cost   = fields.Monetary(string='Overhead Cost', currency_field='currency_id')
    total_cost      = fields.Monetary(
        string='Total Cost', compute='_compute_total_cost',
        store=True, currency_field='currency_id'
    )
    target_price    = fields.Monetary(string='Target Retail Price', currency_field='currency_id')
    margin_pct      = fields.Float(
        string='Margin (%)', compute='_compute_margin', store=True, digits=(5, 2)
    )

    # ── Traceability ──────────────────────────────────────────────────────────
    sale_order_ids = fields.Many2many(
        'sale.order', 'tdc_techpack_sale_rel',
        'techpack_id', 'sale_id',
        string='Sale Orders'
    )
    production_ids = fields.Many2many(
        'mrp.production', 'tdc_techpack_mrp_rel',
        'techpack_id', 'production_id',
        string='Manufacturing Orders'
    )
    sale_count       = fields.Integer(compute='_compute_counts')
    production_count = fields.Integer(compute='_compute_counts')

    # ── Approvals ─────────────────────────────────────────────────────────────
    confirmed_by  = fields.Many2one('res.users', string='Confirmed By', readonly=True)
    approved_by   = fields.Many2one('res.users', string='Approved By', readonly=True)
    approved_date = fields.Date(string='Approved Date', readonly=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Computes
    # ─────────────────────────────────────────────────────────────────────────
    @api.depends('fabric_cost', 'trim_cost', 'labor_cost', 'overhead_cost')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = (
                (rec.fabric_cost or 0)
                + (rec.trim_cost or 0)
                + (rec.labor_cost or 0)
                + (rec.overhead_cost or 0)
            )

    @api.depends('total_cost', 'target_price')
    def _compute_margin(self):
        for rec in self:
            if rec.target_price:
                rec.margin_pct = ((rec.target_price - rec.total_cost) / rec.target_price) * 100
            else:
                rec.margin_pct = 0.0

    @api.depends('sale_order_ids', 'production_ids')
    def _compute_counts(self):
        for rec in self:
            rec.sale_count = len(rec.sale_order_ids)
            rec.production_count = len(rec.production_ids)

    # ─────────────────────────────────────────────────────────────────────────
    # Sequence
    # ─────────────────────────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('tdc.techpack') or _('New')
        return super().create(vals_list)

    # ─────────────────────────────────────────────────────────────────────────
    # State transitions
    # ─────────────────────────────────────────────────────────────────────────
    def action_confirm(self):
        for rec in self:
            if not rec.bom_line_ids:
                raise ValidationError(_('Please add at least one BOM line before confirming.'))
            rec.write({'state': 'confirm', 'confirmed_by': self.env.uid})

    def action_approve(self):
        for rec in self:
            rec.write({
                'state': 'approved',
                'approved_by': self.env.uid,
                'approved_date': fields.Date.today(),
            })

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    # ─────────────────────────────────────────────────────────────────────────
    # Smart button actions
    # ─────────────────────────────────────────────────────────────────────────
    def action_view_sale_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sale Orders'),
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.sale_order_ids.ids)],
        }

    def action_view_productions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Manufacturing Orders'),
            'res_model': 'mrp.production',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.production_ids.ids)],
        }

    def action_print_techpack(self):
        return self.env.ref('tdc_techpack.action_report_techpack').report_action(self)


