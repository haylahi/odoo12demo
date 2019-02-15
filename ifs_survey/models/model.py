# -*- coding: utf-8 -*-
import random
import logging
from datetime import datetime, timedelta
from odoo import _, tools
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class Survey(models.Model):
    _inherit = 'survey.survey'
    
    is_page_skippable = fields.Boolean('Are pages skippable')
    parent_id = fields.Many2one('survey.survey','Parent Survey')
    direct_access = fields.Boolean('Without password')
    model_id = fields.Many2one('ir.model')
    write_on_done = fields.Boolean('Write on Done',default=False)
    
    @api.model
    def next_page(self, user_input, page_id, go_back=False):
        """ The next page to display to the user, knowing that page_id is the id
            of the last displayed page.

            If page_id == 0, it will always return the first page of the survey.

            If all the pages have been displayed and go_back == False, it will
            return None

            If go_back == True, it will return the *previous* page instead of the
            next page.

            .. note::
                It is assumed here that a careful user will not try to set go_back
                to True if she knows that the page to display is the first one!
                (doing this will probably cause a giant worm to eat her house)
        """
        
        next_page_id = False
        survey = user_input.survey_id
        if not survey.is_page_skippable:
            return super(Survey,self).next_page( user_input, page_id, go_back)
        pages = list(enumerate(survey.page_ids))
        
        # First page
        if page_id == 0:
            
            user_input.register_page(False,pages[0][1])
            return (pages[0][1], 0, len(pages) == 1)
        else:
            page_id = self.env['survey.page'].browse(page_id)
        next_page_id = False
        survey = user_input.survey_id
        if go_back:
            next_page_id = user_input.previous_page(page_id)
            next_page_index = pages.index((filter(lambda p: p[1].id == next_page_id.id, pages))[0])
            
            return (next_page_id, next_page_index, False)    
        else:
            codes = ""
            next_page_id = False
            for line in user_input.user_input_line_ids.filtered(lambda user_input_line: user_input_line.page_id.id == page_id.id):
                if bool(line.value_suggested):
                    if len(codes) > 0 :
                        codes+= ","
                    if line.value_suggested.code:
                        codes += line.value_suggested.code
                if bool(line.value_suggested.next_page_id) :
                    next_page_id = line.value_suggested.next_page_id
            if not bool(next_page_id):
                rule_id = self.env['ifs_survey.survey_page_rule'].sudo().search([('page_id','=',page_id.id)],limit=1)
                if bool(rule_id):
                    next_page_id = rule_id.next_page_id
                    
        if bool(next_page_id):
            next_page_index = pages.index((filter(lambda p: p[1].id == next_page_id.id, pages))[0])
            user_input.register_page(page_id,next_page_id)
            return (next_page_id, next_page_index, False)    
        elif bool(page_id.next_page_id):
            next_page_id = page_id.next_page_id
            next_page_index = pages.index((filter(lambda p: p[1].id == next_page_id.id, pages))[0])
            user_input.register_page(page_id,next_page_id)
            return (next_page_id, next_page_index, False)    
        else:
            next_page_id,next_page_index,last =  super(Survey,self).next_page( user_input, page_id.id, go_back)
            user_input.register_page(page_id,next_page_id)
            return ( next_page_id,next_page_index ,last)

