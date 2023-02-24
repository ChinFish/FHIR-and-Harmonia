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
    pickle.dump(LinearR_model[0], open('%s' % (merged_output_path), 'wb'))

    # merged = {}
    # for key in weights[0].keys():
    #     merged[key] = sum([w[key] * f for w, f in zip(weights, factors)])
    #
    # logging.debug("weights: [%s]", weights)
    # logging.debug("merged: [%s]", merged)
    # logging.debug("merged_output_path: [%s]", merged_output_path)
    # torch.save(merged, merged_output_path)


'''For GAIN model'''
# if DorG == "D":
#     logging.debug("This is Discriminator!!")
#     discriminator = [tf.keras.models.load_model(m['path_D']) for m in models]
#     weights = [w.get_weights() for w in discriminator]
#     # logging.debug("D_Weights:", weights)
#     total_data_size = sum(m['size_D'] for m in models)
#     factors = [m['size_D'] / total_data_size for m in models]
#     # logging.debug('D_factors', factors)
#
# elif DorG == "G":
#     logging.debug("This is Generator!!")
#     generator = [tf.keras.models.load_model(m['path_G']) for m in models]
#     weights = [w.get_weights() for w in generator]
#     # logging.debug("G_Weights:", weights)
#     total_data_size = sum(m['size_G'] for m in models)
#     factors = [m['size_G'] / total_data_size for m in models]
#     # logging.debug('G_factors', factors)
#
# else:
#     logging.debug('Error!!DorG has problem!!')
#
# weights = np.array(weights)
#
# factors_weights = []
# for i in range(len(factors)):
#     factors_weights.append(np.array(weights[i]) * factors[i])
#
# factors_weights = np.array(factors_weights)
# merged = sum(factors_weights)
#
# if DorG == "D":
#     discriminator[0].set_weights(merged)
#     discriminator[0].save("%s" % (merged_output_path))
#
# elif DorG == "G":
#     generator[0].set_weights(merged)
#     generator[0].save("%s" % (merged_output_path))
#
# else:
#     logging.debug('Error!!Mode not D or G!!')
#
# logging.debug('merge creating...')

# calculate performance

# return metrics

# discriminator = tf.keras.models.load_model('./test_weights1.tar_D').get_weights()
# logging.debug('type:',type(discriminator))
# logging.debug('discriminator:',discriminator)
