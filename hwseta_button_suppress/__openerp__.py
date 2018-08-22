{
    'name' : 'Button Supressing',
    'version' : '1.1',
    'author' : 'smart ICT',
    'category' : 'Internal',
    'description' : """
    Hide the dropdown buttons on the basis of users
    """,
    'website': 'pragtech.co.in',
    'depends' : ['web'],
    'data': [
             'views/button_view.xml'
    ],
    'qweb' : [
        "static/src/xml/button.xml",
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
