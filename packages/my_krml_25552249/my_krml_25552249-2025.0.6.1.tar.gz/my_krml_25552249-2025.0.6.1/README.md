# my_krml_25552249

My Python package for **data preparation, feature engineering, and model evaluation**.

## Package Structure

```bash
my_krml_25552249/
│
├── data/
│   └── sets.py          # pop_target, split_sets_random, split_sets_by_time, save_sets, load_sets
│
├── features/
│   ├── impute.py        # impute_missing
│   └── dates.py         # convert_to_date
│
├── models/
│   └── performance.py   # metrics, confusion matrix, plots, cross-val, etc.
```

## Installation

```bash
$ pip install my_krml_25552249
```

## Usage

This package is organized into **data handling, feature engineering, and model evaluation** modules.  You can import the relevant module depending on your task, and each module provides simple utility functions to help you **prepare your data, engineer features, evaluate models, and visualise results**.  

Below are some basic examples to get you started.

### Data Handling
```python
from my_krml_25552249.data.sets import pop_target, split_sets_random

# Example: split features and target
X, y = pop_target(df, "target")
X_train, y_train, X_val, y_val, X_test, y_test = split_sets_random(X, y)
```

### Feature Engineering
```python
from my_krml_25552249.features import impute_missing
from my_krml_25552249.features.dates import convert_to_date

# Example: impute missing values
df["column"] = impute_missing(df["column"], strategy="median")

# Example: convert columns to datetime
df = convert_to_date(df, cols=["date_column"])
```

### Model Evaluation
```python
from my_krml_25552249.models.performance import print_regressor_scores

# Example: print regression metrics
print_regressor_scores(y_preds, y_true, set_name="Test")
```

### Visualisation
```python
from my_krml_25552249.models.performance import plot_confusion_matrix

# Example: plot confusion matrix of a model
plot_confusion_matrix(model, X_train, y_train, title="Training Confusion Matrix")
```

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`my_krml_25552249` was created by Shawya. It is licensed under the terms of the MIT license.

## Credits

`my_krml_25552249` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
