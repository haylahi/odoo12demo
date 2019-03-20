# -*- coding: utf-8 -*-
import random
import logging
from datetime import datetime, timedelta
from odoo import _, tools
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)
TREATMENT_PRIORITY = [
    ('0', 'All'),
    ('1', 'Low priority'),
    ('2', 'High priority'),
    ('3', 'Urgent'),
]

class DentalTag(models.Model):
    _name = 'ifs_dental_product.tag'
    _description = ' Tags'
    _order = 'name'

    name = fields.Char(required=True)
    color = fields.Integer('Color')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]

class Patient(models.Model):
    _name = 'ifs_dental_product.patient'
    _inherit = 'mail.thread'
    _description = 'Patient'
    

    name = fields.Char('Name')
    date_of_birth = fields.Date('Date of Birth')
    image = fields.Binary('Image')

    
    @api.model
    def website_writable(self):
        model = self.env['ir.model'].sudo().search([('model', '=', 'ifs_dental_product.patient')])
        model.website_form_access = True
        self.env['ir.model.fields'].sudo().formbuilder_whitelist('ifs_dental_product.patient',['name','date_of_birth','image'])
        
        
class Trattamento(models.Model):
    _name = 'ifs_dental_product.treatment'
    _inherit = ['mail.thread','portal.mixin','mail.activity.mixin']
    _description = 'Treatment'
    
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        # write the domain
        # - ('id', 'in', stages.ids): add columns that should be present
        # - OR ('team_ids', '=', team_id) if team_id: add team columns
        search_domain = [(True, '=', True)]
        
        return stages.search(search_domain, order=order)
    
    def _default_stage_id(self):
        stage_id = self.env['ifs_dental_product.stage'].search([(True,'=',True)], limit=1)
        if bool(stage_id): return stage_id.id
        return False
    
    patient_id = fields.Many2one('ifs_dental_product.patient','Paziente')
    stage_id = fields.Many2one('ifs_dental_product.stage', string='Stage', ondelete='restrict', track_visibility='onchange',
                                copy=False,default=_default_stage_id,group_expand='_read_group_stage_ids',
                               index=True)
    stl_model = fields.Many2one('ir.attachment','3d Model')
    partner_id = fields.Many2one('res.partner','Dentista')
    order_id = fields.Many2one('sale.order','Ordine')
    user_id = fields.Many2one('res.users','Utente')
    image1 = fields.Binary('Image1')
    image2 = fields.Binary('Image1')
    image3 = fields.Binary('Image1')
    image4 = fields.Binary('Image1')
    name = fields.Char('Nome',related="patient_id.name",readonly=True)
    description = fields.Text('Description')
    ref= fields.Char('Ref')
    product_id = fields.Many2one('product.product','Prodotto')
    color = fields.Integer(string='Color Index')
    priority = fields.Selection(TREATMENT_PRIORITY, string='Priority', default='0')
    tag_ids = fields.Many2many('ifs_dental_product.tag', string='Tags')
    deadline = fields.Datetime(string='Deadline')

    @api.multi
    def name_get(self):
        result = []
        for treatment in self:
            result.append((treatment.id, "%s %s (#%d)" % (treatment.name,treatment.product_id.name, treatment.id)))
        return result
    
    @api.model
    def website_writable(self):
        model = self.env['ir.model'].sudo().search([('model', '=', 'ifs_dental_product.treatment')])
        model.website_form_access = True
        self.env['ir.model.fields'].sudo().formbuilder_whitelist('ifs_dental_product.treatment',['patient_id','description','product_id','partner_id','image1','image2','image3','image4'])
        
    @api.multi
    def assign_ticket_to_self(self):
        self.ensure_one()
        self.user_id = self.env.user
        
    @api.multi
    def create_order(self):
        self.ensure_one()
        so = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'partner_invoice_id': self.partner_id.id,
            'partner_shipping_id': self.partner_id.id,
            'order_line': [(0, 0, {'name':self.product_id.name, 'product_id': self.product_id.id, 'product_uom_qty': 1, 'product_uom': self.product_id.uom_id.id, 'price_unit': self.product_id.list_price})],
            
        })
        self.order_id = so.id
        return self.action_view_sales()
    @api.multi
    def action_view_sales(self):
        self.ensure_one()
        action = self.env.ref('sale.action_orders')
        

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'res_model': action.res_model
        }       
class Stage(models.Model):
    _name = 'ifs_dental_product.stage'
    _description = 'Treatment Stage'
    _order = 'sequence, id'

    

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)
    is_close = fields.Boolean(
        'Closing Kanban Stage',
        )
    fold = fields.Boolean(
        'Folded', help='Folded in kanban view')
    