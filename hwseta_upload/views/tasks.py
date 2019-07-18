class BaseBrowsingBehavior(TaskSet):

    @task(100)
    def read_partners(self, limit=80):
        Partner = self.client.env['res.partner']
        partner_ids = Partner.search([], limit=limit)
        Partner.read(partner_ids)

    @task(20)
    def read_products(self, limit=80):
        Product = self.client.env['product.product']
        product_ids = Product.search([], limit=limit)
        Product.read(product_ids)

    @task(1)
    def stop(self):
        self.interrupt()

class BaseComputeBehavior(TaskSet):


    def get_80_partners(self, limit=None):
        Partner = self.client.env['res.partner']
        partner_ids = Partner.search([], limit=limit)
        partner_id = Partner.read(partner_ids)
        return partner_id

    @task(100)
    def compute_pv_stuff(self):
        partners = self.get_80_partners(80)
        for partner in partners:
            partner._compute_mtd()
            partner._compute_qtd()
            partner._compute_ytd()
            partner._compute_performance_history_count()
            partner._compute_rewards_count()
            partner._compute_downline_count()


    @task(1)
    def stop(self):
        self.interrupt()

class BaseSalesBehavior(TaskSet):

    def __init__(self, *args, **kwargs):
        super(BaseSalesBehavior, self).__init__(*args, **kwargs)
        self.Sale = self.client.env['sale.order']

    def _create_sale(self, number_of_lines=None):
        if not number_of_lines:
            number_of_lines = random.randint(1, 15)

        partner_id = helper.find_or_create_customer(self.client)
        lines = []
        for idx in range(1, number_of_lines + 1):
            product_id = helper.find_or_create_sellable_product(
                self.client, idx
            )
            line_values = {'product_id': product_id,
                           'product_uom_qty': random.randint(1, 100)}
            line = (0, 0, line_values)
            lines.append(line)
        order_id = self.Sale.create(
            {'partner_id': partner_id,
             'order_line': lines,
             }
        )
        return order_id

    def _create_transaction(self,number_of_lines=None):
        """
        create a transaction
        the transaction consists of
        1 transaction
        2 journal items
        1 journal entry
        1 bank statement
        """
        if not number_of_lines:
            number_of_lines = random.randint(1, 15)
        now = datetime.datetime.now().date().strftime('%d/%m/%y')
        # cust_model = self.client.get_model('res.partner')
        # cust_id = cust_model.search([('name', 'ilike', 'locust')])[0]
        cust_id = helper.find_or_create_customer(self.client)
        transaction_model = self.client.get_model('account.bank.statement.line')
        # journal_item_model = self.client.get_model('account.move.line')
        journal = self.client.get_model('account.journal').search([('name', 'ilike', 'FNB Payment Account')])[0]
        deb_account = self.client.get_model('account.account').search([('name', 'ilike', 'Trade Payable Third Party')])[
            0]
        cred_account = self.client.get_model('account.account').search([('name', 'ilike', 'FNB Payment Account')])[0]

        journal_entry = self.client.get_model('account.move').create({'name': 'locust test journal entry',
                                                                      'date': now,
                                                                      'journal_id': journal,
                                                                      })
        journal_item_lines = []
        for idx in range(1, number_of_lines + 1):
            deb_dict = {'credit': 0,
                        'name': "Locust test debit" + str(idx),
                        'partner_id': cust_id,
                        'move_id': journal_entry,
                        'account_id': deb_account}
            deb_tuple = (0, 0, deb_dict)
            cred_dict = {'debit': 0,
                         'name': "Locust test Credit" + str(idx),
                         'partner_id': cust_id,
                         'move_id': journal_entry,
                         'account_id': cred_account}
            cred_tuple = (0, 0, cred_dict)
            journal_item_lines.append(deb_tuple)
            journal_item_lines.append(cred_tuple)

        # journal = self.client.get_model('account.journal').search([('code', '=', 'BNK3')])[0]
        bs = self.client.get_model('account.bank.statement').create({'name': 'locust test statement',
                                                                     'date': now,
                                                                     'journal_id': journal,
                                                                     })

        transaction_id = transaction_model.create({
            'name': 'Locust test transaction',
            'ref': 'Locust123123',
            'partner_id': cust_id,
            'statement_id': bs,
            'journal_entry_ids': journal_item_lines,
            'date': now,
            # 'amount': 100,
        })
        return transaction_id

    def _confirm_sale(self, order_id):
        self.Sale.action_confirm([order_id])

    @task(20)
    def new_sale(self):
        order_id = self._create_sale()
        self._confirm_sale(order_id)

    @task(20)
    def new_transaction(self):
        transaction_id = self._create_transaction()
        print transaction_id.name

    @task(5)
    def stop(self):
        self.interrupt()


class BaseBackendBehavior(TaskSet):

    def on_start(self):
        self.client.login(self.locust.db_name,
                          self.locust.login,
                          self.locust.password)


class BackendReadOnlyBehavior(BaseBackendBehavior):
    tasks = {BaseBrowsingBehavior: 1}

class BackendComputeBehavior(BaseBackendBehavior):
    tasks = {BaseComputeBehavior: 1}


class BackendWriteOnlyBehavior(BaseBackendBehavior):
    tasks = {BaseSalesBehavior: 1}


class BackendMixedBehavior(BaseBackendBehavior):
    tasks = {BaseBrowsingBehavior: 5, BaseSalesBehavior: 1}


class FrontendBehavior(TaskSet):

    @task(10)
    def index(self):
        self.client.get("/")

    @task(4)
    def shop(self):
        self.client.get("/shop")
