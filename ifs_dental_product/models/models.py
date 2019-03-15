# -*- coding: utf-8 -*-
import random
import logging
from datetime import datetime, timedelta
from odoo import _, tools
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class Patient(models.Model):
    _name = 'ifs_dental_product.patient'
    _inherit = 'mail.thread'
    _description = 'Patient'
    

    name = fields.Char('Name')
    date_of_birth = fields.Date('Date of Birth')
    
class Trattamento(models.Model):
    _name = 'ifs_dental_product.treatment'
    _inherit = ['mail.thread','portal.mixin']
    _description = 'Treatment'
    
    patient_id = fields.Many2one('ifs_dental_product.patient','Patient')
    stage_id = fields.Many2one('ifs_dental_product.stage', string='Stage', ondelete='restrict', track_visibility='onchange',
                                copy=False,
                               index=True)
    stl_model = fields.Many2one('ir.attachment','3d Model')
    image1 = fields.Binary('Image1')
    image2 = fields.Binary('Image1')
    image3 = fields.Binary('Image1')
    image4 = fields.Binary('Image1')
    name = fields.Char('Name')
    description = fields.Text('Description')
    ref= fields.Char('Ref')
    
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
    