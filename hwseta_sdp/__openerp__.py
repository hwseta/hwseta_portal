{
    'name' : 'HWSETA SDP',
    'version' : '1.1',
    'author' : 'SMART ICT System',
    'category' : 'Skills and Development Management',
    'description' : """
HWSETA SDP module covers.
====================================
    - Learning Programme Implementation
    - SDF Registration
    - SDF Profile Creation
    - Workplace Skill Plan / Implementation Report (WSP/IR) Submission.
    - Monitoring and Evaluation Report.
    - Transche Payment.
    """,
    'website': 'https://www.odoo.com/page/billing',
    'depends' : ['stock_indent', 'hwseta_finance','document'],
    'data': [
        'edi/email_notification_sdp.xml',
        'static/src/xml/monitor_layout.xml',
        'static/src/xml/learner_agg_layout.xml',
        'security/sdf_access.xml',
        'security/ir.model.access.csv',
        'views/data.xml',
        'wizard/import_wsp_xls.xml',
        'wizard/export_wsp_xls.xml',
        'wizard/xls_error_validation.xml',
        'wizard/moa_attachment_view.xml',
        'wizard/wsp_error_log.xml',
        'wizard/atr_error_log.xml',
        'learner_sequence.xml',
        'wsp_view.xml',
        'sdp_view.xml',
        'learnership_view.xml',
        'monitor_and_evaluate_view.xml',
        'sdp_report.xml',
        'views/monitor_evaluate.xml',
        'views/learner_agreement_report.xml',
        'transche_payment_view.xml',
        'views/sdp_ext_css.xml',
        'views/atr_report.xml',
        'views/wsp_report.xml',
        'views/error_log_report.xml',
        'views/wsp_error_log_report.xml',
        'views/atr_error_log_report.xml',
        'data/learner_registration_sequence.xml',
    ],
    'qweb' : [ "static/src/xml/base.xml",],
    'demo': [
    ],
    'test': [
    ],
    
    'installable': True,
    'auto_install': False,
}
