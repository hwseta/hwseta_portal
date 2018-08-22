import csv
import psycopg2
output_myfile = open('vacancy_for_all_2018_2019.csv', 'wb')
wr = csv.writer(output_myfile, delimiter='\t', quoting=csv.QUOTE_ALL)
try:
    conn_string = "host='localhost' dbname='HWSETA' user='odoo' password='odoo'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    wr.writerow(["SDL Number", "WSP No.", 'Organisation Name',
                 "OFO Occupation", "Province", "Main reason why the occupation is listed as a HTFV", "Number of Vacancies"])
    # Getting WSP's which are in current year.
    cursor.execute('select id from wsp_plan where fiscal_year = 30')
    wsp_ids = cursor.fetchall()
    print "wsp_ids ========", wsp_ids
    # Getting Actual Training data for all the WSP.
    count = 0
    for wsp_id in wsp_ids:
        count += 1
        print "WSP No. =========", count, wsp_id
        cursor.execute(
            'select sdl_no, name, employer_id from wsp_plan where id=%s', (wsp_id,))
        sdl_number = cursor.fetchone()
        print "WSP Number =====", sdl_number[1]
        cursor.execute(
            'select employer_sdl_no,name,empl_sic_code_id from res_partner where employer =True and id=%s' % (sdl_number[2],))
        employers = cursor.fetchone()
        cursor.execute(
            "select count(ofo_code), occupation from scarce_and_critical_skills_fields where scarce_and_critical_wsp_id= %s group by occupation", (wsp_id,))
        ofo_ids = cursor.fetchall()
        for ofo_id in ofo_ids:
            print "ofo_ids===", ofo_id
            no_of_vacancies = 0
            cursor.execute(
                'select ofo_code, occupation, province, number_of_vacancies, comments from scarce_and_critical_skills_fields where scarce_and_critical_wsp_id=%s and occupation=%s', (wsp_id, ofo_id[1]))
            vacancy_training_data = cursor.fetchall()
            for vacancy_training_tuple in vacancy_training_data:
                # Getting well formated data for printing
                # OFO Code
                cursor.execute(
                    "select name from ofo_code where id=%s", (vacancy_training_tuple[0],))
                ofo_code = cursor.fetchone()
                if ofo_code is None:
                    pass
                else:
                    ofo_code = ofo_code[0]
                # print "ofo_code =========",ofo_code

                # Occupation
                cursor.execute(
                    "select name from occupation_ofo where id=%s", (vacancy_training_tuple[1],))
                occ_name = cursor.fetchone()
                if occ_name is None:
                    pass
                else:
                    occ_name = occ_name[0]
                # print "occ_name =========",occ_name
                ofo_occ = ''
                if ofo_code and occ_name:
                    ofo_occ = ofo_code + ' - ' + occ_name
                # Province
                cursor.execute(
                    "select name from res_country_state where id=%s", (vacancy_training_tuple[2],))
                province_name = cursor.fetchone()
                if province_name is None:
                    pass
                else:
                    province_name = province_name[0]
                # print "province =========",province_name
                # Number of Vacancies
                if vacancy_training_tuple[3]:
                    no_of_vacancies = no_of_vacancies + \
                        vacancy_training_tuple[3]
            wr.writerow([sdl_number[0], sdl_number[1], employers[
                        1], ofo_occ, province_name, vacancy_training_tuple[4], no_of_vacancies])
            conn.commit()
finally:
    pass
