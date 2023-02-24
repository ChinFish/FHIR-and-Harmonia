# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import json
import requests
import pandas as pd
import numpy as np
from time import time
import os
import logging


def check_mapping_resource_type(resouce_type_mapping_codebook, hospital_mapping_codebook):
    '''
    This function will check whether hospital mapping to the resource type or not.
    :param resouce_type_mapping_codebook: File location. Store resource type mapping each hospital LOINC code codebook
    :param hospital_mapping_codebook: File location. Store hospital lab test mapping LOINC code
    :return: hospital mapping resource type or not
    '''
    hospital_name = 'LOINC code test hospital'
    # print('resource type mapping codebook:{}'.format(resouce_type_mapping_codebook))
    # print('Hospital mapping codebook:{}'.format(hospital_mapping_codebook))
    hospital_loinc_code = hospital_mapping_codebook['LOINC code'].values
    hospital_lab_test = hospital_mapping_codebook['Lab test'].values
    target_loinc_code = resouce_type_mapping_codebook[hospital_name].values
    complete_flag = True
    # print(hospital_loinc_code)
    # print(hospital_lab_test)
    # print(len(hospital_mapping_codebook['LOINC code']))
    for i in range(len(hospital_mapping_codebook['LOINC code'])):
        if hospital_mapping_codebook['LOINC code'][i] not in target_loinc_code:
            complete_flag = False
            logging.info('LOINC code:{} is not mapping in Lab test:{}'.format(hospital_loinc_code[i], hospital_lab_test[i]))
            logging.info('Please add mapping')
    if complete_flag:
        logging.info('Mapping relation is already finish!')
    return complete_flag


def create_big_table(fhir_url):
    '''
    This function will according to resource type mapping table,
    then get all patient ID from each LOINC code(lab test)
    :param fhir_url: which fhir server we need
    :return: a big table
    '''
    mapping_data = pd.read_excel('resource type mapping codebook.xlsx')

    df_big_table = pd.DataFrame()
    # print(df_big_table)
    for i in range(len(mapping_data.axes[0])):
        patient_id = []
        lab_test_value = []
        big_table = {}
        lab_test = mapping_data.iloc[i]['Lab test']
        rstype = mapping_data.iloc[i]['Resource Type']
        loinc_code = mapping_data.iloc[i]['LOINC code test hospital']
        # print('lab test:{},Resource type:{},loinc_code:{}'.format(lab_test, rstype, loinc_code))
        select_url = fhir_url + '/' + rstype
        params = {'code': loinc_code}
        patient_data = requests.get(url=select_url, params=params).json()

        # Handle Bundle type data
        # search all the data in Bundle
        status = 'next'
        while status == 'next':
            for j in range(len(patient_data['entry'])):
                patient_id.append(patient_data['entry'][j]['resource']['subject']['reference'][8:])
                lab_test_value.append(patient_data['entry'][j]['resource']['valueQuantity']['value'])
            # print(len(patient_data['entry']))
            status = patient_data['link'][1]['relation']
            next_link = patient_data['link'][1]['url']
            patient_data = requests.get(url=next_link).json()

        # print('Patient ID:{}'.format(patient_data['entry'][j]['resource']['subject']['reference'][8:]))
        # print('lab test is {} value is {}'.format(
        #     lab_test,
        #     patient_data['entry'][j]['resource']['valueQuantity']['value']))

        # print('Patient ID:{}'.format(patient_id))
        # print('lab test : {}'.format(lab_test_value))

        big_table['Patient_ID'] = patient_id
        big_table[lab_test] = lab_test_value
        df_temp = pd.DataFrame(big_table)
        df_temp = df_temp.set_index('Patient_ID')

        df_big_table = pd.concat((df_big_table, df_temp), axis=1, copy=False)
        # print(df_big_table)
        # print('Big table test{}'.format(i+1))
    # print(df_big_table)
    logging.info('Big table create successfully!!')
    # output big table become csv format
    df_big_table.to_csv('./data/Big_Table.csv')


def run():
    fhir_server_url = 'http://120.126.47.119:8002/fhir'

    rstype_map_codebook = pd.read_excel('resource type mapping codebook.xlsx')
    hospital_map_codebook = pd.read_excel('Hospital mapping codebook(example).xlsx')
    time_check_map_start = time()
    check = check_mapping_resource_type(resouce_type_mapping_codebook=rstype_map_codebook,
                                        hospital_mapping_codebook=hospital_map_codebook)
    time_check_map_end = time()

    '''test data exist function'''
    logging.info(os.path.exists('data/Big_Table.csv') is False)
    # Already mapping and check big table is exist or not
    if os.path.exists('data/Big_Table.csv') is False and check:
        logging.info('======Design big table======')
        if os.path.exists('data') is False:
            os.mkdir('data')
        start_time_create_big_table = time()
        create_big_table(fhir_url=fhir_server_url)
        end_time_create_big_table = time()
    # print('execute check map time:{}', format(time_check_map_end - time_check_map_start))
    # print('execute big table time:{}', format(end_time_create_big_table - start_time_create_big_table))
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
