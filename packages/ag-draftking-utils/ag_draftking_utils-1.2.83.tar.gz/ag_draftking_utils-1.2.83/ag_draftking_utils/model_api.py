import pickle
import datetime
import os
import lightgbm as lgb
import logging
import sys
from sklearn.model_selection import cross_val_predict, cross_val_score
from sklearn.metrics import mean_pinball_loss, make_scorer, r2_score, log_loss
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, LinearRegression
from smart_open import smart_open
import time
from collections import defaultdict
from .util import get_current_chicago_time


BUCKET_NAME = 'draft-kings-trained-models'
PATH_TO_CACHED_MODELS = f's3://{BUCKET_NAME}/2022_pickled_models'
PATH_TO_MODEL_METADATA = f's3://{BUCKET_NAME}/2022_model_metadata'

# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)


# Define the custom pinball loss scorer
def pinball_loss_scorer(y_true, y_pred, tau):
    return mean_pinball_loss(y_true, y_pred, alpha=tau)


class Model:

    def __init__(self, model_id, model_name, model_description, df, x_vars, y_var, training_data_file,
                 path_to_cached_model=PATH_TO_CACHED_MODELS, n_folds=5, clf=None, use_cloud=True,
                 qrm_percentile=-1):

        self.model_id = model_id
        self.model_name = model_name
        self.model_description = model_description
        self.df = df
        self.x_vars = x_vars
        self.y_var = y_var
        self.path_to_cached_model = path_to_cached_model
        self.n_folds = n_folds
        self.metric_value = None
        self.qrm_percentile = qrm_percentile
        self.model = self.get_model(clf)
        self.use_cloud = use_cloud
        self.training_data_file = training_data_file
        self.predictions = np.empty(0)

    def clean_input_df_before(self):
        """
        Make sure the indices are all 0 so the join on cross validation
        predictions is correct
        """
        self.df.reset_index(drop=True, inplace=True)

    @property
    def use_qrm(self):
        return self.qrm_percentile >= 0

    def create_model_cv_scores(self):
        s = time.time()
        
        # run cross-validation from scratch if not already done. 
        if self.predictions.shape[0] == 0:
            scoring_function = make_scorer(pinball_loss_scorer, greater_is_better=False, 
            tau=self.qrm_percentile) if self.qrm_percentile >= 0 else self.metric_name

            cv = cross_val_score(self.model, X=self.df[self.x_vars], y=self.df[self.y_var],
                             cv=self.n_folds, scoring=scoring_function)
            self.metric_value = cv.mean()
        # otherwise, leverage the already run predictions to do the scoring.
        else:
            if self.qrm_percentile >= 0:
                self.metric_value = pinball_loss_scorer(
                    self.df[self.y_var], self.predictions, tau=self.qrm_percentile)
            elif self.model_type == 'regression':
                self.metric_value = r2_score(self.df[self.y_var], self.predictions)
            elif self.model_type == 'classification':
                self.metric_value = log_loss(self.df[self.y_var], self.predictions)


        e = time.time()
        t = '{:.2f}'.format(e-s)
        logging.info(f'Done creating CV scores, took {t} seconds')

    def train_model(self):
        s = time.time()
        self.model.fit(self.df[self.x_vars], self.df[self.y_var])
        e = time.time()
        t = '{:.2f}'.format(e-s)
        logging.info(f'Done training full model, took {t} seconds')

    def cache_model(self):
        s = time.time()
        file = os.path.join(self.path_to_cached_model, str(self.model_id))
        with smart_open(file, 'wb') as f:
            pickle.dump(self.model, f)

        e = time.time()
        t = '{:.2f}'.format(e-s)
        logging.info(f'Saved model to {file}, took {t} seconds')

    def create_predictions(self, prediction_mode='cv'):
        """
        :param prediction_mode: str: either
            "cv" - cross-validated
            "actual" - not cross-validated
        :return: 1D array of predictions,
            actual values if regression, P(X=1) if classification
        """
        clf = self.model
        if prediction_mode == 'actual':
            if self.model_type == 'regression':
                return clf.predict(self.df[self.x_vars])
            elif self.model_type == 'classification':
                return clf.predict_proba(self.df[self.x_vars])[:, 1]
            else:
                raise Exception(f"model_type {self.model_type} unsupported")
        elif prediction_mode == 'cv':
            method = 'predict_proba' if self.model_type == 'classification' else 'predict'
            predictions = cross_val_predict(
                clf,
                X=self.df[self.x_vars],
                y=self.df[self.y_var],
                cv=self.n_folds,
                method=method
            )
            predictions = predictions[:, 1] if self.model_type == 'classification' else predictions
            self.predictions = predictions
            return predictions
        else:
            raise Exception(f"prediction mode {prediction_mode} unsupported")

    def create_cv_predictions_deprecated(self, clean_before_running=True):
        s = time.time()

        if clean_before_running:
            self.clean_input_df_before()

        method = 'predict_proba' if self.model_type == 'classification' else 'predict'
        predictions = cross_val_predict(
            self.model, 
            X=self.df[self.x_vars], 
            y=self.df[self.y_var],
            cv=self.n_folds, 
            method=method
        )
        self.model.fit(self.df[self.x_vars], self.df[self.y_var])
        if method == 'predict_proba':
            df = pd.DataFrame(predictions, columns=[f'Pred_{x}' for x in self.model.classes_])
        else:
            df = pd.DataFrame(predictions, columns=[f'Pred_{self.y_var}'])

        e = time.time()
        t = '{:.2f}'.format(e-s)
        logging.info(f'Done creating CV predictions, took {t} seconds')
        return self._join_with_original_df(df)

    def _join_with_original_df(self, prediction_df):
        return self.df.merge(prediction_df, left_index=True, right_index=True)

    def _get_training_data_stats(self):
        min_date = self.df['GAME_DATE'].min()
        max_date = self.df['GAME_DATE'].max()
        n = self.df.shape[0]
        return min_date, max_date, n

    @staticmethod
    def load_up_cached_model(model_id, model_path=PATH_TO_CACHED_MODELS):
        """
        Given a model id, return the pre-trained model
        """
        with smart_open(os.path.join(model_path, str(model_id)), 'rb') as f:
            clf = pickle.load(f)
        return clf

    @staticmethod
    def get_feature_importances(clf, fi_total_dict):
        """
        Takes in trained classifier, then outputs 
        a dictionary with key=feature name, value=feature importance
        """
        for feature_name, feature_importance in zip(clf.feature_name_, clf.feature_importances_):
            fi_total_dict[feature_name] += feature_importance

    @staticmethod
    def find_distinct_feature_importances(feature_importances, features_only=False):
        s = set()
        end = []
        for feature, feature_val in feature_importances:
            # feature name in format: trailing_10_{stat} (i.e. trailing_10_TS_PCT) 
            feature_name = '_'.join(feature.split('_')[2:])
            if feature_name in s:
                continue
            s.add(feature_name)
            end.append((feature, feature_val))

        if features_only:
            return [x[0] for x in end]
        else:
            return end

    def get_model_metrics(self):
        min_date, max_date, n = self._get_training_data_stats()
        df = pd.DataFrame({
            "model_id": [self.model_id],
            "model_name": [self.model_name],
            "model_description": [self.model_description],
            "train_start_date": [min_date],
            "train_end_date": [max_date],
            "n_observations": [n],
            "x_var_list": [_get_x_var_str(self.x_vars)],
            "y_var": [self.y_var],
            "metric_name": [self.metric_name],
            "metric_value": [self.metric_value],
            "model_type": [self.model_type],
            "n_folds": [self.n_folds],
            "path_to_cached_model": [self.path_to_cached_model],
            "created_date": [get_current_chicago_time()],
            "training_data_file": [self.training_data_file],
            "qrm_percentile": [self.qrm_percentile]
        })
        return df

    def save_model_metrics_to_db(self, conn):
        df = self.get_model_metrics()
        model_metadata_path = os.path.join(PATH_TO_MODEL_METADATA, str(self.model_id)+'.csv')

        # Make sure the model_id isn't already used
        try:
            with smart_open(model_metadata_path) as f:
                raise ValueError(f"model_id={self.model_id} already exists, use a unique model_id")
        except OSError:
            # if the file is not already saved, then save it
            df.to_csv(smart_open(model_metadata_path, 'w'), index=False)
            n_rows = df.shape[0]
            logging.info(f'Saved {n_rows} rows to {model_metadata_path}')

            # also save to DB
            df.to_sql('TrainingModelResults', conn, if_exists='append', index=False)

    @staticmethod
    def create_model_obj(model_id, df):
        """
        :param model_id: int: which specific model version
        :param df: full dataframe with X and Y variables
        :return: Model object
        """
        info = pd.read_csv(smart_open(os.path.join(PATH_TO_MODEL_METADATA, str(model_id)+'.csv'))).iloc[0]
        clf = Model.load_up_cached_model(model_id)

        x_vars = _split_x_var_str(info['x_var_list'])

        model = Model(
            model_id
            , info['model_name']
            , info['model_description']
            , df
            , x_vars
            , info['y_var']
            , info['path_to_cached_model']
            , n_folds=info['n_folds']
            , clf=clf
            , qrm_percentile=info.get('qrm_percentile', -1.0)
        )

        return model

    @property
    def model_type(self):
        d = {
            'LGBMClassifier': 'classification',
            'LGBMRegressor': 'regression',
            'LogisticRegression': 'classification',
            'LinearRegression': 'regression'
        }
        return d[self.model_name]

    def get_model(self, clf):

        if self.model_name == 'LGBMClassifier':
            self.metric_name = 'neg_log_loss'
            return lgb.LGBMClassifier() if not clf else clf

        elif self.model_name == 'LGBMRegressor':
            if self.use_qrm:
                self.metric_name = 'pinball_loss'
            else:
                self.metric_name = 'r2'
            return lgb.LGBMRegressor() if not clf else clf

        elif self.model_name == 'LogisticRegression':
            self.metric_name = 'neg_log_loss'
            return LogisticRegression() if not clf else clf

        elif self.model_name == 'LinearRegression':
            self.metric_name = 'r2'
            return LinearRegression() if not clf else clf

        else:
            raise Exception(f"model {self.model_name} not supported, only LGBMClassifier,"
                            "LGBMRegressor, LogisticRegression, and LinearRegression"
                            " supported")


def _get_x_var_str(string):
    return '|'.join(string)

def _split_x_var_str(string):
    return string.split('|')