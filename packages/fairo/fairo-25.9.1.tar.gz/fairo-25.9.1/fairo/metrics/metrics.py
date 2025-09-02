from sklearn.metrics import confusion_matrix, accuracy_score, roc_auc_score
import numpy as np

EPSILON = 1e-10 # used to avoid division by 0

## helpers
def _make_grouped_confusion_matrices(df, protected_attribute, privileged_group, labels, positive_label, y_true, normalize=None):
    """
    Returns confusion matrices for priv and unpriv groups

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome
        y_true (pandas.DataFrame): pandas DataFrame holding correct predictions
        normalize (str): either None meaning confusion matrices are in tp, fp, etc. 'true' if tpr, fpr, etc

    Returns:
        tuple: (cm of priv, cm of unpriv)
    """
    privileged_df = df[df[protected_attribute] == privileged_group]
    y_pred_priviledged = privileged_df[labels]
    unprivileged_df = df[df[protected_attribute] != privileged_group]
    y_pred_unpriviledged = unprivileged_df[labels]

    priviledged_yt = y_true[y_true[protected_attribute] == privileged_group]
    y_true_priviledged = priviledged_yt[labels]
    unprivileged_yt = y_true[y_true[protected_attribute] != privileged_group]
    y_true_unpriviledged = unprivileged_yt[labels]

    cm_priv = confusion_matrix(y_true_priviledged, y_pred_priviledged, normalize=normalize)
    cm_unpriv = confusion_matrix(y_true_unpriviledged, y_pred_unpriviledged, normalize=normalize)
    return (cm_priv, cm_unpriv)



def pretty_print_confusion_matrix(matrices, names=None):
    # todo: make work with normalized
    for i, matrix in enumerate(matrices):
        if names == None:
            print(f"Confusion Matrix {i + 1}:")
        else:
            print(f"{names[i]}:")
        print("            Predicted")
        print("\t\t      0  \t 1")
        print("\t\t     ---------------")
        print(f"True  0 {matrix[0, 0]:>15} {matrix[0, 1]:>10}")
        print(f"      1 {matrix[1, 0]:>15} {matrix[1, 1]:>10}")
        print("\n")



def _calculate_priv_unpriv_metric(df, protected_attribute, privileged_group, labels, positive_label, y_true, metric_func, **kwargs):
    """
    Calculate a given metric for the privileged and unprivileged groups in a dataset.

    Args:
        df (pandas.DataFrame): The input dataset.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group (any): The value of the protected attribute that denotes the privileged group.
        labels (str): The name of the column containing the predicted labels.
        positive_label (any): The value of the positive label.
        y_true (pandas.Series): The true labels.
        metric_func (callable): The metric function to use (e.g., f1_score, roc_auc_score).
        **kwargs: Additional keyword arguments to be passed to metric_func.

    Returns:
        tuple: result of metric_func on privileged and unprivileged groups
    """
    privileged_group_df = df[df[protected_attribute] == privileged_group]
    unprivileged_group_df = df[df[protected_attribute] != privileged_group]

    # Extract 'labels' column for privileged and unprivileged groups
    y_pred_privileged = privileged_group_df[labels]
    y_true_privileged = y_true[y_true.index.isin(privileged_group_df.index)][labels]
    y_pred_unprivileged = unprivileged_group_df[labels]
    y_true_unprivileged = y_true[y_true.index.isin(unprivileged_group_df.index)][labels]

    # Calculate metric for privileged and unprivileged groups
    metric_privileged = metric_func(y_true_privileged, y_pred_privileged, positive_label=positive_label, **kwargs)
    metric_unprivileged = metric_func(y_true_unprivileged, y_pred_unprivileged, positive_label=positive_label, **kwargs)
    return metric_privileged, metric_unprivileged



def _calculate_priv_unpriv_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true, metric_func, **kwargs):
    """
    Calculate the difference between a given metric for the privileged and unprivileged groups in a dataset.

    Args:
        df (pandas.DataFrame): The input dataset.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group (any): The value of the protected attribute that denotes the privileged group.
        labels (str): The name of the column containing the predicted labels.
        positive_label (any): The value of the positive label.
        y_true (pandas.Series): The true labels.
        metric_func (callable): The metric function to use (e.g., f1_score, roc_auc_score).
        **kwargs: Additional keyword arguments to be passed to metric_func.

    Returns:
        float: The difference between the metric calculated on the privileged and unprivileged groups.
    """
    metric_privileged, metric_unprivileged = _calculate_priv_unpriv_metric(df, protected_attribute, privileged_group, labels, positive_label, y_true, metric_func, **kwargs)
    return metric_privileged - metric_unprivileged



