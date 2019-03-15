# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):

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