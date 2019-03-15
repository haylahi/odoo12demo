# -*- coding: utf-8 -*-
{
    
    'name': "STL Viewer",
    'summary': "View Stl 3d model",
    'description': """
    """,
    'author': "Infosons",
    'website': "https://www.infosons.com",
    'support': 'info@infosons.com',
    'category': 'Document Management',
    'version': '0.1',
    'depends': [ 'web','portal'],
    'data': [
        'views/webclient_templates.xml',
    ],
    'qweb': [
        "static/src/xml/base.xml",
    ],
    'images': [
        'static/description/main_screenshot.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}