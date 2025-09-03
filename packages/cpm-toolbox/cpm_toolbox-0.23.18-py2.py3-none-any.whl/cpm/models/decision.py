import numpy as np
import warnings
from ..generators import Value

__all__ = [
    "Softmax",
    "Sigmoid",
    "GreedyRule",
    "ChoiceKernel",
]


class Softmax:
    """
    Softmax class for computing policies based on activations and temperature.

        The softmax function is defined as: e^(temperature * x) / sum(e^(temperature * x)).

    Parameters
    ----------
    temperature : float
        The inverse temperature parameter for the softmax computation.
    xi : float
        The irreducible noise parameter for the softmax computation.
    activations : numpy.ndarray
        Array of activations for each possible outcome/action. It should be
        a 2D ndarray, where each row represents an outcome and each column
        represents a single stimulus.

    Notes
    -----

    The inverse temperature parameter beta represents the degree of randomness in the choice process.
    As beta approaches positive infinity, choices becomes more deterministic,
    such that the choice option with the greatest activation is more likely to be chosen - it approximates a step function.
    By contrast, as beta approaches zero, choices becomes random (i.e., the probabilities the choice options are approximately equal)
    and therefore independent of the options' activations.

    `activations` must be a 2D array, where each row represents an outcome and each column represents a stimulus or other arbitrary features and variables.
    If multiple values are provided for each outcome, the softmax function will sum these values up.

    Note that if you have one value for each outcome (i.e. a classical bandit-like problem), and you represent it as a 1D
    array, you must reshape it in the format specified for activations. So that if you have 3 stimuli
    which all are actionable, `[0.1, 0.5, 0.22]`, you should have a 2D array of shape (3, 1), `[[0.1], [0.5], [0.22]]`.
    You can see [Example 2]("./examples/examples2") for a demonstration.


    Examples
    --------
    >>> from cpm.models.decision import Softmax
    >>> import numpy as np
    >>> temperature = 5
    >>> activations = np.array([0.1, 0, 0.2])
    >>> softmax = Softmax(temperature=temperature, activations=activations)
    >>> softmax.compute()
    array([0.30719589, 0.18632372, 0.50648039])
    >>> softmax.choice() # This will randomly choose one of the actions based on the computed probabilities.
    2  
    >>> Softmax(temperature=temperature, activations=activations).compute()
    array([0.30719589, 0.18632372, 0.50648039])
    """

    def __init__(self, temperature=None, xi=None, activations=None, **kwargs):
        """ """
        self.temperature = temperature
        if isinstance(self.temperature, Value):
            self.temperature = self.temperature.value
        self.xi = xi
        if isinstance(self.xi, Value):
            self.xi = self.xi.value
        if activations is not None:
            self.activations = activations.copy()
        else:
            self.activations = np.zeros(1)
        self.policies = np.zeros(self.activations.shape[0])
        self.shape = self.activations.shape
        if len(self.shape) > 1:
            self.activations = self.activations.flatten()
            self.shape = self.activations.shape
            warnings.warn(
                "Activations should be a 1D array, but a 2D array was provided. "
                "Flattening the activations to a 1D array."
            )
            

        self.__run__ = False

    def compute(self):
        """
        Compute the policies based on the activations and temperature.

        Returns
        -------
        numpy.ndarray: Array of computed policies.
        """
        output = np.exp(self.activations * self.temperature) / np.sum(
            np.exp(self.activations * self.temperature)
        )
        self.policies = output
        self.__run__ = True
        return self.policies

    def irreducible_noise(self):
        """
        Extended softmax class for computing policies based on activations, with parameters inverse temperature and irreducible noise.

        The softmax function with irreducible noise is defined as:

            (e^(beta * x) / sum(e^(beta * x))) * (1 - xi) + (xi / length(x)),

        where x is the input array of activations, beta is the inverse temperature parameter, and xi is the irreducible noise parameter.

        Notes
        -----

        The irreducible noise parameter xi accounts for attentional lapses in the choice process.
        Specifically, the terms (1-xi) + (xi/length(x)) cause the choice probabilities to be proportionally scaled towards 1/length(x).
        Relatively speaking, this increases the probability that an option is selected if its activation is exceptionally low.
        This may seem counterintuitive in theory, but in practice it enables the model to capture highly surprising responses that can occur during attentional lapses.

        Returns
        -------
        numpy.ndarray: Array of computed policies with irreducible noise.

        Examples
        --------
        >>> activations = np.array([[0.1, 0, 0.2], [-0.6, 0, 0.9]])
        >>> noisy_softmax = Softmax(temperature=1.5, xi=0.1, activations=activations)
        >>> noisy_softmax.irreducible_noise()
        array([0.4101454, 0.5898546])
        """
        if self.__run__:
            policies = self.policies
        else:
            policies = self.compute()
        policies = policies * (1 - self.xi) + (self.xi / self.shape[0])
        self.policies = policies
        return policies

    def choice(self):
        """
        Choose an action based on the computed policies.

        Returns
        -------
        int: The chosen action based on the computed policies.
        """
        if not self.__run__:
            self.compute()
        return np.random.choice(self.policies.shape[0], p=self.policies.flatten())

    def __call__(self):
        return self.compute()


