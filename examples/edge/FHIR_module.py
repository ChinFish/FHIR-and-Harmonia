# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import json
import requests
import pandas as pd
from time import time
import os
import numpy as np
import sys
from sklearn.impute import SimpleImputer


def find_all_lab_test(fhir_url):
    '''
    This function will create all of lab test mapping loinc code
    :param fhir_url: which fhir server we need
    :return: a csv file, which contain lab test mapping with loinc code
    '''
    rstype = 'Observation'
    select_url = fhir_url + '/' + rstype
    patient_data = requests.get(url=select_url).json()
    for i in range(len(patient_data['entry'])):
        # print(len((patient_data['entry'])))
        # print(patient_data['entry'][i]['resource']['code']['coding'][0]['display'])

        status = 'next'
        record_dict = {}
        while status == 'next':
            for j in range(len(patient_data['entry'])):
                loinc_code = patient_data['entry'][j]['resource']['code']['coding'][0]['code']
                lab_test = patient_data['entry'][j]['resource']['code']['coding'][0]['display']
                record_dict[lab_test] = loinc_code
                # print(patient_data['entry'][j]['resource']['code']['coding'][0]['display'])
            # print(len(patient_data['entry']))

            status = patient_data['link'][1]['relation']
            next_link = patient_data['link'][1]['url']
            patient_data = requests.get(url=next_link).json()
            # print('next Bundle!!')
            # print(next_link)
    # print(record_dict)
    keys = record_dict.keys()
    values = record_dict.values()
    df = pd.DataFrame({"Lab test": keys, "Loinc code": values})
    # print(df)
    df.to_excel("ALL_lab_test_relation_with_loinc_code.xlsx")


def check_mapping_resource_type(resouce_type_mapping_codebook, hospital_mapping_codebook):
    '''
    This function will check whether hospital mapping to the resource type or not.
    :param resouce_type_mapping_codebook: File location. Store resource type mapping each hospital LOINC code codebook
    :param hospital_mapping_codebook: File location. Store hospital lab test mapping LOINC code
    :return: hospital mapping resource type or not
    '''
    # print('resource type mapping codebook:{}'.format(resouce_type_mapping_codebook))
    # print('Hospital mapping codebook:{}'.format(hospital_mapping_codebook))

    # hospital_loinc_code = hospital_mapping_codebook['LOINC code'].values
    hospital_lab_test = hospital_mapping_codebook['Lab test'].values
    target_lab_test = resouce_type_mapping_codebook['Lab test'].values
    complete_flag = True
    # print(hospital_loinc_code)
    # print(hospital_lab_test)
    # print(len(hospital_mapping_codebook['LOINC code']))
    for i in range(len(hospital_lab_test)):
        if hospital_lab_test[i] not in target_lab_test:
            complete_flag = False
            print('Lab Test:{} is not mapping in Resource Type'.format(
                hospital_lab_test[i]))
            print('Please add mapping')
    if complete_flag:
        print('Mapping relation is already finish!')
    return complete_flag


