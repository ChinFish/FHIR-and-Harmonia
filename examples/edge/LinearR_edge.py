import logging
import numpy as np
import pandas as pd
import pickle

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def run(output, resume):
    '''Training'''
    # load the boston dataset
    data_url = "http://lib.stat.cmu.edu/datasets/boston"
    raw_df = pd.read_csv(data_url, sep="\s+", skiprows=22, header=None)
    data = np.hstack([raw_df.values[::2, :], raw_df.values[1::2, :2]])
    target = raw_df.values[1::2, 2]
    # defining feature matrix(X) and response vector(y)
    X = data
    y = target

    # splitting X and y into training and testing sets

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4,
                                                        random_state=1)

    # create linear regression object
    try:
        reg = pickle.load(open("%s" % (resume),'rb'))
        logging.info("Load resume success!")
    except Exception as err:
        reg = LinearRegression()
        logging.info("Load resume fails [%s]", err)

    # train the model using the training sets
    logging.info('LinearR model type:{}'.format(type(reg)))
    reg.fit(X_train, y_train)

    # regression coefficients
    # logging.info('Coefficients: ', reg.coef_)

    # variance score: 1 means perfect prediction
    # logging.info('Variance score: {}'.format(reg.score(X_test, y_test)))
    metrics = {'rscore': reg.score(X_test, y_test)}
    pickle.dump(reg, open('%s' % (output), 'wb'))
    return metrics
