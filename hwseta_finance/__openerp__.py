{
    'name' : 'HWSETA Finance',
    'version' : '1.1',
    'author' : 'SMART ICT System',
    'category' : 'Accounting & Finance',
    'description' : """
HWSETA Finance module covers.
====================================
    * Employers Master
    * Employer Invoices
    * Leavy Income Management
        - Leavy Income Configuration : Provide Account Configuration for Leavies.
        - Leavy Import Facility.
        - Employer Invoice Creation after Leavy Import for Mandatory Grants.
        - Manages Leavy History in Employer Master. 
    * Petty Cash Management
        - Petty Cash Approval Process.
        - Cash Register line entries for petty cash.
    * Asset Management
        - Facility to declare product as Asset.
        - Creates Asset with Depreciation after product receipts.
        
    
    """,
    'website': 'https://www.odoo.com/page/billing',
    'depends' : ['account','account_accountant', 'analytic','account_cancel', 'account_voucher','stock_indent', 'hwseta_person', 'account_asset','account_budget'],
    'data': [
        'data/finance_sequence.xml',
        'edi/email_notification_finance.xml',
        'static/src/xml/petty_cash_layout.xml',
        'security/finance_rights.xml',
        'security/ir.model.access.csv',
        'views/data.xml',
        'employer.xml',
        'petty_cash_view.xml',
        'account_view.xml',
        'finance_report.xml',
        'views/petty_cash_report.xml',
        'views/petty_ext_css.xml',
        'wizard/leavy_income_view.xml',
        'wizard/employer_unpaid.xml',
        'wizard/mandatory_wiz.xml',
        'wizard/surplus_mandatory_income_wiz.xml',
        'wizard/levy_exempted_wiz.xml',
        'wizard/levy_import_log.xml',
        'views/leavy_unpaid.xml',
        'views/mandatory_grant_report.xml',
        'views/mandatory_income_report.xml',
        'views/levy_exempted_report.xml',
        'views/account_move_line_rep.xml',
        'views/emp_wise_report_view.xml',
        'views/emp_wise_levy_report.xml',
        'views/partner_ledger_scheme_yearwise_view.xml',
        'views/partner_ledger_inherited_rep.xml',
        'views/report_outstanding_mandatory_grant.xml',
        'wizard/account_ledger_report_wizard_view.xml',
        'wizard/employer_wise_wiz_view.xml',
        'wizard/partner_ledger_wiz_view.xml',
        'wizard/outstanding_mandatory_grant_wiz.xml',
        'wizard/account_partner_balance_report_hwseta.xml',
        'wizard/account_validate_move_view.xml',
        'views/account_partner_bal_new.xml',
        'views/organisation_payment_report.xml',
        'report/organisation_payment.xml'
        
        
        
        
        
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
