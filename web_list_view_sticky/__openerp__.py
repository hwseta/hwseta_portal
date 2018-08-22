{
    'name': 'List View Fixed Table Header',
    'version': '1.2',
    'category': 'Tools',
    'sequence': 15,
    'summary': 'Web List View Fixed Table Header',
    'description': """
Web List View Fixed Table Header
=================================
* Fixed (sticky) list view table header, very helpful when dealing with many record.
""",
    'author' : 'SMART ICT System',
    'depends': ['web','base'],
    'data': [
        'views/web_list_view_sticky.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}