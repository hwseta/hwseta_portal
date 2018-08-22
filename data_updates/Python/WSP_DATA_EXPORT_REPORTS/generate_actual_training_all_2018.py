import csv
import psycopg2
output_myfile = open('actual_training_for_all_2018_2019.csv', 'wb')
wr = csv.writer(output_myfile, delimiter='\t', quoting=csv.QUOTE_ALL)
try:
    conn_string = "host='localhost' dbname='HWSETA' user='odoo' password='odoo'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    wr.writerow(["SDL Number", "WSP No.", 'Organisation Name', 'Sic Code/Industry', "Province", "City", "OFO Occupation", "African Male", "African Female", "African Disabled", "Coloured Male", "Coloured Female",
                 "Coloured Disabled", "Indian Male", "Indian Female", "Indian Disabled", "White Male", "White Female", "White Disabled", "Total Male", "Total Female", "Total Disabled"])
    # Getting WSP's which are in current year.
    cursor.execute('select id from wsp_plan where fiscal_year = 30')
    wsp_ids = cursor.fetchall()
    # Getting Actual Training data for all the WSP.
    count = 0
    for wsp_id in wsp_ids:
        count += 1
        print "WSP No. ============================", count
        cursor.execute(
            'select sdl_no, name, sdf_id, employer_id from wsp_plan where id=%s', (wsp_id,))
        sdl_number = cursor.fetchone()
        print "WSP Number =====", sdl_number[1]
        cursor.execute(
            'select employer_sdl_no,name,empl_sic_code_id from res_partner where employer =True and id=%s' % (sdl_number[3],))
        employers = cursor.fetchone()
        if employers:
            sic_code = ''
            sic_industry = ''
            if employers:
                if employers[2]:
                    sic_code = ''
                    cursor.execute(
                        'select code from hwseta_sic_master where name= %s', (employers[2], ))
                    sic_code_details = cursor.fetchone()
                    if sic_code_details:
                        sic_code = sic_code_details[0]
                    if sic_code:
                        sic_industry = sic_code + ' - ' + employers[2]
            cursor.execute(
                "select count(code), occupation from actual_training_fields where actual_wsp_id= %s group by occupation", (wsp_id,))
            ofo_ids = cursor.fetchall()
            for ofo_id in ofo_ids:
                #                 print "ofo_ids===", ofo_id
                african_male, african_female, african_dissabled, coloured_male, coloured_female, coloured_dissabled, indian_male, indian_female, indian_dissabled, white_male, white_female, white_dissabled, total_male, total_female, total_disabled = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                cursor.execute(
                    'select code, occupation, learner_province, city_id, population_group, gender, dissability from actual_training_fields where actual_wsp_id=%s and occupation=%s', (wsp_id, ofo_id[1]))
                actual_training_data = cursor.fetchall()
                for actual_training_tuple in actual_training_data:
                    # Province
                    print "actual_training_tuple==", actual_training_tuple
                    cursor.execute(
                        "select name from res_country_state where id=%s", (actual_training_tuple[2],))
                    province_name = cursor.fetchone()
                    if province_name is None:
                        pass
                    else:
                        province_name = province_name[0]
                    # print "province =========",province_name
                    # City
                    cursor.execute(
                        "select name from res_city where id=%s", (actual_training_tuple[3],))
                    city_name = cursor.fetchone()
                    if city_name is None:
                        pass
                    else:
                        city_name = city_name[0]
                    # print "Municipality =====",municipality_name
                    # Getting well formated data for printing OFO Code
                    cursor.execute(
                        "select name from ofo_code where id=%s", (actual_training_tuple[0],))
                    ofo_code = cursor.fetchone()
                    if ofo_code is None:
                        pass
                    else:
                        ofo_code = ofo_code[0]
                    # print "ofo_code =========",ofo_code

                    # Occupation
                    cursor.execute(
                        "select name from occupation_ofo where id=%s", (actual_training_tuple[2],))
                    occ_name = cursor.fetchone()
                    if occ_name is None:
                        pass
                    else:
                        occ_name = occ_name[0]
                    # print "occ_name =========",occ_name
                    ofo_occ = ''
                    if ofo_code and occ_name:
                        ofo_occ = ofo_code + ' - ' + occ_name
                    # Population Group
                    if actual_training_tuple[4] == 'african' and actual_training_tuple[5] == 'male':
                        african_male += 1
                    elif actual_training_tuple[4] == 'coloured' and actual_training_tuple[5] == 'male':
                        coloured_male += 1
                    elif actual_training_tuple[4] == 'indian' and actual_training_tuple[5] == 'male':
                        indian_male += 1
                    elif actual_training_tuple[4] == 'white' and actual_training_tuple[5] == 'male':
                        white_male += 1
                    elif actual_training_tuple[4] == 'african' and actual_training_tuple[5] == 'female':
                        african_female += 1
                    elif actual_training_tuple[4] == 'coloured' and actual_training_tuple[5] == 'female':
                        coloured_female += 1
                    elif actual_training_tuple[4] == 'indian' and actual_training_tuple[5] == 'female':
                        indian_female += 1
                    elif actual_training_tuple[4] == 'white' and actual_training_tuple[5] == 'female':
                        white_female += 1                    # Gender

                    # Gender
                    gender = ''
                    if actual_training_tuple[5] == 'male':
                        total_male += 1
                    elif actual_training_tuple[5] == 'female':
                        total_female += 1

                    # Disability
                    disability = ''
                    if actual_training_tuple[6] == 'yes':
                        total_disabled += 1
                    elif actual_training_tuple[4] == 'african' and actual_training_tuple[6] == 'yes':
                        african_dissabled += 1
                    elif actual_training_tuple[4] == 'coloured' and actual_training_tuple[6] == 'yes':
                        coloured_dissabled += 1
                    elif actual_training_tuple[4] == 'indian' and actual_training_tuple[6] == 'yes':
                        indian_dissabled += 1
                    elif actual_training_tuple[4] == 'white' and actual_training_tuple[6] == 'yes':
                        white_dissabled += 1

                wr.writerow(
                    [sdl_number[0], sdl_number[1], employers[1], sic_industry, province_name, city_name, ofo_occ, african_male, african_female, african_dissabled, coloured_male, coloured_female, coloured_dissabled, indian_male, indian_female, indian_dissabled, white_male, white_female, white_dissabled, total_male, total_female, total_disabled])

finally:
    pass
