{
    'name' : 'HWSETA Persons',
    'version' : '1.1',
    'author' : 'SMART ICT System',
    'category' : 'HWSETA departments',
    'description' : """
HWSETA PERSONS module covers.
====================================
    Maintains Fields information regarding Employer, Provider, Employer Department, SDF, Assessors and Moderators. 
    """,
    'website': 'https://www.odoo.com/page/billing',
    'depends' : ['hr','hwseta_projects'],
    'data': [
             'web_master_data.xml',
             'person_view.xml',
             'edi/email_template.xml',
             ],
    'qweb' : [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}