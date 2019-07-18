{
    'name' : 'HWSETA ETQE',
    'version' : '1.1',
    'author' : 'SMART ICT System',
    'category' : 'HWSETA ETQE',
    'description' : """
HWSETA ETQA module covers.
====================================
    
    """,
    'website': 'https://www.odoo.com/page/billing',
    'depends' : ['portal', 'hwseta_sdp'],
    'data': [
        'security/hwseta_etqe_security.xml',
        'security/ir.model.access.csv',
        'data/accreditation_sequence.xml',
        'wizard/approve_learner_wizard_view.xml',
        'provider.xml',
        'admin_view.xml',
        'skills_programme_view.xml',
        'etqe_learning_programme.xml',
        'report/provider_verification.xml',
        'static/src/xml/verification_report_layout.xml',
        'views/provider_verification_report.xml',
        'views/etqe_ext_css.xml',
        'views/accreditation_certificate_view.xml',
        'views/report_achievement_certificate.xml',
        'views/report_qualification_stmt_of_result.xml',
        'views/report_qdm_achievement_certificate.xml',
        'views/report_skills_statement_of_results.xml',
        'views/report_lp_achievement_certificate.xml',
        'views/report_lp_statement_of_result.xml',
        'views/letter_of_approval_view.xml',
        'views/report_provider_extension_of_scope.xml',
        'views/learner_status_report.xml',
        'views/import_learners.xml',
        'views/letter_of_approval_ass_mod.xml',
        'views/report_ass_mod_eoi.xml',
        'views/report_ass_mod_reregistration.xml',
        'views/provider_endorsement_letter.xml',
        'report/accreditation_certificate.xml',
        'report/achievement_certificate.xml',
        'report/letter_of_approval.xml',
        'report/learner_status.xml',
        'report/provider_endorsement.xml',
        'edi/accreditation_action_data.xml',
        
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