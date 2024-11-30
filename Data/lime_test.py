import numpy as np
import pandas as pd
from importlib import *

from lime import lime_tabular

dataset = pd.read_csv('Churn_Modelling.csv')
X = dataset.iloc[:, 3:13]
y = dataset.iloc[:, 13]

geography = pd.get_dummies(X["Geography"], drop_first=True)
gender = pd.get_dummies(X['Gender'], drop_first=True)

X = pd.concat([X, geography, gender], axis=1)

X = X.drop(['Geography', 'Gender'], axis=1)

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

from sklearn.ensemble import RandomForestClassifier
classifier = RandomForestClassifier()
classifier.fit(X_train, y_train)

import pickle
pickle.dump(classifier, open("classifier.pkl", 'wb'))

interpretor = lime_tabular.LimeTabularExplainer(
    training_data=np.array(X_train),
    feature_names=X_train.columns,
    mode='classification'
)

print(X_test.iloc[5])

exp = interpretor.explain_instance(
    data_row=X_test.iloc[5], 
    predict_fn=classifier.predict_proba
)

sorted_local = interpretor.sorted_local
print(sorted_local)

exp.save_to_file('lime_explanation.html')
