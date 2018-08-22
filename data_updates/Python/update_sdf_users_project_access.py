import psycopg2
'''Python script to update SDF users with project access'''

conn_string = "host='localhost' dbname='HWSETA' user='odoo' password='odoo'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
cursor.execute("select id from res_users where sdf_id in (select id from hr_employee where is_sdf = True)")
user_ids = cursor.fetchall()
cnt = 0
if user_ids:
    for u_id in list(set(user_ids)):
        print "==User ID==", u_id[0]
        cursor.execute("select gid, uid from res_groups_users_rel where uid = %s and gid = 24",[str(u_id[0])])
        access_exist = cursor.fetchall()
        print "----Access Exist----", access_exist
        if not access_exist:
            cursor.execute("insert into res_groups_users_rel (gid, uid) values (24,'%s')"%(u_id))
            cnt += 1
print "=========Updated count======",cnt
conn.commit()