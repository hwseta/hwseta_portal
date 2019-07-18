{
    'name' : 'HWSETA Upload',
    'version' : '1.1',
    'author' : 'Dylan Bridge',
    'category' : 'Skills and Development Management',
    'description' : """
HWSETA Upload module covers.
====================================
    - WSS/WSP uploads
    """,
    'website': 'https://www.odoo.com/page/billing',
    'depends' : ['hwseta_sdp','hwseta_person'],
    'data': [
        'data/data.xml',
        'security/upload_access.xml',
        'security/ir.model.access.csv',
        'views/wss_upload_view.xml',
        'views/wss_upload_form.xml',
        'views/res_config_view.xml',
    ],
    'qweb' : [

    ],
    'demo': [
    ],
    'test': [
    ],
    
    'installable': True,
    'auto_install': False,
}
