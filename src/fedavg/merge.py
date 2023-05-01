# import torch
import logging
# import tensorflow as tf
import numpy as np
import pickle


def merge(models, merged_output_path):
    '''For LinearR model'''
    logging.info("Start aggregator!")

    LinearR_model = [pickle.load(open(m['path'], 'rb')) for m in models]
    coef = [m.coef_ for m in LinearR_model]
    intercept = [m.intercept_ for m in LinearR_model]
    total_data_size = sum(m['size'] for m in models)
    factors = [m['size'] / total_data_size for m in models]

    factors_coef = []
    factors_intercept = []
    for i in range(len(factors)):
        factors_coef.append(np.array(coef[i]) * factors[i])
        factors_intercept.append(np.array(intercept[i]) * factors[i])

    factors_coef = np.array(factors_coef)
    factors_intercpet = np.array(factors_intercept)

    merged_coef = sum(factors_coef)
    merged_intercpet = sum(factors_intercpet)

    logging.info(merged_coef)
    logging.info(merged_intercpet)

    LinearR_model[0].coef_ = merged_coef
    LinearR_model[0].intercept_ = merged_intercpet
    pickle.dump(LinearR_model[0], open('%s' % merged_output_path, 'wb'))