class SurveyQuestion(models.Model):
    _inherit = 'survey.question'       
    
    model_id = fields.Many2one('ir.model',related="survey_id.model_id",store=True)
    field_id = fields.Many2one('ir.model.fields', string="Field",domain="[('model_id','=',model_id)]")
    survey_id = fields.Many2one('survey.survey', related='page_id.survey_id', string='Survey',store=True)
    field_domain = fields.Char(string='Domain', default=[])
    relation = fields.Char(related="field_id.relation")
    
    @api.multi
    @api.constrains('field_id','type','field_domain')
    def _update_labels(self):
        for question in self:
            
            if question.type in ['simple_choice','multiple_choice']: 
                if bool(question.field_id) and question.field_id.ttype in ['many2one','many2many','one2many']:
                        
                    answer_options = self.sudo().env[question.field_id.relation].search(eval(question.field_domain))
                    label_ids = self.env['survey.label'].search([
                        ('question_id','=',question.id),
                        ('model_field_res_id','in', answer_options.ids),
                        ('model_res_name', '=', question.field_id.relation)
                    ])
                    
                    model_field_res_ids = [label_id.model_field_res_id for label_id in label_ids]
                    
                    for option in answer_options:
                        if option.id not in model_field_res_ids:
                            self.env['survey.label'].create({
                                "value" : option.name,
                                "model_res_name" : question.field_id.relation,
                                "model_field_res_id" : option.id,
                                "question_id" : question.id
                            })
                        
                    self.env['survey.label'].search([
                        ('question_id','=',question.id),
                        "|",
                            "&",
                                ('model_field_res_id','not in', answer_options.ids),
                                ('model_res_name','=', question.field_id.relation),
                        ('model_res_name','!=',question.field_id.relation)
                    ]).unlink()

                else:
                    self.env['survey.label'].search([
                        ('question_id','=',question.id),
                    ]).unlink()
    
class SurveyLabel(models.Model):
    _inherit = 'survey.label'
    
    survey_id = fields.Many2one('survey.survey', related='question_id.survey_id', string='Survey',store=True)
    next_page_id = fields.Many2one('survey.page','Next Page')
    code = fields.Char('Code')
    model_id = fields.Many2one('ir.model',related="survey_id.model_id",store=True)
    field_id = fields.Many2one('ir.model.fields', related="question_id.field_id", string="Field",domain="[('model_id','=',model_id)]", store=True)
    text = fields.Char('Text in field')
    model_res_name = fields.Char()
    model_field_res_id = fields.Integer()
    
class SurveyPage(models.Model):
    _inherit = 'survey.page'   

    survey_page_rule_ids = fields.One2many('ifs_survey.survey_page_rule','page_id')
    next_page_id = fields.Many2one('survey.page','Next Page')
    
class SurveyPageRule(models.Model):
    _name = 'ifs_survey.survey_page_rule'   
    _order = 'sequence'
    _description = 'Page Rule'
    page_id = fields.Many2one('survey.page','Page',ondelete="cascade") 
    next_page_id = fields.Many2one('survey.page','Next Page',domain="[('survey_id','=',page_id.survey_id)]")
    sequence = fields.Integer('Sequence')


class SurveyUserInputPageSequence(models.Model):
    _name = 'ifs_survey.survey_page_sequence'   
    
    _description = 'Page Rule'
    
    to_page_id = fields.Many2one('survey.page','To Page',ondelete="cascade")
    from_page_id = fields.Many2one('survey.page','From Page',ondelete="cascade")
    user_input_id = fields.Many2one('survey.user_input','Input Id',ondelete="cascade")
    