def create_big_table(fhir_url):
    '''
    This function will according to resource type mapping table,
    then get all patient ID from each LOINC code(lab test)
    :param fhir_url: which fhir server we need
    :return: a big table
    '''
    # Merge loinc code and lab test from the hospital
    mapping_data = pd.read_excel('resource type mapping codebook.xlsx')
    mapping_data = mapping_data.set_index('Lab test')
    # mapping_data = pd.read_csv('code_book.csv')
    loinc_code = pd.read_excel('predict fat codebook.xlsx')
    loinc_code = loinc_code.set_index('Lab test')
    mapping_data = pd.concat((mapping_data, loinc_code), axis=1, copy=False)
    # print(mapping_data.reset_index())
    mapping_data = mapping_data.reset_index()
    # print(set(loinc_code.index),set(mapping_data['Lab test']))
    drop_column = list(set(mapping_data['Lab test']).difference(set(loinc_code.index)))
    # print(drop_column)
    # print(mapping_data)
    for i in drop_column:
        mapping_data = mapping_data.drop(mapping_data[mapping_data['Lab test'] == i].index)
    print(mapping_data)

    df_big_table = pd.DataFrame()
    component = set()
    # Deal with no component part
    for i in range(len(mapping_data.axes[0])):
        patient_id = []
        lab_test_value = []
        big_table = {}
        lab_test = mapping_data.iloc[i]['Lab test']
        rstype = mapping_data.iloc[i]['Resource Type']
        loinc_code = mapping_data.iloc[i]['LOINC code']
        # loinc_code = mapping_data.iloc[i]['LOINC code']
        # print('lab test:{},Resource type:{},loinc_code:{}'.format(lab_test, rstype, loinc_code))
        select_url = fhir_url + '/' + rstype
        params = {'code': loinc_code}
        patient_data = requests.get(url=select_url, params=params).json()

        # check loinc code can be search
        # print(lab_test, loinc_code)
        if 'entry' not in patient_data:
            continue

        # search all the data in Bundle
        status = 'next'
        while status == 'next':
            for j in range(len(patient_data['entry'])):
                # print(patient_data['entry'][j]['resource']['code']['coding'][0]['display'])
                # print(patient_data['entry'][j]['resource']['code']['coding'][0]['code'])

                if 'component' not in patient_data['entry'][j]['resource']:
                    patient_id.append(
                        patient_data['entry'][j]['resource']['subject']['reference'][8:])
                    lab_test_value.append(
                        patient_data['entry'][j]['resource']['valueQuantity']['value'])
                else:
                    component.add(loinc_code)
                    if 'valueQuantity' in patient_data['entry'][j]['resource']:
                        patient_id.append(
                            patient_data['entry'][j]['resource']['subject']['reference'][8:])
                        lab_test_value.append(
                            patient_data['entry'][j]['resource']['valueQuantity']['value'])
            # print(len(patient_data['entry']))
            status = patient_data['link'][1]['relation']
            next_link = patient_data['link'][1]['url']
            patient_data = requests.get(url=next_link).json()

        big_table['Patient_ID'] = patient_id
        big_table[lab_test] = lab_test_value
        df_temp = pd.DataFrame(big_table)
        df_temp = df_temp.set_index('Patient_ID')

        df_big_table = pd.concat((df_big_table, df_temp), axis=1, copy=False)
        # print(df_big_table)
        # print('Big table test{}'.format(i+1))
    # df_big_table.to_csv('no_component_data.csv')
    # component = {'35094-2', '9269-2'}
    # print(component)

    # Deal with component part
    for code in component:
        lab_test_and_value = {}
        big_table = {}
        # print('code', code)
        rstype = 'Observation'
        select_url = fhir_url + '/' + rstype
        params = {'code': code}
        patient_data = requests.get(url=select_url, params=params).json()
        # print(patient_data)
        status = 'next'
        patient_id = []
        # lab_test_and_value[code] = []
        while status == 'next':
            for j in range(len(patient_data['entry'])):
                patient_id.append(
                    patient_data['entry'][j]['resource']['subject']['reference'][8:])
                for k in range(len(patient_data['entry'][j]['resource']['component'])):
                    lab_test = patient_data['entry'][j]['resource']['component'][k]['code']['coding'][0]['display']
                    lab_test_value = patient_data['entry'][j]['resource']['component'][k]['valueQuantity']['value']
                    if lab_test not in lab_test_and_value:
                        lab_test_and_value[lab_test] = []
                    lab_test_and_value[lab_test].append(lab_test_value)

                    # patient_id.append(patient_data['entry'][j]['resource']['subject']['reference'][8:])
                    # lab_test_value.append(patient_data['entry'][j]['resource']['valueQuantity']['value'])
            # print(len(patient_data['entry']))
            status = patient_data['link'][1]['relation']
            next_link = patient_data['link'][1]['url']
            patient_data = requests.get(url=next_link).json()

        big_table['Patient_ID'] = patient_id
        for lab_test in lab_test_and_value.keys():
            big_table[lab_test] = lab_test_and_value[lab_test]
        # print(big_table)
        df_temp = pd.DataFrame(big_table)
        df_temp = df_temp.set_index('Patient_ID')

        df_big_table = pd.concat((df_big_table, df_temp), axis=1, copy=False)
    # print(df_big_table)
    # print(list(df_big_table.columns))
    # Fill the empty column in mapping codebook
    empty_column = []
    # print(list(mapping_data['Lab test']))
    for lab_test in list(mapping_data['Lab test']):
        if lab_test not in list(df_big_table.columns):
            empty_column.append(lab_test)
    print('empty column:', empty_column)
    df_big_table[empty_column] = None
    df_big_table = df_big_table.sort_index(axis=1)
    print(df_big_table)

    print('Big table create successfully!!')
    # output big table become csv format
    df_big_table.to_csv('./data/Big_Table.csv')
    # df_big_table.to_csv('The big table.csv')


