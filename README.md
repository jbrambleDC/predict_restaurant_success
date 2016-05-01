predict_restaurant_success
==============================

Uses Yelp Academic dataset, and census data, to predict restaurant success

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org

### Data
running `make all` will utilize the hive scripts in the `src/data` directory to build the databases in hive. There may be a few
other Hive scripts you may want to run inside of `src/data`. @nhauke has prepared most of these hive scripts and the
corresponding Makefile

### Modeling
@jbrambleDC has created two python scripts than can be ran in ipyspark, or pyspark to train SVMs and crossvalidate them. The
resulying model performs quite poorly. After cutting down on feature selection and taking the mean success_metric by zipcode,
@arifyali trained a regression model found in `src/models/regression.py` that performs much  better. 

### Visualization
All Visualization outputs can be found in `reports/figures/` These contain a scatter plot of all success_metrics at restaurants
plotted vs the housing cost per sq. ft. in that zipcode as of February 2016. Another scatter plot illustrates the success_metric
per zipcode vs housing cost per sq. ft. 