class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"
    
    model_id = fields.Many2one('ir.model',related="survey_id.model_id",store=True)
    res_id = fields.Integer('Resource Id')
    page_sequence_ids  = fields.One2many('ifs_survey.survey_page_sequence','user_input_id','Page path')
    
    @api.multi
    def write(self,values):
        if bool(self.survey_id.write_on_done) and bool(self.survey_id.model_id):
            if self.state != 'done':
                if 'state' in values and values['state']=='done':
                    res = super(SurveyUserInput,self).write(values)
                    res_id = self.sudo().env[ul.survey_id.model_id.model].create({})
                    self.res_id = res_id.id   
                    for a in self.user_input_line_ids:
                        a._processing_data(True)
                    return res
        return super(SurveyUserInput,self).write(values)
            
    @api.multi
    def previous_page(self,page_id):
        for u in self:
            for s in u.page_sequence_ids.filtered(lambda page_sequence :page_sequence.to_page_id.id == page_id.id):
                return s.from_page_id
            
    @api.multi
    def register_page(self,from_page_id,to_page_id):
        to_page_id_id = to_page_id.id if bool(to_page_id) else False  
        for u in self:
            to_clean = False
            added = False
            for s in u.page_sequence_ids:
                if (s.from_page_id.id if s.from_page_id else False ) == (from_page_id.id if from_page_id else False) and s.to_page_id.id != to_page_id_id:
                    to_clean = s.to_page_id
                    s.to_page_id = to_page_id_id
                    added = True
                elif (s.from_page_id.id if s.from_page_id else False ) == (from_page_id.id if from_page_id else False) and s.to_page_id.id == to_page_id_id:
                    added = True
            if not added :
                self.env['ifs_survey.survey_page_sequence'].create({
                                                                'user_input_id':u.id,
                                                                'from_page_id':from_page_id.id if from_page_id else False,
                                                                'to_page_id':to_page_id.id if to_page_id else False
                                                                })
            if bool(to_clean):
                to_delete = self.clean(to_clean)
                for s in to_delete:
                    self.env['ifs_survey.survey_page_sequence'].browse(s).unlink()
                    
        # clean all the sequent page path       
    def clean(self,from_page_id,to_delete=False):
        for u in self:
           to_delete_list = set() if not to_delete else to_delete
           for s in u.page_sequence_ids:
               if bool(s.from_page_id):
                   if s.from_page_id.id == from_page_id.id:
                        self.clean(s.to_page_id)
                        questions =self.env['survey.question'].sudo().search([('page_id','=',s.from_page_id.id)]).ids
                        ulines = self.env['survey.user_input_line'].sudo().search([('user_input_id','=',self.id),('question_id','in',questions)])
                        for ul in ulines :
                            ul.sudo().unlink()
                        to_delete_list.add(s.id)
           return to_delete_list
           
    @api.model
    def create(self, vals):
        ul = super(SurveyUserInput, self).create(vals)
        if not bool(ul.res_id) and bool(ul.survey_id.model_id.model) and not bool(ul.survey_id.write_on_done):
            res_id = self.sudo().env[ul.survey_id.model_id.model].create({})
            ul.res_id = res_id.id   
        return ul
            
class SurveyUserInputLine(models.Model):
    _inherit = "survey.user_input_line"        

    @api.multi
    def get_value(self):
        for u in self:
                value = False
                if u.answer_type == 'text':
                    value = u.value_text
                elif u.answer_type == 'number':
                    value = u.value_number 
                elif u.answer_type == 'date':
                    value = u.value_date 
                elif u.answer_type == 'free_text':
                    value = u.value_free_text 
                elif u.answer_type == 'suggestion':
                    value = u.value_suggested.value
                return value
    
    @api.constrains('value_text', 'value_number','value_date','value_free_text','value_suggested','value_suggested_row')
    def _processing_data(self,manual=False):
        if bool(survey_id.model_id):
            if not bool(self.survey_id.write_on_done) or manual:
                value = self.get_value()
                if self.answer_type == 'suggestion' and bool(self.value_suggested.text):
                    value = self.value_suggested.text
                if self.answer_type == 'suggestion' and self.question_id.field_id.ttype == 'many2one':
                    value = self.value_suggested.model_field_res_id
                if bool(self.question_id.model_id) and bool(self.question_id.field_id) and self.question_id.field_id.ttype not in ['many2many','one2many']:
                    self.env[self.question_id.model_id.model].sudo().browse(self.user_input_id.res_id).write({self.question_id.field_id.name:value})
        return
                                             
#     @api.model
#     def save_line_multiple_choice(self, user_input_id, question, post, answer_tag):
#         result = super(SurveyUserInputLine, self).save_line_multiple_choice(user_input_id, question, post, answer_tag)
#         
#         input_line_ids = self.search([('user_input_id','=',user_input_id)])
#         vals = None
#         
#         if question.field_id.ttype == 'one2many':
#             vals = {}
#             for input_line_id in input_line_ids:    
#                 vals[question.field_id.relation_field] = input_line_id.value_suggested.model_field_res_id
#         
#         if question.field_id.ttype == 'many2many':
#             vals = []
#             for input_line_id in input_line_ids:
#                 vals.append(input_line_id.value_suggested.model_field_res_id)
#         
#         for input_line_id in input_line_ids:
#             label_res_id = self.env[self.value_suggested.model_res_name].browse(self.value_suggested.model_field_res_id)
#             #update o insert
#             
#         return result                           
        
