import psycopg2
'''Python script to insert Qualifications in Satellite Campus For Provider: The Order Of St John For Sa (HW592A0600149)'''

conn_string = "host='localhost' dbname='HWSETA' user='odoo' password='odoo'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
print "=============Script Started================="
cursor.execute(
    "select id, qualification_id, saqa_qual_id from provider_master_qualification where accreditation_qualification_id = 78309")
qual_ids = cursor.fetchall()

for qual_id in qual_ids:
    cursor.execute("select id from res_partner where parent_id = 78309")
    child_ids = cursor.fetchall()
    for child_id in child_ids:
        print "-----Skill SAQA ID-------", qual_id[2]

        cursor.execute(
            "insert into provider_master_campus_qualification (qualification_id, saqa_qual_id, accreditation_qualification_campus_id) values (%s, %s, %s)", ([qual_id[1], qual_id[2], child_id[0]]))

        cursor.execute(
            'select max(id) from provider_master_campus_qualification')
        master_campus_qual_id = cursor.fetchone()

        cursor.execute(
            "select name,type,id_data,title,level1,level2,level3,selection,is_seta_approved,is_provider_approved from provider_master_qualification_line where line_id ='%s'" % (qual_id[0]))
        qual_unit_ids = cursor.fetchall()

        for qual_unit_id in qual_unit_ids:
            is_seta_approved, is_provider_approved = False, False
            if qual_unit_id[8] is None:
                pass
            else:
                is_seta_approved = qual_unit_id[8]
            if qual_unit_id[9] is None:
                pass
            else:
                is_provider_approved = qual_unit_id[9]
            cursor.execute("insert into provider_master_campus_qualification_line (name, type, id_data, title, level1, level2, level3, selection, line_id, is_seta_approved,is_provider_approved ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", ([
                           str(qual_unit_id[3]), str(qual_unit_id[1]), str(qual_unit_id[2]), str(qual_unit_id[3]), str(qual_unit_id[4]), str(qual_unit_id[5]), str(qual_unit_id[6]), 'True', master_campus_qual_id[0], is_seta_approved, is_provider_approved]))

conn.commit()
print "=================Script Ended==================="