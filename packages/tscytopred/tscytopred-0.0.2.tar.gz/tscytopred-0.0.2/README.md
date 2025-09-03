# TSCytoPred: Inferring time-series cytokine expression for transcriptomics data based on deep learning

Cytokines play a crucial role in immune system regulation, mediating responses from pathogen defense to tissue-damaging inflammation. Excessive cytokine production is implicated in severe conditions such as cancer progression, hemophagocytic lymphohistiocytosis, and severe cases of Coronavirus disease-19 (COVID-19). Studies have shown that cytokine expression profiles serve as biomarkers for disease severity and mortality prediction, with machine learning (ML) methods increasingly employed for predictive analysis. To improve patient outcome predictions, treatment adaptation, and survival rates, longitudinal analysis of cytokine profiles is essential. Time-series cytokine profiling has been linked to tumor response, overall survival in various cancers, and acute encephalopathy. Similarly, COVID-19 severity and patient outcomes correlate with cytokine expression dynamics over time. However, challenges remain due to the limited availability of time-series cytokine data, restricting broader experimental applications and robust predictive modeling. Recent advancements indicate that cytokine expression can be computationally inferred using gene expression data and transcription factor interactions. Inferring cytokine levels from existing gene expression datasets could enhance early disease detection and treatment response predictions while reducing profiling costs. 

This work proposes TSCytoPred, a deep learning-based model trained on time-series gene expression data to infer cytokine expression trajectories. TSCytoPred identifies genes relevant for predicting target cytokines through interaction relationships and high correlation. These identified genes are subsequently utilized in a neural network incorporating an interpolation block to estimate cytokine expression trajectories between observed time points. Performance evaluations using a COVID-19 dataset demonstrate that TSCytoPred significantly outperforms baseline regression methods, achieving the highest $R^2$ and the lowest mean absolute error. Furthermore, the proposed model enhances predicted severity outcomes for COVID-19 patients by inferring missing longitudinal data. TSCytoPred can be applied to datasets with a small number of time points and is compatible with longitudinal datasets containing irregular time gaps.

## Requirements
* Python (>= 3.6)
* Pytorch (>= v1.6.0)
* Other python packages : numpy, pandas, os, sys, scikit-learn

## Usage
Clone the repository or download source code files.

## Inputs
[Note!] All the example datasets can be found in './example/' directory.

#### Time-series/Longitudinal Gene expression profiles (Both training/testing)
* Contains gene expression profiles for each timepoint per patient
* Row : Timepoint (Sample), Column : Feature (Gene)
* The dataset should contain two columns named **"sample_id"** and **"timepoint"**, where, "sample_id" corresponds to the id of each patient, and "timepoint" should have timepoint information, where each timepoint needs to be denoted as the format of "%Y-%m-%d" (e.g., 2021-08-03).
* Dataset should be in sequential order of timepoint and the patients. For example, if per patient has three timepoints, then, it should be ordered in "patient01_timepoint_1,patient01_timepoint_2,patient01_timepoint_3,patient02_timepoint_1,patient02_timepoint_,...".
* File name should be "train_gene_expression.csv" and "test_gene_expression.csv"
* Example : ./example/train_gene_expression.csv

#### Time-series/Longitudinal Cytokine expression profiles (Training)
* Contains cytokine expression profiles for each timepoint per patient
* Row : Timepoint (Sample), Column : Feature (Cytokine)
* The dataset should contain two columns named **"sample_id"** and **"timepoint"**, same as gene expression file.
* Dataset should be in sequential order of timepoint and the patients, same as gene expression file.
* File name should be "train_cytokine_expression.csv"
* Example : ./example/train_cytokine_expression.csv

## How to run
1. Edit the **run_TSCytoPred.sh** to make sure each variable indicate the corresponding files.
2. Run the below command :
```
chmod +x run_TSCytoPred.sh
./run_TSCytoPred.sh
```

3. All the results will be saved in the newly created **results** directory.
   * pred_cytokine.csv : inferred cytokine expression values

## Contact
If you have any questions or problems, please contact to **joungmin AT vt.edu**.
