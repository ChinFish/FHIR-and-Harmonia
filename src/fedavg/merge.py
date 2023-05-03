# import torch
import logging
# import tensorflow as tf
import numpy as np
import pickle


def merge(models, merged_output_path):
    '''
    :param models: model path, datasize, and check array
    :param merged_output_path: which path to output
    :return: This function will return non-zero weights and dot check_array
    '''
    '''For LinearR model'''
    logging.info("Start aggregator!")

    LinearR_model = [pickle.load(open(m['path'], 'rb')) for m in models]
    coef = [m.coef_ for m in LinearR_model]
    intercept = [m.intercept_ for m in LinearR_model]
    total_data_size = sum(m['size'] for m in models)
    factors = [m['size'] / total_data_size for m in models]
    check_array = [m['check_array'] / total_data_size for m in models]
    logging.info('check array:{}'.format(check_array))

    check_array = np.array(check_array)
    logging.info('numpy check array:{}'.format(check_array))

    # deal with coef shape problem
    shaped_coef = []

    for i in range(len(check_array)):
        new_coef = []
        count = 0
        for j in check_array[i]:
            if j == 1:
                new_coef.append(coef[i][count])
                count = count + 1
            else:
                new_coef.append(0)
        shaped_coef.append(new_coef)
    shaped_coef = np.array(shaped_coef)
    logging.info('經過shape處理的coef:{}'.format(shaped_coef))

    factors_coef = []
    factors_intercept = []
    for i in range(len(factors)):
        factors_coef.append(np.array(shaped_coef[i]) * factors[i])
        factors_intercept.append(np.array(intercept[i]) * factors[i])

    # This line may cause problem
    factors_coef = np.array(factors_coef)
    factors_intercpet = np.array(factors_intercept)

    merged_coef = sum(factors_coef)
    dot_check_array = np.prod(check_array, axis=0)
    dot_coef = dot_check_array * merged_coef
    merged_coef = merged_coef[dot_coef != 0]

    merged_intercpet = sum(factors_intercpet)

    logging.info(merged_coef)
    logging.info(merged_intercpet)

    # LinearR_model[0].coef_ = merged_coef
    LinearR_model[0].coef_ = merged_coef
    LinearR_model[0].intercept_ = merged_intercpet
    pickle.dump(LinearR_model[0], open('%s' % merged_output_path, 'wb'))

    coef_path = merged_output_path.replace('/model.sav', '')
    coef_path = coef_path + '/' + 'check_array.csv'
    logging.info('check array path:{}'.format(coef_path))
    dot_coef.to_csv(dot_check_array)
    logging.info('Merge Successful!')
    # coef_path = merged_output_path.replace('/model.sav', '')
    # coef_path = coef_path + '/' + 'coef.csv'
    # logging.info('coef path:{}'.format(coef_path))
    # dot_coef.to_csv(coef_path)
    #
    # intercept_path = merged_output_path.replace('/model.sav', '')
    # intercept_path = intercept_path + '/' + 'intercept.csv'
    # logging.info('coef path:{}'.format(intercept_path))
    # merged_intercpet.to_csv(intercept_path)
