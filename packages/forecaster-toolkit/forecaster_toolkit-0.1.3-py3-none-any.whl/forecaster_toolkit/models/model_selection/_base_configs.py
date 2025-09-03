BASE_PARAM_GRID = {
    "RandomForestModel": {
        "n_estimators": [100, 200, 300],
        "max_depth": [5, 10, 20],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4],
    },
    "CatBoostModel": {
        "n_estimators": [100, 200, 300],
        "max_depth": [2, 5, 7],
    },
    "XGBoostModel": {
        "n_estimators": [100, 200, 300],
        "max_depth": [5, 10, 20],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4],
    },
}
