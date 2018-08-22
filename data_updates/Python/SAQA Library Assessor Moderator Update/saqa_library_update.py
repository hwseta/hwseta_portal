import psycopg2

'''Python script to update Assessor/Moderator Qualifications in SAQA Library'''

conn_string = "host='localhost' dbname='HWSETA' user='odoo' password='odoo'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

print "********Script Started***********"
skill_lp_linked_qual_list = ["74290", "58786", "50062", "64149", "50063", "79806"]
count = 0
cursor.execute("select id from provider_qualification where seta_branch_id = '1' or saqa_qual_id in %s", [
               tuple(skill_lp_linked_qual_list)])
qualification_ids = cursor.fetchall()
for qualification_id in qualification_ids:
    count += 1
    print "===Updated Count===", count
    cursor.execute('update provider_qualification set is_ass_mod_linked = true where id = %s' % (
        qualification_id))
    conn.commit()
print "*******Script Ended************"