def prepocessing(big_table, features_missing_rate, big_table_drop_rate, mask_rate=0.2):
    # read the csv file and set the index
    big_table = pd.read_csv(big_table).set_index('Patient_ID')

    # count the number of missing values for each row
    missing_counts = big_table.isnull().sum(axis=1)
    # print('missing counts:', missing_counts)

    # calculate the missing rate and add it as a new column
    missing_rate = missing_counts / big_table.shape[1]
    big_table['missing_rate'] = missing_rate

    # find the features with a missing rate above the threshold and drop them
    drop_features = big_table.loc[big_table['missing_rate'] > features_missing_rate].index
    big_table.drop(drop_features, inplace=True)

    # print the percentage of dropped features
    dropped_features_count = len(drop_features)
    sample_count = big_table.shape[0]
    print(f"Samples dropped: {dropped_features_count / sample_count * 100:.2f}%")
    print('drop samples:{}'.format(list(drop_features)))

    # check if the table can be used
    if dropped_features_count / sample_count > big_table_drop_rate:
        print('This big table will not recommend be used!')
    else:
        print('This table can be used!')

    # print(big_table)

    # print('Column has None value:',list(big_table.loc[:,big_table.isnull().any()].columns))

    # preprocessing for model input
    big_table['BMI'] = big_table['Body weight'] / ((big_table['Body height'] / 100) * (big_table['Body height'] / 100))
    big_table = big_table.drop(['Body weight', 'Body height'], axis=1)
    big_table['label'] = [1 if bmi > 24 else 0 for bmi in big_table['BMI']]

    # Drop all Nan column
    big_table = big_table.dropna(axis=1, how='all')
    '''
    true_value = np.array(big_table['Adult Waist Circumference Protocol'])
    # put the Nan value to big table
    mask = np.random.rand(len(big_table)) < mask_rate
    big_table.loc[mask, 'Adult Waist Circumference Protocol'] = np.nan

    # output the missing big table
    big_table.to_csv('./data/Big_Table_missing.csv')

    missing_counts = big_table.isnull().sum(axis=0)
    # print(missing_counts['Adult Waist Circumference Protocol'] / len(big_table))

    # impute data
    imp = SimpleImputer(strategy='most_frequent')

    # 將補值後的結果存回 DataFrame
    big_table[['Adult Waist Circumference Protocol']] = imp.fit_transform(
        big_table[['Adult Waist Circumference Protocol']])
    imputed_value = np.array(big_table['Adult Waist Circumference Protocol'])
    # print('true value:{}, imputed value:{}'.format(true_value, imputed_value))
    # Calculate impute and true value difference

    diff_sum = np.abs(np.subtract(true_value, imputed_value)).mean()

    # diff_sum = np.subtract(true_value, imputed_value).sum()

    print('Difference:', diff_sum)
    '''

    # Drop Patient_ID, missing_rate, and BMI to become training dataset
    # big_table = big_table.reset_index(drop=True)
    big_table = big_table.drop(columns=['BMI', 'missing_rate'])
    big_table.to_csv('./data/Big_Table_processed.csv')
    print(big_table)


def test_web():
    import webbrowser
    urL = 'https://www.google.com.tw/'
    webbrowser.get('windows-default').open_new(urL)


if __name__ == '__main__':
    fhir_server_url = 'http://120.126.47.119:8002/fhir'

    # create_big_table(fhir_server_url)

    # find_all_lab_test(fhir_server_url)

    rstype_map_codebook = pd.read_excel('resource type mapping codebook.xlsx')
    hospital_map_codebook = pd.read_excel(
        'predict fat codebook.xlsx')
    time_check_map_start = time()
    # check the mapping relation
    check = check_mapping_resource_type(resouce_type_mapping_codebook=rstype_map_codebook,
                                        hospital_mapping_codebook=hospital_map_codebook)
    time_check_map_end = time()
    if not check:
        sys.exit()

    # test data exist function
    print(os.path.exists('data/Big_Table.csv') is False)
    # Already mapping and check big table is exist or not
    if os.path.exists('data/Big_Table.csv') is False and check:
        print('======Design big table======')
        if os.path.exists('data') is False:
            os.mkdir('data')

    start_time_create_big_table = time()
    # create big table!
    create_big_table(fhir_url=fhir_server_url)

    end_time_create_big_table = time()
    print('execute check map time:{}', format(
        time_check_map_end - time_check_map_start))
    print('execute big table time:{}', format(
        end_time_create_big_table - start_time_create_big_table))

    big_table_path = 'data/Big_Table.csv'
    # print(big_table_path)

    prepocessing(big_table=big_table_path, features_missing_rate=0.6, big_table_drop_rate=0.6)
    # test_web()
# # See PyCharm help at https://www.jetbrains.com/help/pycharm/
