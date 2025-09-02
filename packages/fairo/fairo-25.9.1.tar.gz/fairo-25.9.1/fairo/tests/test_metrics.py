import pandas as pd
from modules.fairo.fairo.metrics.fairness_object import Fairness
from modules.fairo.fairo.metrics.metrics import *
from modules.fairo.fairo.metrics.metrics import _make_grouped_confusion_matrices


def assert_near(a, b, epsilon=.01):
    assert a - b < epsilon and a - b > -1 * epsilon

# Example DataFrame
data = [
    {'name': 'Bob', 'age': 32, 'gender': 'male', 'hired': True},
    {'name': 'Charlie', 'age': 28, 'gender': 'male', 'hired': True}, # 2 true positives
    {'name': 'Dave', 'age': 22, 'gender': 'male', 'hired': True}, 
    {'name': 'Dave', 'age': 22, 'gender': 'male', 'hired': True}, 
    {'name': 'Dave', 'age': 22, 'gender': 'male', 'hired': True}, # 3 false positives
    {'name': 'Dave', 'age': 22, 'gender': 'male', 'hired': False}, 
    {'name': 'Dave', 'age': 22, 'gender': 'male', 'hired': False}, 
    {'name': 'Dave', 'age': 22, 'gender': 'male', 'hired': False}, 
    {'name': 'Dave', 'age': 22, 'gender': 'male', 'hired': False}, 
    {'name': 'Dave', 'age': 22, 'gender': 'male', 'hired': False}, # 5 true negatives
    {'name': 'Dave', 'age': 22, 'gender': 'male', 'hired': False}, # 1 false negative

    {'name': 'Alice', 'age': 25, 'gender': 'female', 'hired': True},
    {'name': 'Alice', 'age': 25, 'gender': 'female', 'hired': True}, # 2 true positive
    {'name': 'Alice', 'age': 25, 'gender': 'female', 'hired': False},
    {'name': 'Alice', 'age': 25, 'gender': 'female', 'hired': False},
    {'name': 'Alice', 'age': 25, 'gender': 'female', 'hired': False},
    {'name': 'Alice', 'age': 25, 'gender': 'female', 'hired': False}, # 4 false negative
    {'name': 'Eve', 'age': 19, 'gender': 'female', 'hired': False}, # 1 true negative
    {'name': 'Eve', 'age': 19, 'gender': 'female', 'hired': True},
    {'name': 'Eve', 'age': 19, 'gender': 'female', 'hired': True},
    {'name': 'Eve', 'age': 19, 'gender': 'female', 'hired': True}, # 3 false positive
]

data_true = [
    {'gender': 'male', 'hired': True},
    {'gender': 'male', 'hired': True}, # 2 true positives
    {'gender': 'male', 'hired': False},
    {'gender': 'male', 'hired': False},
    {'gender': 'male', 'hired': False}, # 3 false positives
    {'gender': 'male', 'hired': False},
    {'gender': 'male', 'hired': False},
    {'gender': 'male', 'hired': False},
    {'gender': 'male', 'hired': False},
    {'gender': 'male', 'hired': False}, # 5 true negatives
    {'gender': 'male', 'hired': True}, # 1 false negative

    {'gender': 'female', 'hired': True},
    {'gender': 'female', 'hired': True}, # 2 true positives
    {'gender': 'female', 'hired': True},
    {'gender': 'female', 'hired': True},
    {'gender': 'female', 'hired': True},
    {'gender': 'female', 'hired': True}, # 4 false negative
    {'gender': 'female', 'hired': False}, # 1 true negative
    {'gender': 'female', 'hired': False},
    {'gender': 'female', 'hired': False},
    {'gender': 'female', 'hired': False}, # 3 false positives
]
scores = [.1, .3, .9, .4, .6, .1, .3, .9, .4, .6, .1, .3, .9, .4, .6, .1, .3, .9, .4, .6, .7]
df = pd.DataFrame(data)
df['scores'] = scores
y_true = pd.DataFrame(data_true)

# Example usage of the parity_difference function
protected_attribute = 'gender'
privileged_group = 'male'
labels = 'hired'
positive_label = True
fo = Fairness(df, protected_attribute, privileged_group, labels, positive_label, y_true)

