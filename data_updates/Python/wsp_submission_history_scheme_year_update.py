import psycopg2

'''Python script to replace Scheme Year (Char) field with Scheme Year (Many2one field) in Organisation master'''

conn_string = "host='localhost' dbname='HWSETA' user='odoo' password='odoo'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

cursor.execute("select id, scheme_year from wsp_submission_track")
wsp_submission_ids = cursor.fetchall()

for wsp_submission in wsp_submission_ids:
    if wsp_submission[1]:
        print "=========Scheme Year==========", wsp_submission[1]
        cursor.execute("select id from scheme_year where name = %s ",[(wsp_submission[1])])
        scheme_year_id = cursor.fetchone()
        print "====Scheme Year ID====", scheme_year_id[0], 
        wsp_submission[0]
        if scheme_year_id:
            cursor.execute("update wsp_submission_track set scheme_year_id = %s where id = %s", ([scheme_year_id[0],wsp_submission[0]]))
            conn.commit()