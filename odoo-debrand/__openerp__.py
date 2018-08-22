{
    'name': "Odoo Debranding",
    'version': "8.0.1.0",
    'summary': """Debrand Odoo""",
    'description': """Debrand Odoo""",
    'author': "Pragmatic Techsoft Pvt Ltd",
    'company': "Pragmatic Techsoft Pvt Ltd",
    'website': "http://www.pragtech.co.in",
    'category': 'Tools',
    'depends': ['base', 'im_livechat', 'website'],
    'data': [
        'views/views.xml',
        'views/templates.xml'],
    'demo': [],
    'qweb': ["static/src/xml/*.xml"],
    'images': ['static/description/icon.jpg'],
    'installable': True,
    'application': False
}
