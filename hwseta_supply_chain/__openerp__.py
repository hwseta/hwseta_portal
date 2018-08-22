{
    'name' : 'HWSETA Supply Chain',
    'version' : '1.1',
    'author' : 'SMART ICT System',
    'category' : 'Supply Chain Management',
    'description' : """
HWSETA Supply Chain module covers.
====================================
    - Indent Management.
    - Purchase Multilevel Validation for Approval from Higher Authority.
    - Purchase Requisition.
    - Tender Management.
    """,
    'website': 'https://www.odoo.com/page/billing',
    'depends' : ['purchase_double_validation','purchase_requisition','stock_indent'],
    'data': [
             'supply_chain_view.xml',
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
