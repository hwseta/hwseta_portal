from openerp.osv import fields, osv
# from openerp import models, fields, api, _

class account_partner_balance_report(osv.osv_memory):
    """
        This wizard will provide the partner balance report by periods, between any two dates.
    """
    _inherit = 'account.common.report'
    _description = 'Print Account Partner Balance'
    _name ="account.common.report.new"
    _columns = {
        'display_partner': fields.selection([('non-zero_balance', 'With balance is not equal to 0'), ('all', 'All Partners')]
                                    ,'Display Partners'),
        'journal_ids': fields.many2many('account.journal', 'account_partner_balance_journal_rel', 'account_id', 'journal_id', 'Journals', required=True),
           
        'partner': fields.many2one('res.partner', 'Partner'),
        
        'result_selection': fields.selection([('customer','Receivable Accounts'),
                                              ('supplier','Payable Accounts'),
                                              ('customer_supplier','Receivable and Payable Accounts')],
                                              "Partner's", required=True),

    }
    
    _defaults = {
        'display_partner': 'non-zero_balance',
         'result_selection': 'customer',
    }
    
    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move','partner'], context=context)[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to','partner']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)
    
    
    
    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['display_partner'])[0])
        return self.pool['report'].get_action(cr, uid, [], 'hwseta_finance.report_partnerbalance', data=data, context=context)
    
    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data['form'].update(self.read(cr, uid, ids, ['amount_currency'], context=context)[0])
        fy_ids = data['form']['fiscalyear_id'] and [data['form']['fiscalyear_id']] or self.pool.get('account.fiscalyear').search(cr, uid, [('state', '=', 'draft')], context=context)
        period_list = data['form']['periods'] or self.pool.get('account.period').search(cr, uid, [('fiscalyear_id', 'in', fy_ids)], context=context)
        data['form']['active_ids'] = self.pool.get('account.journal.period').search(cr, uid, [('journal_id', 'in', data['form']['journal_ids']), ('period_id', 'in', period_list)], context=context)
        return data
    
    
#     @api.multi
    def onchange_result_selection_new(self, cr,uid,ids,result_selection) :
        res = {}
        if not result_selection :
            return res
        if result_selection == 'customer':
            res_part=self.pool.get('res.partner').search(cr,uid,[('customer','=',True)])
        elif result_selection == 'supplier':
            res_part=self.pool.get('res.partner').search(cr,uid,[('supplier','=',True)])
        else:
            res_part=self.pool.get('res.partner').search(cr,uid,[])
        res={'domain': {'partner':[('id','in', res_part)]}}
        return res