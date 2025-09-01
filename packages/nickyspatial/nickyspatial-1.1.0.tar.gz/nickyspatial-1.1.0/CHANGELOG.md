## v1.1.0 (2025-08-31)

### Feat

- add cnn in test app and update notebook
- add dynamic hidden layers confing for CNN both in UI and package
- add hidden layer configs, use_batch_norms and dense_units params and make the cnn model creation dynamic
- view Training Patch Extraction counts in CNN model
- add early_stooping_patience as an input in UI and update notebook
- implement deep learning based classigication in streamlit UI
- implement EarlyStopping, ReduceLROnPlateau in CNN model
- add model evaluation function in CNN model
- add  function to visualize models history, train and val accuracy and loss
- added notebook for CNN implemenattion
- pass and read all params from classifier_params
- add CNN based classification Class

## v1.0.0 (2025-08-01)

### Fix

- **naming**: changes resolution in segmentation to avoid potential
- update Binder link and Python version in example notebook
- **ci**: fixes ci to push pypi and then updates the URL
- remove redundant --no-group option in dependency installation

## v0.2.0 (2025-05-15)

### Feat

- add plot_sample function and updae example usecase
- display OOB score after classification, streamlit: revised UI

### Fix

- merge issue
- error in interactive map for sample collection  in google collab
- **Dockerfile**: change exposed port from 8501 to 8080
- merge issue

## v0.1.1 (2025-05-10)

### Fix

- **ci**: fixes doc build

## v0.1.0 (2025-05-10)

### Feat

- add classes legend in select_sample window
- restructured UI content by replacing add the tabs into add process format
- add encloded_by operation in frontend and make the rule_based refinement dynamix
- merge region fronted wip
- RF implementation (sample collection and classification) done in frontend
- supervised classification using Random Forest backend complete

### Fix

- all pre_commit issue
- pre-commit issue
- key error

## v0.0.9 (2025-04-05)

### Fix

- **ui**: fixes ui , adds streamlit

### Refactor

- **ruff**: refact accordingly ruff formatting

### Perf

- **rules**: adds get ruleset method

## v0.0.8 (2025-04-05)

### Fix

- **raster**: fixes bug when category is string and map it to int in rasterio

## v0.0.7 (2025-04-05)

### Fix

- **docs**: fixes documentation bug

## v0.0.6 (2025-04-05)

### Fix

- **ci**: precommit
- **ci**: adds precommitci and fixes to publish

## v0.0.5 (2025-04-05)

### Fix

- **documentation**: fixes broken link in example

## v0.0.4 (2025-04-05)

### Fix

- **compactness**: fixes compactness as it is in slic
- **ci**: uv installation bug on mkdocs build fix
- **data**: fixes data sample renaming
- **test**: add temp workaround to debug later for test cases

## v0.0.3 (2025-04-04)

### Fix

- **docs**: adds fixes to missing broken links

## "v0.0.2" (2025-04-04)

### Refactor

- **test**: adds test scripts
