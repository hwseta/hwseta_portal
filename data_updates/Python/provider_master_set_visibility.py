import psycopg2
'''Python script to remove duplicate transaction from provider master'''
conn_string = "host='localhost' dbname='HWSETA' user='odoo' password='odoo'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
count = 0
cursor.execute(
    "select distinct(provider_accreditation_num) from res_partner where provider = True")
provider_acc_ids = cursor.fetchall()
for provider_acc_num in provider_acc_ids:
    if provider_acc_num:
        cursor.execute(
            "select id from res_partner where provider = True and provider_accreditation_num = %s", ([provider_acc_num[0]]))
        provider_ids = cursor.fetchall()
        pro_lst = []
        for pro_id in provider_ids:
            pro_lst.append(pro_id[0])
        if pro_lst:
            max_provider_id = max(pro_lst)
            # Making new record visible
            if max_provider_id:
                cursor.execute(
                    "update res_partner set is_visible = True where provider = True and id = %s", ([max_provider_id]))
                conn.commit()
            # Making old record invisible
            if len(pro_lst) > 1:
                min_provider_id = min(pro_lst)
                if min_provider_id:
                    cursor.execute(
                        "update res_partner set is_visible = False where provider = True and id = %s", ([min_provider_id]))
                    conn.commit()
