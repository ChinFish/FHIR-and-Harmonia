import logging
import numpy as np
import pandas as pd
import pickle

from sklearn import linear_model
from sklearn.model_selection import train_test_split


def run(output, resume):
    ''' model Training'''
    data = pd.read_csv('data/Big_Table_processed.csv')
    X = data.iloc[:, 0:-1]
    X = X.drop(columns=['Patient_ID'])
    Y = data.iloc[:, -1]
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=1)

    # Create check array
    hospital_map_codebook = pd.read_excel(
        'predict fat codebook.xlsx')
    lab_test = list(hospital_map_codebook['Lab test'])
    remove = ['Body weight', 'Body height']
    lab_test = [elem for elem in lab_test if elem not in remove]
    lab_test.sort()
    features = list(X.columns)
    check_array = [1 if x in features else 0 for x in lab_test]
    df_check_array = pd.DataFrame(check_array)

    logging.info('check array:{}'.format(check_array))

    # create model object
    try:
        logistic = pickle.load(open("%s" % resume, 'rb'))
        logging.info("Load resume success!")
    except Exception as err:
        logistic = linear_model.LogisticRegression()
        logistic.fit(X_train, y_train)
        logging.info("Load resume fails [%s]", err)

    # train the model using the training sets
    # logging.info('LinearR model type:{}'.format(type(logistic)))

    # regression coefficients
    # logging.info('Coefficients: ', reg.coef_)

    # variance score: 1 means perfect prediction
    # logging.info('Variance score: {}'.format(reg.score(X_test, y_test)))
    metrics = {'accuracy': logistic.score(X_test, y_test)}
    pickle.dump(logistic, open('%s' % output, 'wb'))
    # df_check_array.to_csv('check_array.csv')
    return metrics, check_array
