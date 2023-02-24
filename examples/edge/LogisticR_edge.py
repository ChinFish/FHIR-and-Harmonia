import logging
import numpy as np
import pandas as pd
import pickle

from sklearn import linear_model
from sklearn.model_selection import train_test_split


def run(output, resume):
    '''Training'''
    data_url = "data/Fhir_server_All_data.xlsx"
    data = pd.read_excel(data_url)
    data = data[['Body height','Body weight','Urate [Mass/volume] in Serum or Plasma','Triglyceride [Mass/volume] in Serum or Plasma --fasting',
        'Percentage of body fat Measured','Adult Waist Circumference Protocol']]

    data['BMI'] = data['Body weight'] / ((data['Body height']/100)*(data['Body height']/100))
    data = data.drop(['Body weight','Body height'],axis=1)
    data['label'] = [1 if bmi>24 else 0 for bmi in data['BMI']]
    X = data.iloc[:,0:-1]
    X = X.drop(['BMI'],axis=1)
    Y = data.iloc[:,-1]
    
    # logistic.fit(X,Y)
    X_train,X_test,y_train,y_test=train_test_split(X,Y,test_size=0.3,random_state=1)
    
    # logistic.predict(X_test)
    # print(logistic.score(X_test,y_test))


    # create linear regression object
    try:
        logistic = pickle.load(open("%s" % (resume),'rb'))
        logging.info("Load resume success!")
    except Exception as err:
        logistic = linear_model.LogisticRegression()
        # logistic = linear_model.SGDClassifier(max_iter=100000,shuffle=False,loss='log')
        logistic.fit(X_train,y_train)
        logging.info("Load resume fails [%s]", err)

    # train the model using the training sets
    logging.info('LinearR model type:{}'.format(type(logistic)))
    

    # regression coefficients
    # logging.info('Coefficients: ', reg.coef_)

    # variance score: 1 means perfect prediction
    # logging.info('Variance score: {}'.format(reg.score(X_test, y_test)))
    metrics = {'accuracy': logistic.score(X_test,y_test)}
    pickle.dump(logistic, open('%s' % (output), 'wb'))
    return metrics
