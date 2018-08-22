{
    'name' : 'HWSETA Sales and Marketing',
    'version' : '1.1',
    'author' : 'SMART ICT System',
    'category' : 'Sales and Marketing',
    'description' : """
HWSETA Sales and Marketing module covers.
====================================
    * Manage Sales Process
    * Manage Customers and Contacts
    * Manage Marketing Process
    """,
    'website': 'https://www.odoo.com/page/billing',
    'depends' : ['sale', 'marketing_crm', 'marketing_campaign','stock_indent'],
    'data': [
             'marketing_menus.xml',
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
