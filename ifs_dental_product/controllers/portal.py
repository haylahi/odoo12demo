# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.osv.expression import OR
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.exceptions import ValidationError

class CustomerPortal(WebsiteForm,CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        values['treatment_count'] = request.env['ifs_dental_product.treatment'].search_count([])
        
        return values

    def _treatment_get_page_view_values(self, treatment, access_token, **kwargs):
        values = {
            'page_name': 'treatment',
            'treatment': treatment,
        }
        return self._get_page_view_values(treatment, access_token, values, 'my_treatments_history', False, **kwargs)

    @http.route(['/my/treatments', '/my/treatment/page/<int:page>'], type='http', auth="user", website=True)
    def my_dental_treatment(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Subject'), 'order': 'name'},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('ifs_dental_product.treatment', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search)]])
            domain += search_domain

        # pager
        treatments_count = request.env['ifs_dental_product.treatment'].search_count(domain)
        pager = portal_pager(
            url="/my/treatments",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=treatments_count,
            page=page,
            step=self._items_per_page
        )

        treatments = request.env['ifs_dental_product.treatment'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_treatment_history'] = treatments.ids[:100]

        values.update({
            'date': date_begin,
            'treatments': treatments,
            'page_name': 'treatment',
            'default_url': '/my/treatment',
            'pager': pager,
            'archive_groups': archive_groups,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'sortby': sortby,
            'search_in': search_in,
            'search': search,
        })
        return request.render("ifs_dental_product.portal_treatments_treatment", values)

    @http.route([
        "/treatments/treatment/<int:treatment_id>",
        "/treatments/treatment/<int:treatment_id>/<token>",
        '/my/treatment/<int:treatment_id>'
    ], type='http', auth="public", website=True)
    def treatments_followup(self, treatment_id=None, access_token=None, **kw):
        try:
            treatment_sudo = self._document_check_access('ifs_dental_product.treatment', treatment_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._treatment_get_page_view_values(treatment_sudo, access_token, **kw)
        return request.render("ifs_dental_product.treatments_followup", values)
    
    
    @http.route(['/treatment/patient-data/<int:treatment_id>','/treatment/patient-data'], type='http', auth="public",method="post", website=True)
    def treatment_patient_data(self, treatment_id=None, **kw):
        model_record = request.env['ir.model'].sudo().search([('model', '=', 'ifs_dental_product.patient')])
        try:
            data = self.extract_data(model_record, request.params)
        # If we encounter an issue while extracting data
        except ValidationError as e:
            # I couldn't find a cleaner way to pass data to an exception
            return json.dumps({'error_fields' : e.args[0]})
        try:
            id_record = self.insert_record(request, model_record, data['record'], data['custom'], data.get('meta'))
            if id_record:
                self.insert_attachment(model_record, id_record, data['attachments'])

        # Some fields have additional SQL constraints that we can't check generically
        # Ex: crm.lead.probability which is a float between 0 and 1
        # TODO: How to get the name of the erroneous field ?
        except IntegrityError:
            return json.dumps(False)
        products = [(product_id.id,product_id.display_name + " (" +str(product_id.list_price)+ " € )" ) for product_id in request.env['product.product'].search([(True,'=',True)])]
        select_options = {
            'product_id': products
        }
        return request.render("ifs_dental_product.treatment_data", {'patient_id':id_record,'select_options':select_options})

    
    @http.route(['/treatment/treatment-data/<int:treatment_id>','/treatment/treatment-data'], type='http', auth="public",method="post", website=True)
    def treatment_treatment_data(self, treatment_id=None, **kw):
        model_record = request.env['ir.model'].sudo().search([('model', '=', 'ifs_dental_product.treatment')])
        try:
            data = self.extract_data(model_record, request.params)
        # If we encounter an issue while extracting data
        except ValidationError as e:
            # I couldn't find a cleaner way to pass data to an exception
            return json.dumps({'error_fields' : e.args[0]})
        try:
            id_record = self.insert_record(request, model_record, data['record'], data['custom'], data.get('meta'))
            if id_record:
                self.insert_attachment(model_record, id_record, data['attachments'])

        # Some fields have additional SQL constraints that we can't check generically
        # Ex: crm.lead.probability which is a float between 0 and 1
        # TODO: How to get the name of the erroneous field ?
        except IntegrityError:
            return json.dumps(False)
        return request.render("ifs_dental_product.treatment_photo", {'treatment_id':id_record})
    
    
    
    @http.route(['/treatment/treatment-photo/<int:treatment_id>','/treatment/treatment-photo'], type='http', auth="public",method="post", website=True)
    def treatment_treatment_photo(self, treatment_id=None, **kw):
        model_record = request.env['ir.model'].sudo().search([('model', '=', 'ifs_dental_product.treatment')])
        treatment_id = request.params.pop('treatment_id')
        try:
            data = self.extract_data(model_record, request.params)
        # If we encounter an issue while extracting data
        except ValidationError as e:
            # I couldn't find a cleaner way to pass data to an exception
            return json.dumps({'error_fields' : e.args[0]})
        try:
            id_record = self.update_record(request, model_record,treatment_id, data['record'], data['custom'], data.get('meta'))
            if id_record:
                self.insert_attachment(model_record, id_record, data['attachments'])

        # Some fields have additional SQL constraints that we can't check generically
        # Ex: crm.lead.probability which is a float between 0 and 1
        # TODO: How to get the name of the erroneous field ?
        except IntegrityError:
            return json.dumps(False)
        return request.redirect("/treatments/treatment/"+str(id_record))
    
    
    @http.route('''/treatments/submit''', type='http', auth="public", website=True)
    def website_treatment_form(self, **kwargs):
        default_values = {}
#         if request.env.user.partner_id != request.env.ref('base.public_partner'):
#             default_values['name'] = request.env.user.partner_id.name
#             default_values['email'] = request.env.user.partner_id.email
        return request.render("ifs_dental_product.treatment_submit", { 'default_values': default_values})


    def update_record(self, request, model, res_id, values, custom, meta=None):
        model_name = model.sudo().model
        record = request.env[model_name].sudo().with_context(mail_create_nosubscribe=True).browse(int(res_id))
        record.write(values)
        if custom or meta:
            default_field = model.website_form_default_field_id
            default_field_data = values.get(default_field.name, '')
            custom_content = (default_field_data + "\n\n" if default_field_data else '') \
                           + (self._custom_label + custom + "\n\n" if custom else '') \
                           + (self._meta_label + meta if meta else '')

            # If there is a default field configured for this model, use it.
            # If there isn't, put the custom data in a message instead
            if default_field.name:
                if default_field.ttype == 'html' or model_name == 'mail.mail':
                    custom_content = nl2br(custom_content)
                record.update({default_field.name: custom_content})
            else:
                values = {
                    'body': nl2br(custom_content),
                    'model': model_name,
                    'message_type': 'comment',
                    'no_auto_thread': False,
                    'res_id': record.id,
                }
                mail_id = request.env['mail.message'].sudo().create(values)

        return record.id
