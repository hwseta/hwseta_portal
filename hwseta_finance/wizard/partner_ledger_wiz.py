
from openerp.osv import fields, osv

class account_partner_ledger_inh(osv.osv_memory):
    """
    This wizard will provide the partner Ledger report by periods, between any two dates.
    """
    _inherit = 'account.partner.ledger'
    _description = 'Account Partner Ledger'

    _columns = {
        'jvtype': fields.selection([('mandatory', 'Mandatory'), ('discretionary', 'Discretionary')], "JV Type"),
        'sch_yr': fields.boolean("Scheme Year Wise"),
        'partner': fields.many2one('res.partner', 'Partner'),
    }
    
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
    
    def _print_report(self, cr, uid, ids, data, context):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['sch_yr','jvtype','initial_balance', 'filter', 'page_split', 'amount_currency','partner'])[0])
        if data['form'].get('page_split') is True: 
            return self.pool['report'].get_action(cr, uid, [], 'account.report_partnerledgerother', data=data, context=context)
        if context.get('active_model') == "res.partner":
            return self.pool['report'].get_action(cr, uid, [], 'account.report_partnerledger', data=data, context=context)
        else:
            return self.pool['report'].get_action(cr, uid, [], 'hwseta_finance.report_partnerledger_latest', data=data, context=context)