class Sigmoid:
    """
    A class representing a sigmoid function that takes an n by m array of activations and returns an n
    array of outputs, where n is the number of output and m is the number of
    inputs.

        The sigmoid function is defined as: 1 / (1 + e^(-temperature * (x - beta))).

    Parameters
    ----------
    temperature : float
        The inverse temperature parameter for the sigmoid function.
    beta : float
        It is the value of the output activation that results in an output rating
        of P = 0.5.
    activations : ndarray
        An array of activations for the sigmoid function.

    Examples
    --------
    >>> from cpm.models.decision import Sigmoid
    >>> import numpy as np
    >>> temperature = 7
    >>> activations = np.array([[0.1, 0.2]])
    >>> sigmoid = Sigmoid(temperature=temperature, activations=activations)
    >>> sigmoid.compute()
    array([[0.66818777, 0.80218389]])

    """

    def __init__(self, temperature=None, activations=None, beta=0, **kwargs):
        self.temperature = temperature
        self.beta = beta
        self.activations = np.asarray(activations.copy())
        self.policies = []
        self.shape = self.activations.shape
        if len(self.shape) > 1:
            self.activations = self.activations.flatten()
            self.shape = self.activations.shape
            warnings.warn(
                "Activations should be a 1D array, but a 2D array was provided. "
                "Flattening the activations to a 1D array."
            )
        self.__run__ = False

    def compute(self):
        """
        Computes the Sigmoid function.

        Returns
        -------
        output: ndarray
            A 2D array of outputs computed using the sigmoid function.
        """
        output = 1 / (
            1
            + np.exp((self.activations - self.beta) * -self.temperature)
        )
        self.policies = output
        self.__run__ = True
        return output

    def choice(self):
        """
        Chooses the action based on the sigmoid function.

        Returns
        -------
        action: int
            The chosen action based on the sigmoid function.

        Notes
        -----
        The choice is based on the probabilities of the sigmoid function, but it is not
        guaranteed that the policy values will sum to 1. Therefore, the policies
        are normalised to sum to 1 when generating a discrete choice.
        """
        if not self.__run__:
            self.compute()
        return np.random.choice(self.shape[0], p=self.policies / self.policies.sum())

    def __call__(self):
        return self.compute()


