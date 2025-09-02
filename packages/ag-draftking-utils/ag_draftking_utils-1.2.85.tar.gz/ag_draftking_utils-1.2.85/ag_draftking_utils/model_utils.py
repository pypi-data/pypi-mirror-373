import boto3
import smart_open
import lightgbm as lgb
import numpy as np


def fit_and_save_classification_model(df, model_obj, x_vars, y_var, expected_classes, save_path):
    """
    Fits a LightGBM object and saves the 
    1) Fitted Model 
    2) Feature Variable List
    3) Class Labels

    Inputs:
        df: pd.DataFrame: training data
        model_obj: i.e. a LightGBM object 
        x_vars: List[str] - feature variables you want to train on 
        y_var: str - groundtruth column 
        expected_classes: List[any] - All the classes that you expect to see. If the model
            doesnt train on one of this class, or trains on something unexpected, an Exception
            will be raised. 
        save_path: str - where you want to save the models
    """
    model_obj.fit(df[x_vars], df[y_var])
    for outcome in model_obj.classes_:
        if outcome not in expected_classes:
            raise Exception(f'Got unexpected class {outcome}.')
    for outcome in expected_classes:
        if outcome not in model_obj.classes_:
            classes_string = ', '.join(list(model_obj.classes_))
            raise Exception(f'Expected to get class {outcome}, but wasnt present in the data. '
                            f'Only classes: {classes_string} were found.')

    if save_path.startswith('s3://'):
        local_model_path = "/tmp/model.txt"
        model_obj.booster_.save_model(local_model_path)
        s3 = boto3.client('s3')
        bucket_name = save_path[5:].split('/')[0]
        key = '/'.join(save_path[5:].split('/')[1:])
        s3.upload_file(local_model_path, bucket_name, key+'/model.txt')
    else:
        model_obj.booster_.save_model(f'{save_path}/model.txt')

    with smart_open.smart_open(f'{save_path}/features.txt', 'w') as f:
        f.write('\n'.join(model_obj.feature_name_))
    with smart_open.smart_open(f'{save_path}/class_labels.txt', 'w') as f:
        f.write('\n'.join([str(x) for x in model_obj.classes_]))
    print(f'Done training model, saved to folder: {save_path}.')


class PatchedLGBMClassifier(lgb.LGBMClassifier):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._classes_patch = None
        self._feature_name_patch = None

    # The following allow for calling the "classes_" or "feature_name_" attributes.
    @property
    def classes_(self):
        return self._classes_patch

    @classes_.setter
    def classes_(self, value):
        self._classes_patch = value

    @property
    def feature_name_(self):
        return self._feature_name_patch

    @feature_name_.setter
    def feature_name_(self, value):
        self._feature_name_patch = value


def load_lgbm_classifier_from_s3(prefix: str) -> lgb.LGBMClassifier:
    """
    prefix: 's3://bucket/folder/...'  (no trailing slash needed)
    Assumes the folder contains model.txt, features.txt, class_labels.txt
    """
    import smart_open
    # --- 1. read model.txt into memory --------------------------------------
    with smart_open.open(f"{prefix.rstrip('/')}/model.txt", "r") as f:
        model_txt = f.read()

    booster = lgb.Booster(model_str=model_txt)          # load from string
    clf = PatchedLGBMClassifier()
    clf._Booster = booster
    clf.fitted_ = True                                   # fool sklearn

    # --- 2. restore classes_ -------------------------------------------------
    with smart_open.open(f"{prefix.rstrip('/')}/class_labels.txt", "r") as f:
        classes = [eval(line.strip()) for line in f]     # works for str / int
    clf.classes_ = np.array(classes)
    print(clf.classes_)

    # 3. Load feature names
    with smart_open.open(f"{prefix.rstrip('/')}/features.txt", "r") as f:
        feature_names = [line.strip() for line in f]
    clf.feature_name_ = feature_names
    clf.n_features_in_ = len(feature_names)
    return clf