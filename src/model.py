from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import RobustScaler
import math
import pandas as pd

def ML_model(df_merged, numerical):
    # X -> Numerical predictors 
    # y -> gross, numerical response 
    X, y = df_merged[numerical].loc[:, df_merged[numerical].columns != 'gross'], df_merged['gross']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=13)

    # Fitting the robust scaler transform on the train set
    rs1 = RobustScaler().fit(X_train)
    rs2 = RobustScaler().fit(y_train.values.reshape(-1,1))

    # Transforming both train and test sets
    X_train = pd.DataFrame(rs1.transform(X_train.values), index=X_train.index, columns=X_train.columns)
    y_train = pd.DataFrame(rs2.transform(y_train.values.reshape(-1,1)), index=y_train.index, columns=['gross'])

    X_test = pd.DataFrame(rs1.transform(X_test), index=X_test.index, columns=X_test.columns)
    y_test = pd.DataFrame(rs2.transform(y_test.values.reshape(-1,1)), index=y_test.index, columns=['gross'])
    cat_tomerge = df_merged[df_merged.columns[~df_merged.columns.isin(numerical)]]

    X_train = pd.merge(X_train, cat_tomerge, left_index=True, right_index=True)
    X_test = pd.merge(X_test, cat_tomerge, left_index=True, right_index=True)

    # Gradient Boosting Regressor model
    model = GradientBoostingRegressor(random_state=0)
    model.fit(X_train.values, y_train.values)

    # Predict Gross from our predictor features
    y_train_pred = model.predict(X_train.values)
    y_test_pred = model.predict(X_test.values)

    train_rmse = math.sqrt(mean_squared_error(y_train.values, y_train_pred))
    train_r2 = model.score(X_train.values, y_train.values)
    test_rmse = math.sqrt(mean_squared_error(y_test.values, y_test_pred))
    test_r2 = model.score(X_test.values, y_test.values)

    ## feature importance
    importances = list(model.feature_importances_)
    attr_importances = [(attr, round(importance, 3)) for attr, importance in zip(X_test.columns, importances)]
    # Sort the feature importances by most important first
    attr_importances = sorted(attr_importances, key = lambda x: x[1], reverse = True)
    sel_features = pd.DataFrame(attr_importances[:5], columns=['Features','Importance'])
    # print(sel_features.Features.values)

    X_train = X_train[['num_voted_users', 'budget', 'num_critic_for_reviews', 'Family', 'imdb_score']]
    X_test = X_test[['num_voted_users', 'budget', 'num_critic_for_reviews', 'Family', 'imdb_score']]

    model2=GradientBoostingRegressor(random_state=0)
    model2.fit(X_train.values, y_train.values)

    return model2, y_train, y_test, y_train_pred, y_test_pred, train_rmse, train_r2, test_rmse, test_r2