### TEST GROUP CONFUSION MATRIX
(cm_priv, cm_unpriv) = _make_grouped_confusion_matrices(df, protected_attribute, privileged_group, labels, positive_label, y_true, normalize=None)
assert cm_priv[0][0] == 5 and cm_priv[0][1] == 3 and cm_priv[1][1] == 2 and cm_priv[1][0] == 1
assert cm_unpriv[0][0] == 1 and cm_unpriv[0][1] == 3 and cm_unpriv[1][1] == 2 and cm_unpriv[1][0] == 4

# pretty_print_confusion_matrix([_make_grouped_confusion_matrices(df, protected_attribute, privileged_group, labels, positive_label, y_true, normalize=None)[0]], ["privileged"])
# pretty_print_confusion_matrix([_make_grouped_confusion_matrices(df, protected_attribute, privileged_group, labels, positive_label, y_true, normalize=None)[1]], ["unprivileged"])
# pretty_print_confusion_matrix([_make_grouped_confusion_matrices(df, protected_attribute, privileged_group, labels, positive_label, y_true, normalize='all')[0]], ["privileged"])
# pretty_print_confusion_matrix([_make_grouped_confusion_matrices(df, protected_attribute, privileged_group, labels, positive_label, y_true, normalize='all')[1]], ["unprivileged"])


### CONFUSION MATRIX TESTS
(priv, unpriv) = false_positive_rate(df, protected_attribute, privileged_group, labels, positive_label, y_true)
assert priv == 3/(8 + EPSILON) and unpriv == 3/(4 + EPSILON)

(priv, unpriv) = true_negative_rate(df, protected_attribute, privileged_group, labels, positive_label, y_true)
assert priv == 5/(8 + EPSILON) and unpriv == 1/(4 + EPSILON)

(priv, unpriv) = true_positive_rate(df, protected_attribute, privileged_group, labels, positive_label, y_true)
assert priv == 2/(3 + EPSILON) and unpriv == 2/(6 + EPSILON)

(priv, unpriv) = false_negative_rate(df, protected_attribute, privileged_group, labels, positive_label, y_true)
assert priv == 1/(3 + EPSILON) and unpriv == 4/(6 + EPSILON)

(priv, unpriv) = positive_predictive_value(df, protected_attribute, privileged_group, labels, positive_label, y_true)
assert priv == 2/(5 + EPSILON) and unpriv == 2/(5 + EPSILON)

(priv, unpriv) = false_discovery_rate(df, protected_attribute, privileged_group, labels, positive_label, y_true)
assert priv == 3/(5 + EPSILON) and unpriv == 3/(5 + EPSILON)

(priv, unpriv) = negative_predictive_value(df, protected_attribute, privileged_group, labels, positive_label, y_true)
assert priv == 5/(6 + EPSILON) and unpriv == 1/(5 + EPSILON)

(priv, unpriv) = false_omission_rate(df, protected_attribute, privileged_group, labels, positive_label, y_true)
assert priv == 1/(6 + EPSILON) and unpriv == 4/(5 + EPSILON)


### PARITY TESTS
# print(parity_difference(df, protected_attribute, privileged_group, labels, positive_label)) # ~ -.05
assert_near(parity_difference(df, protected_attribute, privileged_group, labels, positive_label), -0.05)
# print(parity_ratio(df, protected_attribute, privileged_group, labels, positive_label)) # ~ .9
assert_near(parity_ratio(df, protected_attribute, privileged_group, labels, positive_label), .9)


####
# (diff, ratio) = predictive_parity(df, protected_attribute, privileged_group, labels, positive_label, y_true)
# assert diff == 0 and ratio == 1

cuad = conditional_use_accuracy_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true)
assert cuad == 0 + 5/(6 + EPSILON) - 1/(5 + EPSILON)

te = treatment_equality(df, protected_attribute, privileged_group, labels, positive_label, y_true)
assert te == 1/(3 + EPSILON) - 4/(3 + EPSILON)

eod = equal_odds_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true)
assert eod == 2/(3 + EPSILON) - 2/(6 + EPSILON)

