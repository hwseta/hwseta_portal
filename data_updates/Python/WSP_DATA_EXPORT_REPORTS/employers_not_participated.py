import psycopg2
import csv
output_myfile = open('Organisation Not Participated in 2018-19.csv', 'wb')
wr = csv.writer(output_myfile, delimiter='\t', quoting=csv.QUOTE_ALL)
try:
    conn_string = "host='localhost' dbname='HWSETA' user='odoo' password='odoo'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    
    cursor.execute("select employer_id from wsp_plan where fiscal_year = 30")
    employer_ids = sorted(map(lambda x: x[0], cursor.fetchall()))

    cursor.execute(
        'select id, name, employer_sdl_no, empl_sic_code_id from res_partner where employer=True and active=True')
    employer_values = cursor.fetchall()
    
    wr.writerow(['Employer Name', 'Employer SDL No', 'SIC Code'])
    count = 0

    for employer_val in employer_values:
        if employer_val[0] not in employer_ids:
            sic_code = ''
            cursor.execute(
                'select code from hwseta_sic_master where name= %s', (employer_val[3], ))
            sic_code_details = cursor.fetchone()
            if sic_code_details:
                sic_code = sic_code_details[0]
            wr.writerow([employer_val[1], employer_val[2], sic_code])
            count += 1
    print"count ", count
    conn.commit()
finally:
    pass
