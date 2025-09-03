import numpy as np
import pandas as pd
import copy
from scipy.stats import (
    truncnorm,
    truncexpon,
    uniform,
    beta,
    gamma,
    norm,
)


class Parameters:
    """
    A class representing a set of parameters.
    It takes keyword arguments representing the parameters with their values and wraps them into a python object.

    Parameters
    ----------
    **kwargs : dict
        Keyword arguments representing the parameters. 

    Returns
    -------
    Parameters
        A Parameters object, where each attributes is one of the keyword arguments
        provided for the function wrapped by the Value class.

    Examples
    --------
    >>> from cpm.generators import Parameters
    >>> parameters = Parameters(a=0.5, b=0.5, c=0.5)
    >>> parameters['a']
    0.1
    >>> parameters.a
    0.1
    >>> parameters()
    {'a': 0.1, 'b': 0.2, 'c': 0.5}

    The Parameters class can also provide a prior.

    >>> x = Parameters(
    >>>    a=Value(value=0.1, lower=0, upper=1, prior="normal", args={"mean": 0.5, "sd": 0.1}),
    >>>    b=0.5,
    >>>    weights=Value(value=[0.1, 0.2, 0.3], lower=0, upper=1, prior=None),
    >>> )

    >>> x.prior(log=True)
    -6.5854290732499186

    We can also sample new parameter values from the prior distributions.
    >>> x.sample()
    {'a': 0.4670755733417274, 'b': 0.30116207009111917}
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, Value):
                setattr(self, key, value)
            elif callable(value):
                # Create a static method on the class with the key as the method name
                setattr(self.__class__, key, staticmethod(value))
            elif value is None:
                setattr(self, key, None)
            else:
                setattr(self, key, Value(value))
        # self.__dict__.update(kwargs)

    def __getitem__(self, key):
        return self.__dict__.get(key)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __call__(self):
        return self.__dict__

    def __copy__(self):
        return Parameters(**self.__dict__)

    def __deepcopy__(self, memo):
        return Parameters(**copy.deepcopy(self.__dict__, memo))

    def __keys__(self):
        return self.__dict__.keys()

    def __len__(self):
        return 0

    # def __getattribute__(self, name):
    #     attr = object.__getattribute__(self, name)
    #     # Only deepcopy Value instances (not methods, etc.)
    #     if isinstance(attr, Value):
    #         return copy.deepcopy(attr)
    #     elif not callable(attr):
    #         return copy.deepcopy(attr)
    #     return attr

    def update(self, **kwargs):
        """
        Update the parameters with new values.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments representing the parameters.

        """
        for key, value in kwargs.items():
            if key in self.__dict__:
                self.__dict__[key].fill(value)

    def keys(self):
        """
        Return a list of all the keys in the parameters dictionary.

        Returns
        -------
        keys : list
            A list of all the keys in the parameters dictionary.
        """
        return self.__dict__.keys()

    def bounds(self):
        """
        Returns a tuple with lower (first element) and upper (second element) bounds for parameters with defined priors.

        Returns
        -------
        lower, upper: tuples
            A tuple of lower and upper parameter bounds
        """
        lower, upper = [], []
        for _, value in self.__dict__.items():
            if value is not None:
                if value.prior is not None:
                    lower.append(value.lower)
                    upper.append(value.upper)
        ## make sure to turn non-homogeneous arrays into flattened numpy arrays
        lower = np.concatenate([np.asarray(x).flatten() for x in lower])
        upper = np.concatenate([np.asarray(x).flatten() for x in upper])
        return lower, upper

    def PDF(self, log=False):
        """
        Return the prior probability density of the parameter values.

        Returns
        -------
        float
            The summed probability density of the parameter set under the prior distribution for each parameter. If `log` is True, the log probability is returned. When the PDF is 0, it returns the smallest positive float value. If `log` is True and the log probability is negative infinity, it returns the most negative float value.
        """
        prior = 0
        for _, value in self.__dict__.items():
            if value is not None:
                # Check if the value has a prior distribution
                # and if so, add its PDF to the prior
                if value.prior is not None:
                    prior += value.PDF(log=True)
        if np.isneginf(prior):
            prior = np.finfo(np.float64).min
        if not log:
            prior = np.exp(prior)
            if prior <= 0:
                prior = np.finfo(np.float64).tiny
        return prior

    def update_prior(self, **kwargs):
        """
        Update the prior distribution of all parameters.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments representing the parameters of the prior distribution. For each parameter, the keyword should be the name of the parameter and the value should be a dictionary of the parameters of the prior distribution. If you are unsure what the names are for the parameters of the prior distribution, you can check the `scipy.stats` documentation or the `prior.kwds` attribute.
        """
        for key, value in kwargs.items():
            if key in self.__dict__:
                self.__dict__[key].update_prior(**value)

    def sample(self, size=1, jump=False):
        """
        Sample and update parameter values from their prior distribution.

        Returns
        -------
        sample : dict
            A dictionary of the sampled parameters.
        """
        output = []
        for i in range(size):
            sample = {}
            for key, value in self.__dict__.items():
                if value.prior is not None:
                    if jump:
                        sample[key] = value.prior.rvs(loc=value.value)
                    else:
                        sample[key] = value.prior.rvs()
            output.append(sample)
        return output

    def free(self):
        """
        Return a dictionary of all parameters with a prior distribution.

        Returns
        -------
        free : dict
            A dictionary of all parameters with a prior distribution.
        """
        free = []
        for key, value in self.__dict__.items():
            if value is not None:
                if value.prior is not None:
                    free.append(key)
        return free

    def export(self):
        """
        Return all freely-varying parameters and their accompanying lower and upper bounds, and prior distributions.

        Returns
        -------
        pandas.DataFrame
            A table of all freely-varying parameters and their accompanying lower and upper bounds, and prior distributions. Each row is a parameter, and the columns are the lower bound, upper bound, prior distribution, and the parameters of the prior distribution.
        """
        table = pd.DataFrame()
        for key, value in self.__dict__.items():
            if value is not None:
                if value.prior is not None:
                    output = pd.Series(
                        {
                            "lower": value.lower,
                            "upper": value.upper,
                            "prior_fun": value.prior,
                            **value.prior.kwds,
                        }
                    )
                    output = output.to_frame().T
                    table = pd.concat([table, output], axis=0)
        table.index = self.free()
        return table


class Value:
    """

    The `Value` class is a wrapper around a float value, with additional details such as the prior distribution, lower and upper bounds. It supports all basic mathematical operations and can be used as a regular float with the parameter value as operand.

    Parameters
    ----------
    value : float
        The value of the parameter.
    lower : float, optional
        The lower bound of the parameter.
    upper : float, optional
        The upper bound of the parameter.
    prior : string or object, optional
        If a string, it should be one of continuous distributions from `scipy.stats`.
        See the [scipy documentation](https://docs.scipy.org/doc/scipy/reference/stats.html) for more details.
        The default is None.
        If an object, it should be or contain a callable function representing the prior distribution of the parameter with methods similar to `scipy.stats` distributions.
        See Notes for more details.
    args : dict, optional
        A dictionary of arguments for the prior distribution function.

    Notes
    -----
    We currently implement the following continuous distributions from `scipy.stats` corresponding to the `prior` argument:

    - 'uniform'
    - 'truncated_normal'
    - 'beta'
    - 'gamma'
    - 'truncated_exponential'
    - 'norm'

    Because these distributions are inherited from `scipy.stats`, see the [scipy documentation](https://docs.scipy.org/doc/scipy/reference/stats.html) for more details on how to update variables of the distribution.

    Returns
    -------
    Value
        A Value object, where each attribute is one of the arguments provided for the function. It support all basic mathematical operations and can be used as a regular float with the parameter value as operand.
    """

    def __init__(
        self,
        value=None,
        lower=0,
        upper=1,
        prior=None,
        args=None,
        **kwargs,
    ):
        self.value = value
        self.lower = lower
        self.upper = upper

        args = args if args is not None else {"a": 0, "b": 1, "mean": 0, "sd": 1}

        # set the prior distribution
        self.__pdef__ = prior

        if prior is None:
            self.prior = None
        if prior == "uniform":
            self.prior = uniform(loc=lower, scale=upper)
        elif prior == "truncated_normal":
            # calculate the bounds of the truncated normal distribution
            below, above = (lower - args.get("mean")) / args.get("sd"), (
                upper - args.get("mean")
            ) / args.get("sd")
            self.prior = truncnorm(
                loc=args.get("mean"), scale=args.get("sd"), a=below, b=above
            )
        elif prior == "beta":
            self.prior = beta(
                a=args.get("a"),
                b=args.get("b"),
                loc=args.get("mean"),
                scale=args.get("sd"),
            )
        elif prior == "gamma":
            self.prior = gamma(
                a=args.get("a"), loc=args.get("mean"), scale=args.get("sd")
            )
        elif prior == "truncated_exponential":
            self.prior = truncexpon(
                b=(upper - args.get("mean")) / args.get("sd"),
                loc=args.get("mean"),
                scale=args.get("sd"),
            )
        elif prior == "norm":
            self.prior = norm(loc=args.get("mean"), scale=args.get("sd"))
        elif callable(prior):
            self.prior = prior(**args)
        else:
            self.prior = prior

    def __repr__(self):
        return str(self.value)

    def __getitem__(self, key):
        return self.__dict__.get(key)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __update__(self, key, value):
        self.__dict__[key] = value

    def __call__(self):
        return self.__dict__

    def __str__(self):
        return str(self.__dict__)

    def export(self):
        return self.__dict__

    def __mul__(self, other):
        return self.value * other

    def __rmul__(self, other):  # other * self
        return self.value * other

    def __add__(self, other):
        return self.value + other

    def __radd__(self, other):  # other + self
        return self.value + other

    def __iadd__(self, other):
        return self.value + other

    def __sub__(self, other):  # self - other
        return self.value + (-other)

    def __rsub__(self, other):  # other - self
        return other + (-self.value)

    def __truediv__(self, other):
        return self.value / other

    def __floordiv__(self, other):
        return self.value // other

    def __mod__(self, other):
        return self.value % other

    def __pow__(self, other):
        return self.value**other

    def __rpow__(self, other):
        return other**self.value

    def __neg__(self):  # -self
        return self.value * -1

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __lt__(self, other):
        return self.value < other

    def __neg__(self):  # -self
        return self.value * -1

    def __truediv__(self, other):  # self / other
        return self.value * other**-1

    def __rtruediv__(self, other):  # other / self
        return other * self.value**-1

    def __copy__(self):
        return Value(**self.__dict__)

    def __array__(self) -> np.ndarray:
        return np.asarray(self.value)

    def __float__(self) -> float:
        return float(self.value)

    def __int__(self) -> int:
        return int(self.value)

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

    def __len__(self):
        return len(self.value)

    def __shape__(self):
        return np.shape(self.value)

    def __copy__(self):
        return Value(**self.__dict__)

    def __deepcopy__(self, memo):
        return Value(**copy.deepcopy(self.__dict__, memo))

    def copy(self):
        """
        Return a copy of the parameter.

        Returns
        -------
        Value
            A copy of the parameter.
        """
        return Value(**self.__dict__)

    def fill(self, value):
        """
        Replace the value of the parameter with a new value.

        Parameters
        ----------
        value : float or array_like
            The new value of the parameter.

        Notes
        -----
        If the parameter is an array, it should be a list of values. If the parameter is an array, and the new value is a single value, it will be broadcasted to the shape of the array.
        """
        self.value = value

    def PDF(self, log=False):
        """
        Return the prior distribution of the parameter.

        Returns
        -------
        float
            The probability of the parameter value under the prior distribution. If `log` is True, the log probability is returned.
        """
        if log:
            return self.prior.logpdf(self.value)
        else:
            return self.prior.pdf(self.value)

    def sample(self, size=1, jump=False):
        """
        Sample and update the parameter value from its prior distribution.

        Returns
        -------
        sample : float
            A sample from the prior distribution of the parameter.
        """
        if jump:
            new = self.prior.rvs(loc=self.value)
            self.fill(new)
        else:
            new = self.prior.rvs()
            self.fill(new)

    def update_prior(self, **kwargs):
        """
        Update the prior distribution of the parameter. Currently it is only implemented for truncated normal distributions.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments representing the parameters of the prior distribution. If you are unsure what the names are for the parameters of the prior distribution, you can check the `scipy.stats` documentation or the `prior.kwds` attribute.

        """

        # initialize updates with "loc" and "scale" parameters
        updates = {"loc": kwargs.get("mean"), "scale": kwargs.get("sd")}
        available_params = self.prior.kwds.keys()

        # check if "a" and "b" are both in `available_params`, and if so add to updates dict
        if "a" in available_params and "b" in available_params:
            updates["a"] = (self.lower - kwargs.get("mean")) / kwargs.get("sd")
            updates["b"] = (self.upper - kwargs.get("mean")) / kwargs.get("sd")

        # now, update the prior object
        self.prior.kwds.update(**updates)


class LogParameters(Parameters):
    """
    A class that represents parameters with logarithmic transformations.

    This class inherits from the `Parameters` class and provides methods to apply logarithmic transformations to the values of the parameters.

    Attributes
    ----------
    ...

    Methods
    -------
    log_transform()
        Apply a logarithmic transformation to the values of the parameters.
    log_exp_transform()
        Apply a logarithmic exponential transformation to the values of the parameters.

    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, Value):
                setattr(self, key, value)
            else:
                setattr(self, key, Value(value))
        self.log_transform()

    def __logit(self, value, lower, upper):
        """
        Function that transforms a value to a logit scale.
        """
        if value < lower or value > upper:
            raise ValueError("Value out of bounds.")
        elif value == lower:
            return -np.inf
        elif value == upper:
            return np.inf
        else:
            x = (value - lower) / (upper - lower)
            return np.log(x / (1 - x))

    def log_transform(self):
        """
        Apply a logarithmic transformation to the values of the parameters.

        This method iterates over the attributes of the object and checks if the attribute has a prior function and is an instance of the Value class. If both conditions are met, the value of the attribute is transformed using the logarithmic transformation function.

        """
        for _, value in self.__dict__.items():
            if value is not None:
                if value.prior is not None and isinstance(value, Value):
                    value.value = self.__logit(value.value, value.lower, value.upper)

    def log_inverse_transform(self):
        """
        Apply a logarithmic exponential transformation to the values of the parameters.

        This method iterates over the attributes of the object and checks if they are instances of the `Value` class.
        If an attribute is an instance of `Value` with a specified prior, the `value` attribute of that instance is transformed using the
        logarithmic exponential transformation function. The transformed value is then assigned
        back to the `value` attribute.

        Returns
        -------
        dict:
            A dictionary containing the updated attributes of the object.

        """

        output = []

        def _logexptransform(value, lower, upper):
            return lower + (upper - lower) * (1 / (1 + np.exp(-value)))

        out = {}

        for key, value in self.__dict__.items():
            if isinstance(value, Value) and value.prior is not None:
                out[key] = _logexptransform(value.value, value.lower, value.upper)
        return out

    def __revert(self):
        """
        Function to revert log transform of the parameters - for internal use only.
        """

        def _logexptransform(value, lower, upper):
            return lower + (upper - lower) * (1 / (1 + np.exp(-value)))

        for _, value in self.__dict__.items():
            if isinstance(value, Value) and value.prior is not None:
                value.value = _logexptransform(value.value, value.lower, value.upper)

    def update(self, log=False, **kwargs):
        """
        Update the parameters with new values.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments representing the parameters.

        """

        for key, value in kwargs.items():
            if key in self.__dict__:
                if self.__dict__[key].prior is not None and log:
                    value = self.__logit(
                        value, self.__dict__[key].lower, self.__dict__[key].upper
                    )
                self.__dict__[key].fill(value)

    def __copy__(self):
        self.__revert()
        return LogParameters(**self.__dict__)

    def __deepcopy__(self, memo):
        self.__revert()
        return LogParameters(**copy.deepcopy(self.__dict__, memo))

    def bounds(self):
        """
        Returns a tuple with lower (first element) and upper (second element) bounds for parameters with defined priors.

        Returns
        -------
        lower, upper: tuples
            A tuple of lower and upper parameter bounds
        """
        lower, upper = [], []
        for _, value in self.__dict__.items():
            if value is not None:
                if value.prior is not None:
                    if value.lower == 0:
                        lower.append(
                            self.__logit(value.lower + 1e-10, value.lower, value.upper)
                        )
                    else:
                        lower.append(self.__logit(value.lower, value.lower, value.upper))

                    upper.append(
                        self.__logit(value.upper - 1e-10, value.lower, value.upper)
                    )
        return lower, upper
