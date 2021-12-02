from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np


class ColumnFilter(BaseEstimator, TransformerMixin):

    def __init__(self, columns=None):
        """

        :param columns: Columns to be dropped
        """
        if columns is None:
            columns = ['Item_Identifier']
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_tf = X.drop(columns=self.columns)
        X_tf['Item_Fat_Content'] = X['Item_Fat_Content'].apply(lambda x: 'low fat' if x in ['Regular', 'reg'] else 'regular')
        X_tf['Outlet_Size'] = X_tf['Outlet_Size'].apply(self.change_outlet_size)
        X_tf['Outlet_Identifier'] = X_tf['Outlet_Identifier'].apply(lambda x:int(x[-2:]))
        return X_tf

    def change_outlet_size(self, x):
        if x == 'Small':
            return 0
        elif x == 'Medium':
            return 1
        elif x == 'High':
            return 2
        else:
            return np.nan


class ToArrayTransformer(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.values


class SparseToMatrixTransformer(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.toarray()