def _calculate_priv_unpriv_ratio(df, protected_attribute, privileged_group, labels, positive_label, y_true, metric_func, epsilon=EPSILON, **kwargs):
    """
    Calculate the ratio between a given metric for the privileged and unprivileged groups in a dataset.

    Args:
        df (pandas.DataFrame): The input dataset.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group (any): The value of the protected attribute that denotes the privileged group.
        labels (str): The name of the column containing the predicted labels.
        positive_label (any): The value of the positive label.
        y_true (pandas.Series): The true labels.
        metric_func (callable): The metric function to use (e.g., f1_score, roc_auc_score).
        **kwargs: Additional keyword arguments to be passed to metric_func.

    Returns:
        float: The ratio between the metric calculated on the privileged and unprivileged groups.
    """
    metric_privileged, metric_unprivileged = _calculate_priv_unpriv_metric(df, protected_attribute, privileged_group, labels, positive_label, y_true, metric_func, **kwargs)
    return metric_privileged / (metric_unprivileged + epsilon)



## preliminary definitions using df and y_true
def false_positive_rate(df, protected_attribute, privileged_group, labels, positive_label, y_true, epsilon=EPSILON, **kwargs):
    """
    Returns false positive rate for priv and unpriv groups

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome
        y_true (pandas.DataFrame): pandas DataFrame holding correct predictions

    Returns:
        tuple: (FPR of priv, FPR of unpriv)
    """
    (cm_priv, cm_unpriv) = _make_grouped_confusion_matrices(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    # FP / (FP + TN)
    priv_return = cm_priv[0][1] / (cm_priv[0][1] + cm_priv[0][0] + epsilon)
    unpriv_return = cm_unpriv[0][1] / (cm_unpriv[0][1] + cm_unpriv[0][0] + epsilon)
    return (priv_return, unpriv_return)



def true_negative_rate(df, protected_attribute, privileged_group, labels, positive_label, y_true, epsilon=EPSILON, **kwargs):
    """
    Returns true negative rate for priv and unpriv groups

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome
        y_true (pandas.DataFrame): pandas DataFrame holding correct predictions

    Returns:
        tuple: (TNR of priv, TNR of unpriv)
    """
    (cm_priv, cm_unpriv) = _make_grouped_confusion_matrices(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    # TN / (FP + TN)
    priv_return = cm_priv[0][0] / (cm_priv[0][0] + cm_priv[0][1] + epsilon)
    unpriv_return = cm_unpriv[0][0] / (cm_unpriv[0][0] + cm_unpriv[0][1] + epsilon)
    return (priv_return, unpriv_return)



def true_positive_rate(df, protected_attribute, privileged_group, labels, positive_label, y_true, epsilon=EPSILON, **kwargs):
    """
    Returns true positive rate aka recall and sensitivity for priv and unpriv groups

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome
        y_true (pandas.DataFrame): pandas DataFrame holding correct predictions

    Returns:
        tuple: (TPR of priv, TPR of unpriv)
    """
    (cm_priv, cm_unpriv) = _make_grouped_confusion_matrices(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    # TP / (TP + FN)
    priv_return = cm_priv[1][1] / (cm_priv[1][1] + cm_priv[1][0] + epsilon)
    unpriv_return = cm_unpriv[1][1] / (cm_unpriv[1][1] + cm_unpriv[1][0] + epsilon)
    return (priv_return, unpriv_return)



def false_negative_rate(df, protected_attribute, privileged_group, labels, positive_label, y_true, epsilon=EPSILON, **kwargs):
    """
    Returns false negative rate for priv and unpriv groups

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome
        y_true (pandas.DataFrame): pandas DataFrame holding correct predictions

    Returns:
        tuple: (FNR of priv, FNR of unpriv)
    """
    (cm_priv, cm_unpriv) = _make_grouped_confusion_matrices(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    # FN / (TP + FN)
    priv_return = cm_priv[1][0] / (cm_priv[1][0] + cm_priv[1][1] + epsilon)
    unpriv_return = cm_unpriv[1][0] / (cm_unpriv[1][0] + cm_unpriv[1][1] + epsilon)
    return (priv_return, unpriv_return)



def positive_predictive_value(df, protected_attribute, privileged_group, labels, positive_label, y_true, epsilon=EPSILON, **kwargs):
    """
    Returns positive_predictive_value aka precision for priv and unpriv groups

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome
        y_true (pandas.DataFrame): pandas DataFrame holding correct predictions

    Returns:
        tuple: (PPV of priv, PPV of unpriv)
    """
    (cm_priv, cm_unpriv) = _make_grouped_confusion_matrices(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    # TP / (TP + FP)
    priv_return = cm_priv[1][1] / (cm_priv[1][1] + cm_priv[0][1] + epsilon)
    unpriv_return = cm_unpriv[1][1] / (cm_unpriv[1][1] + cm_unpriv[0][1] + epsilon)
    return (priv_return, unpriv_return)



def false_discovery_rate(df, protected_attribute, privileged_group, labels, positive_label, y_true, epsilon=EPSILON, **kwargs):
    """
    Returns false_discovery_rate for priv and unpriv groups

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome
        y_true (pandas.DataFrame): pandas DataFrame holding correct predictions

    Returns:
        tuple: (FDR of priv, FDR of unpriv)
    """
    (cm_priv, cm_unpriv) = _make_grouped_confusion_matrices(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    # FP / (FP + TP)
    priv_return = cm_priv[0][1] / (cm_priv[1][1] + cm_priv[0][1] + epsilon)
    unpriv_return = cm_unpriv[0][1] / (cm_unpriv[1][1] + cm_unpriv[0][1] + epsilon)
    return (priv_return, unpriv_return)



def negative_predictive_value(df, protected_attribute, privileged_group, labels, positive_label, y_true, epsilon=EPSILON, **kwargs):
    """
    Returns negative_predictive_value for priv and unpriv groups

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome
        y_true (pandas.DataFrame): pandas DataFrame holding correct predictions

    Returns:
        tuple: (NPV of priv, NPV of unpriv)
    """
    (cm_priv, cm_unpriv) = _make_grouped_confusion_matrices(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    # TN / (TN + FN)
    priv_return = cm_priv[0][0] / (cm_priv[1][0] + cm_priv[0][0] + epsilon)
    unpriv_return = cm_unpriv[0][0] / (cm_unpriv[1][0] + cm_unpriv[0][0] + epsilon)
    return (priv_return, unpriv_return)



def false_omission_rate(df, protected_attribute, privileged_group, labels, positive_label, y_true, epsilon=EPSILON, **kwargs):
    """
    Returns false_omission_rate for priv and unpriv groups

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome
        y_true (pandas.DataFrame): pandas DataFrame holding correct predictions

    Returns:
        tuple: (FOR of priv, FOR of unpriv)
    """
    (cm_priv, cm_unpriv) = _make_grouped_confusion_matrices(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    # FN / (TN + FN)
    priv_return = cm_priv[1][0] / (cm_priv[1][0] + cm_priv[0][0] + epsilon)
    unpriv_return = cm_unpriv[1][0] / (cm_unpriv[1][0] + cm_unpriv[0][0] + epsilon)
    return (priv_return, unpriv_return)



## metrics just using predicted values (df)
def selection_rate(data, positive_label, epsilon=EPSILON):
    """
    Calculate the selection rate for a column in a DataFrame based on a positive label.

    Args:
        data (pandas.Series): The column data.
        positive_label: The positive label to calculate the selection rate for.

    Returns:
        float: The selection rate as a proportion between 0 and 1.

    Example:
        df = pd.DataFrame(data)
        privileged_df = df[df[protected_attribute] == privileged_group]
        privileged_selection_rate = selection_rate(privileged_df[labels], positive_label)
    """
    total_samples = len(data)
    positive_samples = sum(data == positive_label)

    return positive_samples / (total_samples + epsilon)



def parity_vals(df, protected_attribute, privileged_group, labels, positive_label, **kwargs):
    """
    Calculate the parity difference for a selected column based on the protected attribute and privileged group.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome

    Returns:
        (parity_difference, parity_ratio)
    """
    return (parity_difference(df, protected_attribute, privileged_group, labels, positive_label), parity_ratio(df, protected_attribute, privileged_group, labels, positive_label))



def parity_difference(df, protected_attribute, privileged_group, labels, positive_label, **kwargs):
    """
    Calculate the parity difference for a selected column based on the protected attribute and privileged group.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome

    Returns:
        float: The parity difference as a proportion between -1 and 1.
    """
    privileged_df = df[df[protected_attribute] == privileged_group]
    privileged_selection_rate = selection_rate(privileged_df[labels], positive_label)

    unprivileged_df = df[df[protected_attribute] != privileged_group]
    unprivileged_selection_rate = selection_rate(unprivileged_df[labels], positive_label)
 
    return privileged_selection_rate - unprivileged_selection_rate



def parity_ratio(df, protected_attribute, privileged_group, labels, positive_label, epsilon=EPSILON, **kwargs):
    """
    Calculate the parity difference for a selected column based on the protected attribute and privileged group.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome

    Returns:
        float: The parity ratio as a proportion between 0 and 1.
    """
    privileged_df = df[df[protected_attribute] == privileged_group]
    privileged_selection_rate = selection_rate(privileged_df[labels], positive_label)

    unprivileged_df = df[df[protected_attribute] != privileged_group]
    unprivileged_selection_rate = selection_rate(unprivileged_df[labels], positive_label)

    return privileged_selection_rate / (unprivileged_selection_rate + epsilon)



## metrics using df and y_true
def predictive_parity(df, protected_attribute, privileged_group, labels, positive_label, y_true, **kwargs):
    """
    Calculates PPV and NPV difference and ratio between priv and unpriv groups

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome
        y_true (pandas.DataFrame): pandas DataFrame holding correct predictions

    Returns:
        tuple: ((PPV difference, PPV ratio), (NPV difference, NPV ratio))
    """
    (ppv_priv, ppv_unpriv) = positive_predictive_value(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    (npv_priv, npv_unpriv) = negative_predictive_value(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    return ((ppv_priv - ppv_unpriv, ppv_priv / ppv_unpriv), (npv_priv - npv_unpriv, npv_priv / npv_unpriv))



def conditional_use_accuracy_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true, **kwargs):
    """
    Calculates total difference between ppv and npv for priv and unpriv group

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome
        y_true (pandas.DataFrame): pandas DataFrame holding correct predictions

    Returns:
        float: total difference between ppv and npv for priv and unpriv group
    """
    (ppv_priv, ppv_unpriv) = positive_predictive_value(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    (npv_priv, npv_unpriv) = negative_predictive_value(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    return ppv_priv - ppv_unpriv + npv_priv - npv_unpriv



def treatment_equality(df, protected_attribute, privileged_group, labels, positive_label, y_true, epsilon=EPSILON, **kwargs):
    """
    Calculates FN / FP for priv and unpriv groups

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome
        y_true (pandas.DataFrame): pandas DataFrame holding correct predictions

    Returns:
        tuple: FN / FP for priv and unpriv groups
    """
    (cm_priv, cm_unpriv) = _make_grouped_confusion_matrices(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    # FN / FP
    priv_ret = cm_priv[1][0] / (cm_priv[0][1] + epsilon)
    unpriv_ret = cm_unpriv[1][0] / (cm_unpriv[0][1] + epsilon)
    return priv_ret - unpriv_ret



def equal_odds_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true, **kwargs):
    """
    Calculates equal_odds_difference between privileged_group and unpr

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome
        y_true (pandas.DataFrame): pandas DataFrame holding correct predictions

    Returns:
        float: the equal odds difference between privileged group and unpr

    Example:
        df = pd.DataFrame(data)
        y_true = pd.DataFrame(data_true)
        protected_attribute = 'gender'
        privileged_group = 'male'
        selected_column = 'hired'
        positive_label = True
        eod = equal_odds_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    """
    (tpr_priv, tpr_unpriv) = true_positive_rate(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    return tpr_priv - tpr_unpriv



def average_odds_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true, **kwargs):
    """
    Calculates average_odds_difference between privileged_group and unpr

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome
        y_true (pandas.Data): pandas DataFrame holding correct predictions

    Returns:
        float: the average odds difference between privileged group and unpr

    Example:
        df = pd.DataFrame(data)
        y_true = pd.DataFrame(data_true)
        protected_attribute = 'gender'
        privileged_group = 'male'
        selected_column = 'hired'
        positive_label = True
        eod = average_odds_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    """
    (tpr_priv, tpr_unpriv) = true_positive_rate(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    tpr_diff = tpr_priv - tpr_unpriv
    (fpr_priv, fpr_unpriv) = false_positive_rate(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    fpr_diff = fpr_priv - fpr_unpriv
    return (tpr_diff + fpr_diff) / 2



def average_odds_ratio(df, protected_attribute, privileged_group, labels, positive_label, y_true, epsilon=EPSILON, **kwargs):
    """
    Calculates average_odds_ratio between privileged_group and unpr

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group: The privileged group value in the protected attribute column.
        labels (str): The name of the selected column for labels.
        positive_label: a label that indicates a positive outcome
        y_true (pandas.Data): pandas DataFrame holding correct predictions

    Returns:
        float: the average odds ratio between privileged group and unpr

    Example:
        df = pd.DataFrame(data)
        y_true = pd.DataFrame(data_true)
        protected_attribute = 'gender'
        privileged_group = 'male'
        selected_column = 'hired'
        positive_label = True
        eod = average_odds_ratio(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    """
    (tpr_priv, tpr_unpriv) = true_positive_rate(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    tpr_ratio = tpr_priv / (tpr_unpriv + epsilon)
    (fpr_priv, fpr_unpriv) = false_positive_rate(df, protected_attribute, privileged_group, labels, positive_label, y_true)
    fpr_ratio = fpr_priv / (fpr_unpriv + epsilon)
    return (tpr_ratio + fpr_ratio) / 2



def overall_accuracy(df, labels, y_true, **kwargs):
    """
    Calculate overall accuracy of df compared to y_true

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        labels (str): The name of the selected column for labels.
        y_true (pandas.DataFrame): pandas DataFrame holding correct predictions

    Returns:
        float: the accuracy difference between priv and unpriv groups

    Example:
        df = pd.DataFrame(data)
        y_true = pd.DataFrame(data_true)
        protected_attribute = 'gender'
        privileged_group = 'male'
        labels = 'hired'
        positive_label = True
        ac = overall_accuracy(df, labels, y_true)
    """
    return accuracy_score(y_true[labels], df[labels])



def accuracy_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true, **kwargs):
    """
    Calculates the difference in accuracy between the privileged and unprivileged groups for a given binary classification
    problem.

    Args:
        df (pandas.DataFrame): The dataset.
        protected_attribute (str): The column name of the protected attribute.
        privileged_group (any): The privileged group for the protected attribute.
        labels (str): The column name of the predicted labels.
        positive_label (any): The positive label (usually True or 1).
        y_true (pandas.Series): The ground truth labels.

    Returns:
        float: The difference in accuracy between the privileged and unprivileged groups.
    """
    return _calculate_priv_unpriv_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true, (lambda x, y, **kwargs: accuracy_score(x, y)))



## stats
def gini_coefficient(df, scores, **kwargs):
    """
    Calculate the Gini coefficient for the given scores and protected attribute.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group (any): The privileged group value in the protected attribute column.
        scores (str): The name of the selected column for scores.

    Returns:
        float: gini coeff

    Raises:
        ValueError: If the scores column is not present
    """
    if len(scores) == 0:
        raise ValueError('scores was not provided')
    
    def gini(x):
        total = 0
        for i, xi in enumerate(x[:-1], 1):
            total += np.sum(np.abs(xi - x[i:]))
        return total / (len(x)**2 * np.mean(x))

    return gini(df[scores])



def theil_index(df, scores, epsilon=EPSILON, **kwargs):
    """
    Calculates the Theil T Index

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        scores (str): The name of the selected column for scores.

    Returns:
        float: Theil T of scores column

    Raises:
        ValueError: If the scores column is not present
    """
    scores_column = df[scores]
    if len(scores_column) == 0:
        raise ValueError('scores was not provided')
    
    scores_over_mean = scores_column / (np.mean(scores_column) + epsilon)
    log_scores_over_mean = np.log(scores_over_mean)
    total = float(0)
    for i in range(len(scores_column)):
        total += scores_over_mean[i] * log_scores_over_mean[i]
    return total / len(scores_column)



def _fb_score(y_true, y_pred, positive_label, beta=1):
    """
    Helper function that calculates the Fbeta score for a binary classification problem.

    Args:
        y_true (array-like): Ground truth labels.
        y_pred (array-like): Predicted labels.
        positive_label (any): Positive label (usually True or 1)
        beta: weight chosen such that recall is considered beta times as important as precision

    Returns:
        float: The Fbeta score.
    """
    tp = sum((yt == positive_label and yp == positive_label) for yt, yp in zip(y_true, y_pred))
    fp = sum((yt != positive_label and yp == positive_label) for yt, yp in zip(y_true, y_pred))
    fn = sum((yt == positive_label and yp != positive_label) for yt, yp in zip(y_true, y_pred))

    if tp == 0:
        return 0

    precision = tp / (tp + fp)
    recall = tp / (tp + fn)

    fb = (1 + beta**2) * precision * recall / ((beta**2 * precision) + recall)

    return fb



def fb_score(df, labels, positive_label, y_true, beta=1, **kwargs):
    """
    Calculate the Fbeta score for binary classification.

    Args:
        df (pandas.DataFrame): The input dataframe.
        labels (str): The name of the column containing the predicted labels.
        positive_label (any): The value representing the positive label.
        y_true (pandas.DataFrame): The true df.

    Returns:
        float: The F1 score.

    Example:
        data = pd.DataFrame({'labels': [0, 1, 1, 0], 'predictions': [0, 1, 1, 0]})
        true_labels = data['labels']
        predicted_labels = data['predictions']
        score = f1_score(data, 'predictions', 1, true_labels)
    """
    # print(y_true[labels], df[labels], positive_label, beta)
    return _fb_score(y_true[labels], df[labels], positive_label, beta=beta)



def grouped_fb(df, protected_attribute, privileged_group, labels, positive_label, y_true, beta=1, **kwargs):
    """
    Calculate fbeta score for a privileged group and an unprivileged group.

    Args:
        df (pandas DataFrame): The dataset.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group (any): The privileged group value for the protected attribute.
        labels (str): The name of the predicted label column.
        positive_label (any): The positive label value.
        y_true (pandas Series): The true label values.

    Returns:
        tuple: score for priv, score for unpriv
    """
    return _calculate_priv_unpriv_metric(df, protected_attribute, privileged_group, labels, positive_label, y_true, _fb_score, beta=beta)



def fb_ratio(df, protected_attribute, privileged_group, labels, positive_label, y_true, beta=1, **kwargs):
    """
    Calculate the ratio in fbeta score between a privileged group and an unprivileged group.

    Args:
        df (pandas DataFrame): The dataset.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group (any): The privileged group value for the protected attribute.
        labels (str): The name of the predicted label column.
        positive_label (any): The positive label value.
        y_true (pandas Series): The true label values.

    Returns:
        float: ratio of priv pe to unpriv pe
    """
    return _calculate_priv_unpriv_ratio(df, protected_attribute, privileged_group, labels, positive_label, y_true, _fb_score, beta=beta)



def fb_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true, beta=1, **kwargs):
    """
    Calculate the difference in fbeta score between a privileged group and an unprivileged group.

    Args:
        df (pandas DataFrame): The dataset.
        protected_attribute (str): The name of the protected attribute column.
        privileged_group (any): The privileged group value for the protected attribute.
        labels (str): The name of the predicted label column.
        positive_label (any): The positive label value.
        y_true (pandas Series): The true label values.

    Returns:
        float: difference between priv pe to unpriv pe
    """
    return  _calculate_priv_unpriv_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true, _fb_score, beta=beta)



def roc_auc_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true, **kwargs):
    """
    Calculate the difference in ROC AUC score between the privileged group and the unprivileged group.

    Args:
        df (pandas.DataFrame): Dataset.
        protected_attribute (str): Name of the protected attribute column.
        privileged_group (any): Value of the privileged group.
        labels (str): Name of the column containing predicted scores.
        positive_label (any): Value of the positive label.
        y_true (array-like): Ground truth labels.

    Returns:
        float: The difference in ROC AUC score between the privileged group and the unprivileged group.
    """
    return _calculate_priv_unpriv_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true, (lambda x, y, **kwargs: roc_auc_score(x, y)))



def roc_auc_ratio(df, protected_attribute, privileged_group, labels, positive_label, y_true, **kwargs):
    """
    Calculate the difference in ROC AUC score between the privileged group and the unprivileged group.

    Args:
        df (pandas.DataFrame): Dataset.
        protected_attribute (str): Name of the protected attribute column.
        privileged_group (any): Value of the privileged group.
        labels (str): Name of the column containing predicted scores.
        positive_label (any): Value of the positive label.
        y_true (array-like): Ground truth labels.

    Returns:
        float: The difference in ROC AUC score between the privileged group and the unprivileged group.
    """
    return _calculate_priv_unpriv_ratio(df, protected_attribute, privileged_group, labels, positive_label, y_true, (lambda x, y, **kwargs: roc_auc_score(x, y)))



def grouped_roc_auc(df, protected_attribute, privileged_group, labels, positive_label, y_true, **kwargs):
    """
    Calculate the difference in ROC AUC score between the privileged group and the unprivileged group.

    Args:
        df (pandas.DataFrame): Dataset.
        protected_attribute (str): Name of the protected attribute column.
        privileged_group (any): Value of the privileged group.
        labels (str): Name of the column containing predicted scores.
        positive_label (any): Value of the positive label.
        y_true (array-like): Ground truth labels.

    Returns:
        float: The difference in ROC AUC score between the privileged group and the unprivileged group.
    """
    return _calculate_priv_unpriv_metric(df, protected_attribute, privileged_group, labels, positive_label, y_true, (lambda x, y, **kwargs: roc_auc_score(x, y)))



def roc_auc(df, labels, y_true, **kwargs):
    """
    Calculate the ROC AUC (Area Under the Receiver Operating Characteristic Curve) score.

    Args:
        df (pandas.DataFrame): The input dataframe.
        labels (str): The name of the column containing the predicted labels.
        y_true (pandas.DataFrame): The true labels.

    Returns:
        float: The ROC AUC score.

    Example:
        data = pd.DataFrame({'labels': [0, 1, 1, 0], 'predictions': [0.2, 0.8, 0.6, 0.4]})
        true_labels = data['labels']
        predicted_labels = data['predictions']
        score = roc_auc(data, 'predictions', true_labels)
    """
    return roc_auc_score(y_true[labels], df[labels])



metric_names_to_python_functions = {
    # Confusion Matrix metrics
    "False Positive Rate": false_positive_rate,
    "True Negative Rate": true_negative_rate,
    "True Positive Rate": true_positive_rate,
    "False Negative Rate": false_negative_rate,
    "Positive Predictive Value": positive_predictive_value,
    "False Discovery Rate": false_discovery_rate,
    "Negative Predictive Value": negative_predictive_value,
    "False Omission Rate": false_omission_rate,

    # Selection Rate metrics
    "Parity Difference": parity_difference,
    "Parity Ratio": parity_ratio,

    # Fairness metrics
    "Predictive Parity": predictive_parity,
    "Conditional Use Accuracy Difference": conditional_use_accuracy_difference,
    "Treatment Equality": treatment_equality,

    # Odds metrics
    "Equal Odds Difference": equal_odds_difference,
    "Average Odds Difference": average_odds_difference,
    "Average Odds Ratio": average_odds_ratio,

    # Accuracy metrics
    "Overall Accuracy": overall_accuracy,
    "Accuracy Difference": accuracy_difference,

    # F-Beta metrics
    "F-Beta Score": fb_score,
    "Grouped F-Beta": grouped_fb,
    "F-Beta Ratio": fb_ratio,
    "F-Beta Difference": fb_difference,

    # ROC AUC metrics
    "ROC AUC Score": roc_auc,
    "ROC AUC Difference": roc_auc_difference,
    "ROC AUC Ratio": roc_auc_ratio,
    "Grouped ROC AUC": grouped_roc_auc,

    # Inequality metrics
    "Gini Coefficient": gini_coefficient,
    "Theil Index": theil_index
}