class GreedyRule:
    """
    A class representing an ε-greedy rule based on Daw et al. (2006).

    Parameters
    ----------
    activations : ndarray
        An array of activations for the greedy rule.
    epsilon : float
        Exploration parameter. The probability of selecting a random action.

    Attributes
    ----------
    activations : ndarray
        An array of activations for the greedy rule.
    epsilon : float
        Exploration parameter. The probability of selecting a random action.
    policies : ndarray
        An array of outputs computed using the greedy rule.
    shape : tuple
        The shape of the activations array.

    References
    ----------
    Daw, N. D., O’Doherty, J. P., Dayan, P., Seymour, B., & Dolan, R. J. (2006). Cortical substrates for exploratory decisions in humans. Nature, 441(7095), Article 7095. https://doi.org/10.1038/nature04766
    """

    def __init__(self, activations=None, epsilon=0, **kwargs):
        self.activations = np.asarray(activations.copy())
        self.epsilon = epsilon
        self.policies = []
        self.shape = self.activations.shape
        if len(self.shape) == 1:
            self.shape = (1, self.shape[0])
        self.run = False

    def compute(self):
        """
        Computes the greedy rule.

        Returns
        -------
        output: ndarray
            A 2D array of outputs computed using the greedy rule.
        """
        output = self.activations.sum(axis=1)
        policies = np.zeros(output.shape)
        maximum = np.max(output)
        policies[output != maximum] = self.epsilon * 1
        policies[output == maximum] = 1 - (output.shape[0] - 1) * self.epsilon
        policies[output <= 0] = 0
        if np.all(policies == 0):
            policies.fill(1 / policies.shape[0])
        else:
            policies = policies / policies.sum()  # normalise
        self.policies = policies
        self.run = True
        return self.policies

    def choice(self):
        """
        Chooses the action based on the greedy rule.

        Returns
        -------
        action: int
            The chosen action based on the greedy rule.
        """
        if not self.run:
            self.compute()
        out = np.random.choice(self.shape[0], p=self.policies)
        return out

    def config(self):
        """
        Returns the configuration of the greedy rule.

        Returns
        -------
        config: dict
            A dictionary containing the configuration of the greedy rule.

            - activations (ndarray): An array of activations for the greedy rule.
            - name (str): The name of the greedy rule.
            - type (str): The class of function it belongs.
        """
        config = {
            "activations": self.activations,
            "name": self.__class__.__name__,
            "type": "decision",
        }
        return config

    def __repr__(self):
        return f"{self.__class__.__name__}(activations={self.activations}, epsilon={self.epsilon})"

    def __str__(self):
        return f"{self.__class__.__name__}(activations={self.activations}, epsilon={self.epsilon})"

    def __call__(self):
        return self.compute()


class ChoiceKernel:
    """
    A class representing a choice kernel based on a softmax function that incorporates the frequency of choosing an action.
    It is based on Equation 7 in Wilson and Collins (2019).

    Parameters
    ----------
    temperature_activations : float
        The inverse temperature parameter for the softmax computation.
    temperature_kernel : float
        The inverse temperature parameter for the kernel computation.
    activations : ndarray, optional
        An array of activations for the softmax function.
    kernel : ndarray, optional
        An array of kernel values for the softmax function.

    Notes
    -----

    In order to get Equation 6 from Wilson and Collins (2019), either set `activations` to None (default) or set it to 0.

    See Also
    --------
    [cpm.models.learning.KernelUpdate][cpm.models.learning.KernelUpdate]: A class representing a kernel update (Equation 5; Wilson and Collins, 2019) that updates the kernel values.

    References
    ----------
    Wilson, R. C., & Collins, A. G. E. (2019). Ten simple rules for the computational modeling of behavioral data. eLife, 8, Article e49547.

    Examples
    --------
    >>> activations = np.array([[0.1, 0, 0.2], [-0.6, 0, 0.9]])
    >>> kernel = np.array([0.1, 0.9])
    >>> choice_kernel = ChoiceKernel(temperature_activations=1, temperature_kernel=1, activations=activations, kernel=kernel)
    >>> choice_kernel.compute()
    array([0.44028635, 0.55971365])

    """

    def __init__(
        self,
        temperature_activations=0.5,
        temperature_kernel=0.5,
        activations=None,
        kernel=None,
        **kwargs,
    ):
        self.temperature_a = temperature_activations
        self.temperature_k = temperature_kernel
        self.activations = activations.copy()
        self.kernel = kernel.copy()
        self.policies = []
        if activations is None:
            self.activations = np.zeros(1)
        self.shape = self.kernel.shape
        self.run = False

    def compute(self):
        output = np.zeros(self.shape[0])
        values = self.activations * self.temperature_a
        kernels = self.kernel * self.temperature_k
        # activation of output unit for action/outcome
        nominator = np.exp(np.sum(values, axis=1) * kernels)
        # denominator term for scaling
        denominator = np.sum(np.exp(np.sum(values, axis=1) * kernels))
        output = nominator / denominator
        self.policies = output
        self.run = True
        return output

    def choice(self):
        if not self.run:
            self.compute()
        return np.random.choice(self.shape[0], p=self.policies)

    def __call__(self):
        return self.compute()
