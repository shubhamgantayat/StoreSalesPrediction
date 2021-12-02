from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from transformers.custom_transformers import ToArrayTransformer, ColumnFilter, SparseToMatrixTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder


class CustomPipeline:
    """
    This class contains custom pipelines used for data preprocessing.
    """

    @staticmethod
    def column_pipeline():
        """

        :return: Columns Transformer
        """
        cat_attributes = ['Item_Type', 'Outlet_Location_Type', 'Outlet_Type', 'Item_Fat_Content']
        num_attributes = ['Item_Weight', 'Item_Visibility', 'Item_MRP']
        cat_attributes_2 = ['Outlet_Size', 'Outlet_Identifier']
        col_tf = ColumnTransformer([
            ("standard_scaler", StandardScaler(), num_attributes),
            ("one_hot", OneHotEncoder(), cat_attributes),
            ("to_array", ToArrayTransformer(), cat_attributes_2)
        ])
        return col_tf

    @staticmethod
    def total_pipeline(n_neighbors=3):
        """

        :param n_neighbors: n_neighbors is a parameter for knn imputer
        :return: pipeline
        """
        pipeline = Pipeline([
            ("col_filter", ColumnFilter()),
            ("col_transformer", CustomPipeline().column_pipeline()),
            # ("sparse", SparseToMatrixTransformer()),
            ('knn_imputer', KNNImputer(n_neighbors=n_neighbors))
        ])
        return pipeline