aod = average_odds_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true)
assert aod - ((2/(3 + EPSILON) - 2/(6 + EPSILON) + 3/(8 + EPSILON) - 3/(4 + EPSILON)) / 2) < 1e-6 and aod - ((2/(3 + EPSILON) - 2/(6 + EPSILON) + 3/(8 + EPSILON) - 3/(4 + EPSILON)) / 2) > -1e-6

aor = average_odds_ratio(df, protected_attribute, privileged_group, labels, positive_label, y_true)
assert aor == ((2/(3 + EPSILON)) / (2/(6 + EPSILON)) + ((3/(8 + EPSILON)) / (3/(4 + EPSILON)))) / 2

accuracy = overall_accuracy(df, labels, y_true)
# print(accuracy) # ~ .476
assert_near(accuracy, .476)

acc_diff = accuracy_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true)
# print(acc_diff) # ~ .336
assert_near(acc_diff, .336)

# test fbeta
cm_all = confusion_matrix(y_true[labels], df[labels])
# pretty_print_confusion_matrix([cm_all])
f1_all = fb_score(df, labels, positive_label, y_true, beta=1)
assert f1_all == (2 * .4 * (4/9)) / (.4 + (4/9))
f2_all = fb_score(df, labels, positive_label, y_true, beta=2)
assert f2_all == ((1 + 2**2) * .4 * (4/9)) / ((2**2 * .4) + (4/9))

# test predictive equality
f1_priv, f1_unpriv = grouped_fb(df, protected_attribute, privileged_group, labels, positive_label, y_true, beta=1)
# print(f1_priv, f1_unpriv) # should be .5, .363636363
assert_near(f1_priv, .5)
assert_near(f1_unpriv, .36363)

fhalf_priv, fhalf_unpriv = grouped_fb(df, protected_attribute, privileged_group, labels, positive_label, y_true, beta=.5)
# print(fhalf_priv) # ~ .4347
# print(fhalf_unpriv) # ~ .3846
assert_near(fhalf_priv, .4347)
assert_near(fhalf_unpriv, .3846)

per = fb_ratio(df, protected_attribute, privileged_group, labels, positive_label, y_true, beta=1)
# print(per) # ~ 1.37
assert_near(per, 1.37)
ped = fb_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true, beta=1)
# print(ped) # ~ .136
assert_near(ped, .136)

per = fb_ratio(df, protected_attribute, privileged_group, labels, positive_label, y_true, beta=.5)
# print(per) # ~ 1.13
assert_near(per, 1.13)
ped = fb_difference(df, protected_attribute, privileged_group, labels, positive_label, y_true, beta=.5)
# print(ped) # ~ .0501
assert_near(ped, .0501)


### PROGRAMMATIC EXAMPLE
url = "http://localhost:4566/restapis/6c60fuj871/local/_user_request_/metrics"
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Basic YTg5ZWZkMWUtODdiOS00ZWNhLWE1YTItYTI4YjU3MmEyODVjOmUzZDdlMzJkZmQzNDlhMTEyYmZiYjE3ZWQzNDI1OWUx',
  'Cookie': 'sessionid=gzc64jx2wjghdr99obibgdz4xyclbmen'
}
func_name = "False Negative Rate"
payload = {
    "new_parameter_values": {
        "df": df.to_json(),
        "privileged_group": privileged_group,
        "labels": labels,
        "positive_label": positive_label,
        "kwargs": {
            "beta": 2
        },
        "y_true": y_true.to_json(),
        "protected_attribute": protected_attribute,
        "scores": "scores"
    },
    "existing_parameter_values": {},
    "func_name": func_name
}
# print(payload)

# response = requests.request("POST", url, headers=headers, data=payload)
# local_result = metric_names_to_python_functions[func_name](df=df, labels=labels, positive_label=positive_label, y_true=y_true, protected_attribute=protected_attribute, privileged_group=privileged_group,
#                                                   beta=2)


# for key, value in metric_names_to_python_functions.items():
#     payload["func_name"] = key
#     response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
#     local_result = metric_names_to_python_functions[key](df=df, labels=labels, positive_label=positive_label, y_true=y_true, protected_attribute=protected_attribute,  privileged_group=privileged_group, scores='scores', beta=2)
#     print(key)
#     try:                           
#         print(f"lambda: {json.loads(response.text)['result']}") 
#     except Exception:
#         print(response.text)
#     print(f"local:  {local_result}")