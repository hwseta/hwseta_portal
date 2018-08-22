# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw
from openerp.addons.account.report import common_report_header as common_report
from openerp import SUPERUSER_ID


class partner_balance(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(partner_balance, self).__init__(cr, uid, name, context=context)
        self.account_ids = []
        self.localcontext.update( {
            'time': time,
            'get_fiscalyear': self._get_fiscalyear,
            'get_journal': self._get_journal,
            'get_filter': self._get_filter,
            'get_account': self._get_account,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_partners':self._get_partners,
            'get_target_move': self._get_target_move,
        })

    def _get_fiscalyear(self, data):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            return self.pool.get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).name
        return ''

    def _get_filter(self, data):
        if data.get('form', False) and data['form'].get('filter', False):
            if data['form']['filter'] == 'filter_date':
                return self._translate('Date')
            elif data['form']['filter'] == 'filter_period':
                return self._translate('Periods')
        return self._translate('No Filters')
    
    def _get_account(self, data):
        if data.get('form', False) and data['form'].get('chart_account_id', False):
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['chart_account_id']).name
        return ''
    
    def _get_journal(self, data):
        codes = []
        if data.get('form', False) and data['form'].get('journal_ids', False):
            self.cr.execute('select code from account_journal where id IN %s',(tuple(data['form']['journal_ids']),))
            codes = [x for x, in self.cr.fetchall()]
        return codes
    
    def _get_start_date(self, data):
        if data.get('form', False) and data['form'].get('date_from', False):
            return data['form']['date_from']
        return ''

    def _get_target_move(self, data):
        if data.get('form', False) and data['form'].get('target_move', False):
            if data['form']['target_move'] == 'all':
                return _('All Entries')
            return _('All Posted Entries')
        return ''

    def _get_end_date(self, data):
        if data.get('form', False) and data['form'].get('date_to', False):
            return data['form']['date_to']
        return ''

    def get_start_period(self, data):
        if data.get('form', False) and data['form'].get('period_from', False):
            return self.pool.get('account.period').browse(self.cr,self.uid,data['form']['period_from']).name
        return ''

    def get_end_period(self, data):
        if data.get('form', False) and data['form'].get('period_to', False):
            return self.pool.get('account.period').browse(self.cr, self.uid, data['form']['period_to']).name
        return ''

    
    def set_context(self, objects, data, ids, report_type=None):
        self.display_partner = data['form'].get('display_partner', 'non-zero_balance')
        obj_move = self.pool.get('account.move.line')
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=data['form'].get('used_context', {}))
        self.result_selection = data['form'].get('result_selection')
        self.target_move = data['form'].get('target_move', 'all')
        self.partner = data['form'].get('partner')
        if (self.result_selection == 'customer' ):
            self.ACCOUNT_TYPE = ('receivable',)
        elif (self.result_selection == 'supplier'):
            self.ACCOUNT_TYPE = ('payable',)
        else:
            self.ACCOUNT_TYPE = ('payable', 'receivable')

        self.cr.execute("SELECT a.id " \
                "FROM account_account a " \
                "LEFT JOIN account_account_type t " \
                    "ON (a.type = t.code) " \
                    "WHERE a.type IN %s " \
                    "AND a.active", (self.ACCOUNT_TYPE,))
        self.account_ids = [a for (a,) in self.cr.fetchall()]
        res = super(partner_balance, self).set_context(objects, data, ids, report_type=report_type)
        lines = self.lines()
        sum_debit = sum_credit = sum_litige = 0
        for line in filter(lambda x: x['type'] == 3, lines):
            sum_debit += line['debit'] or 0
            sum_credit += line['credit'] or 0
            sum_litige += line['enlitige'] or 0
        self.localcontext.update({
            'lines': lambda: lines,
            'sum_debit': lambda: sum_debit,
            'sum_credit': lambda: sum_credit,
            'sum_litige': lambda: sum_litige,
        })
        return res

    def lines(self):
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted']
        full_account = []
        if not self.partner:
            self.cr.execute(
                "SELECT p.ref,l.account_id,ac.name AS account_name,ac.code AS code,p.name, sum(debit) AS debit, sum(credit) AS credit, " \
                        "CASE WHEN sum(debit) > sum(credit) " \
                            "THEN sum(debit) - sum(credit) " \
                            "ELSE 0 " \
                        "END AS sdebit, " \
                        "CASE WHEN sum(debit) < sum(credit) " \
                            "THEN sum(credit) - sum(debit) " \
                            "ELSE 0 " \
                        "END AS scredit, " \
                        "(SELECT sum(debit-credit) " \
                            "FROM account_move_line l " \
                            "WHERE partner_id = p.id " \
                                "AND " + self.query + " " \
                                "AND blocked = TRUE " \
                        ") AS enlitige " \
                "FROM account_move_line l LEFT JOIN res_partner p ON (l.partner_id=p.id) " \
                "JOIN account_account ac ON (l.account_id = ac.id)" \
                "JOIN account_move am ON (am.id = l.move_id)" \
                "WHERE ac.type IN %s " \
                "AND am.state IN %s " \
                "AND " + self.query + "" \
                "GROUP BY p.id, p.ref, p.name,l.account_id,ac.name,ac.code " \
                "ORDER BY l.account_id,p.name",
                (self.ACCOUNT_TYPE, tuple(move_state)))
            res = self.cr.dictfetchall()
        else:
            self.cr.execute(
                "SELECT p.ref,l.account_id,ac.name AS account_name,ac.code AS code,p.name, sum(debit) AS debit, sum(credit) AS credit, " \
                        "CASE WHEN sum(debit) > sum(credit) " \
                            "THEN sum(debit) - sum(credit) " \
                            "ELSE 0 " \
                        "END AS sdebit, " \
                        "CASE WHEN sum(debit) < sum(credit) " \
                            "THEN sum(credit) - sum(debit) " \
                            "ELSE 0 " \
                        "END AS scredit, " \
                        "(SELECT sum(debit-credit) " \
                            "FROM account_move_line l " \
                            "WHERE partner_id = p.id " \
                                "AND " + self.query + " " \
                                "AND blocked = TRUE " \
                        ") AS enlitige " \
                "FROM account_move_line l LEFT JOIN res_partner p ON (l.partner_id=p.id) " \
                "JOIN account_account ac ON (l.account_id = ac.id)" \
                "JOIN account_move am ON (am.id = l.move_id)" \
                "WHERE ac.type IN %s " \
                "AND am.state IN %s " \
                "AND " + self.query + "" \
                "AND l.partner_id = %s " \
                "GROUP BY p.id, p.ref, p.name,l.account_id,ac.name,ac.code " \
                "ORDER BY l.account_id,p.name",
                (self.ACCOUNT_TYPE, tuple(move_state),self.partner))
            res = self.cr.dictfetchall()


        if self.display_partner == 'non-zero_balance':
            full_account = [r for r in res if r['sdebit'] > 0 or r['scredit'] > 0]
        else:
            full_account = [r for r in res]

        for rec in full_account:
            if not rec.get('name', False):
                rec.update({'name': _('Unknown Partner')})

        ## We will now compute Total
        subtotal_row = self._add_subtotal(full_account)
        return subtotal_row

    def _add_subtotal(self, cleanarray):
        i = 0
        completearray = []
        tot_debit = 0.0
        tot_credit = 0.0
        tot_scredit = 0.0
        tot_sdebit = 0.0
        tot_enlitige = 0.0
        for r in cleanarray:
            # For the first element we always add the line
            # type = 1 is the line is the first of the account
            # type = 2 is an other line of the account
            if i==0:
                # We add the first as the header
                #
                ##
                new_header = {}
                new_header['ref'] = ''
                new_header['name'] = r['account_name']
                new_header['code'] = r['code']
                new_header['debit'] = r['debit']
                new_header['credit'] = r['credit']
                new_header['scredit'] = tot_scredit
                new_header['sdebit'] = tot_sdebit
                new_header['enlitige'] = tot_enlitige
                new_header['balance'] = r['debit'] - r['credit']
                new_header['type'] = 3
                ##
                completearray.append(new_header)
                #
                r['type'] = 1
                r['balance'] = float(r['sdebit']) - float(r['scredit'])

                completearray.append(r)
                #
                tot_debit = r['debit']
                tot_credit = r['credit']
                tot_scredit = r['scredit']
                tot_sdebit = r['sdebit']
                tot_enlitige = (r['enlitige'] or 0.0)
                #
            else:
                if cleanarray[i]['account_id'] <> cleanarray[i-1]['account_id']:

                    new_header['debit'] = tot_debit
                    new_header['credit'] = tot_credit
                    new_header['scredit'] = tot_scredit
                    new_header['sdebit'] = tot_sdebit
                    new_header['enlitige'] = tot_enlitige
                    new_header['balance'] = float(tot_sdebit) - float(tot_scredit)
                    new_header['type'] = 3
                    # we reset the counter
                    tot_debit = r['debit']
                    tot_credit = r['credit']
                    tot_scredit = r['scredit']
                    tot_sdebit = r['sdebit']
                    tot_enlitige = (r['enlitige'] or 0.0)
                    #
                    ##
                    new_header = {}
                    new_header['ref'] = ''
                    new_header['name'] = r['account_name']
                    new_header['code'] = r['code']
                    new_header['debit'] = tot_debit
                    new_header['credit'] = tot_credit
                    new_header['scredit'] = tot_scredit
                    new_header['sdebit'] = tot_sdebit
                    new_header['enlitige'] = tot_enlitige
                    new_header['balance'] = float(tot_sdebit) - float(tot_scredit)
                    new_header['type'] = 3
                    ##get_fiscalyear
                    ##

                    completearray.append(new_header)
                    ##
                    #
                    r['type'] = 1
                    #
                    r['balance'] = float(r['sdebit']) - float(r['scredit'])

                    completearray.append(r)

                if cleanarray[i]['account_id'] == cleanarray[i-1]['account_id']:
                    # we reset the counter

                    new_header['debit'] = tot_debit
                    new_header['credit'] = tot_credit
                    new_header['scredit'] = tot_scredit
                    new_header['sdebit'] = tot_sdebit
                    new_header['enlitige'] = tot_enlitige
                    new_header['balance'] = float(tot_sdebit) - float(tot_scredit)
                    new_header['type'] = 3

                    tot_debit = tot_debit + r['debit']
                    tot_credit = tot_credit + r['credit']
                    tot_scredit = tot_scredit + r['scredit']
                    tot_sdebit = tot_sdebit + r['sdebit']
                    tot_enlitige = tot_enlitige + (r['enlitige'] or 0.0)

                    new_header['debit'] = tot_debit
                    new_header['credit'] = tot_credit
                    new_header['scredit'] = tot_scredit
                    new_header['sdebit'] = tot_sdebit
                    new_header['enlitige'] = tot_enlitige
                    new_header['balance'] = float(tot_sdebit) - float(tot_scredit)

                    #
                    r['type'] = 2
                    #
                    r['balance'] = float(r['sdebit']) - float(r['scredit'])
                    #

                    completearray.append(r)

            i = i + 1
        return completearray

    def _get_partners(self):

        if self.result_selection == 'customer':
            return _('Receivable Accounts')
        elif self.result_selection == 'supplier':
            return _('Payable Accounts')
        elif self.result_selection == 'customer_supplier':
            return _('Receivable and Payable Accounts')
        return ''


class report_partnerbalance(osv.AbstractModel):
    _name = 'report.hwseta_finance.report_partnerbalance'
    _inherit = 'report.abstract_report'
    _template = 'hwseta_finance.report_partnerbalance'
    _wrapped_report_class = partner_balance

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
