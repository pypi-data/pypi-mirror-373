import pickle

class Fairness:
    """
    A class for measuring fairness of a predictive model with respect to a protected attribute.

    Attributes:
        _df (pandas.DataFrame): Pandas DataFrame holding data predicted by a model.
        _labels (str): Name of column in _df containing outcome labels.
        _positive_label (any): Label that indicates a positive outcome.
        _y_true (pandas.DataFrame): (Optional) Pandas DataFrame holding true values, used in some metrics.
        _kwargs (dict): (Optional) Dictionary holding various metadata that users can pass in to custom metric functions.
        _protected_attribute (str): Name of the protected attribute.
        _privileged_group (any): Group with a historically positive label for their protected attribute,
            corresponding to a positive outcome of the condition_func.
        __results (dict): Dictionary holding the results of metrics.
        _scores (str): Name of the column in _df containing predicted scores.

    Methods:
        __init__(self, df, protected_attribute, privileged_group, labels, positive_label, y_true=None,
                 column_to_interpret=None, condition_func=None, scores, **kwargs):
            Initializes a Fairness object that holds arguments as instance variables.
            Note: Will create priv and unpriv groups if column_to_interpret and condition_func is not None
            using create_groups() func
        _create_groups(self, column_to_interpret, condition_func, protected_attribute, privileged_group):
            Creates column specifiying priv and unpriv groups based on results from condition_func
        compute(self, func):
            Computes func on self. Saves result in __result dict and returns result
        get_result_of(self, func):
            Returns most previous result of func(self)
        getters and setters exist for all attributes except for __results
    """
    def __init__(self, df, protected_attribute, privileged_group, labels, positive_label, y_true=None, column_to_interpret=None, condition_func=None, scores=None, **kwargs):
        """Creates a Fairness object that holds args as instance vars
        Note: Will create priv and unpriv groups if column_to_interpret and condition_func is not None
        using create_groups() func

        Args:
            self: object
            df (pandas.DataFrame): pandas DataFrame holding data predicted by a model
            protected_attribute (str): attributing describing a feature eg. sex, race, religion, etc.
            privileged_group: group with a historically posive label for their protected_attribute, positive outcome of condition_func
            labels (str): column holding outcome labels
            positive_label: a label that indicates a positive outcome

            y_true (optional pandas.DataFrame): pandas DataFrame holding true values, optional because not all metrics compare to true values

            column_to_interpret (optional str): name of column in self._df containing values to be passed to condition_func
            condition_func (optional func): function used to determine values in protected_attribute column

            kwargs (optional dict): used to hold various metadata that users can pass in to custom metric functions

        Returns:
            Fairness object holding results of metrics

        Example:
            df = pd.DataFrame(data)
            y_true = pd.DataFrame(data_true)
            protected_attribute = 'gender'
            privileged_group = 'male'
            labels = 'hired'
            positive_label = True
            condition_func = lambda x: x > 30

            fo_gender = Fairness(df, protected_attribute, privileged_group, labels, positive_label, y_true) # creates fairness object
            fo_age = Fairness(df, 'age_older_than_30', True, labels, True, column_to_interpret='age', condition_func=condition_func)
        """
        self._df = df
        self._labels = labels
        self._positive_label = positive_label
        self._y_true = y_true
        self.__results = {}
        self._scores = scores

        if column_to_interpret is None or condition_func is None:
            self._protected_attribute = protected_attribute
            self._privileged_group = privileged_group
        else:
            self._create_groups(column_to_interpret, condition_func, protected_attribute, privileged_group)

    def _create_groups(self, column_to_interpret, condition_func, protected_attribute, privileged_group):
        """Creates column specifiying priv and unpriv groups based on results from condition_func
        Creates column self._protected_attribute in self._df where values are condition_func(column_to_interpret[i])
        for all values in column_to_interpret. privileged_group is the positive outcome of condition_func

        Args:
            column_to_interpret (str): name of column in self._df containing values to be passed to condition_func
            condition_func (func): function used to determine values in protected_attribute column
            protected_attribute (str): attributing describing a feature. Used for new column name in self._df
            privileged_group: group with a historically posive label for their protected_attribute, positive outcome of condition_func

        Returns:
        None

        Example:
            protected_attribute = 'gender'
            privileged_group = 'male'
            labels = 'hired'
            positive_label = True
            fo = Fairness(df, None, None, labels, positive_label)
            condition_func = lambda x: x > 30
            fo._create_group('age', condition_func, 'age_older_than_30', True)
            print(fo.compute(parity_vals))
        """
        self._df[protected_attribute] = self._df[column_to_interpret].apply(condition_func)
        self._protected_attribute = protected_attribute
        self._privileged_group = privileged_group

    def compute(self, func, **kwargs):
        """Computes func on self. Saves result in __result dict and returns result

        Args:
            func: metric function whose result is to be returned

        Returns:
            result of func(self.args)

        Example:
            val = fo.compute(parity_vals)
        """
        self.__results[func] = func(df=self._df, protected_attribute=self._protected_attribute, privileged_group=self._privileged_group, labels=self._labels, positive_label=self._positive_label, y_true=self._y_true, scores=self._scores, **kwargs)
        return self.__results[func]

    def get_result_of(self, func):
        """Returns most previous result of func(self)
        Returns most previous result of func(self) if one exists. Else evaluates
        and returns func(self)

        Args:
            func: func whose result is to be returned
            self: object

        Returns:
            most previous result of func(self) or func(self) if no value yet exists

        Example:
            val = fo.get_result_of(parity_vals)
        """
        if func not in self.__results:
            self.compute(func)
        return self.__results[func]


    def save(self, file_name):
        with open(file_name, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, file_name):
        with open(file_name, "rb") as f:
            loaded_object = pickle.load(f)
        return loaded_object

    # Getters
    def get_df(self):
        return self._df

    def get_protected_attribute(self):
        return self._protected_attribute

    def get_privileged_group(self):
        return self._privileged_group

    def get_labels(self):
        return self._labels

    def get_positive_label(self):
        return self._positive_label

    def get_y_true(self):
        return self._y_true

    def get_scores(self):
        return self._scores

    # Setters
    def set_df(self, df):
        self._df = df

    def set_protected_attribute(self, protected_attribute):
        self._protected_attribute = protected_attribute

    def set_privileged_group(self, privileged_group):
        self._privileged_group = privileged_group

    def set_labels(self, labels):
        self._labels = labels

    def set_positive_label(self, positive_label):
        self._positive_label = positive_label

    def set_y_true(self, y_true):
        self._y_true = y_true

    def set_scores(self, scores):
        self._scores = scores
