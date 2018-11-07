# -*- coding: utf-8 -*-
{
    'name': """ Infosons Survey Addons """,

    'summary':  """
        Infosons Survey Addons
    """,

    'description':"""
          Survey for addons to create model throug survey
        """,

    'author': "Infosons",
    'website': "http://www.infosons.com",
    'depends': ['mail','survey'],
    'data': [
             'security/ir.model.access.csv',
            'views/survey_views.xml',
            
        ],
}