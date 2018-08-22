{
    'name' : 'HWSETA Projects',
    'version' : '1.1',
    'author' : 'SMART ICT System',
    'category' : 'Projects Management',
    'description' : """
HWSETA Projects module covers.
====================================
    """,
    'website': 'https://www.odoo.com/page/billing',
    'depends' : ['base','project',],
    'data': [
        'project_view.xml',
        'security/hwseta_projects_security.xml',
        'security/ir.model.access.csv',
    
        
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
