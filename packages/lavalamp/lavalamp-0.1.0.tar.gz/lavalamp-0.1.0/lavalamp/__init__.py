import numpy as np
import lavalamp.plot



SAMPLE_SIZE = 1e6
DISP_SAMPLE_AMOUNT = 7



class Base_Lavalamp:
    """
    Base_Lavalamp is the base class for representing random numbers.
    
    The class provides methods for arithmetic operations, statistical properties,
    and comparisons. Should not be instantiated directly.
    
    Parameters
    ----------
    values : np.ndarray
        Array of sampled values representing the distribution.
    """

    def __init__(self, values):
        """
        Initialize a Base_Lavalamp instance.

        Parameters
        ----------
        values : np.ndarray
            Array of sampled values representing the distribution.
        """
        self.values = values
        self.label = ''

    def __add__(self, other):
        if isinstance(other, Base_Lavalamp):
            values = other.values
        else:
            values = other
        return Base_Lavalamp(self.values + values)

    def __sub__(self, other):
        if isinstance(other, Base_Lavalamp):
            values = other.values
        else:
            values = other
        return Base_Lavalamp(self.values - values)

    def __mul__(self, other):
        if isinstance(other, Base_Lavalamp):
            values = other.values
        else:
            values = other
        return Base_Lavalamp(self.values * values)

    def __truediv__(self, other):
        if isinstance(other, Base_Lavalamp):
                values = other.values
        else:
            values = other
        return Base_Lavalamp(self.values / values)

    def __pow__(self, other):
        if isinstance(other, Base_Lavalamp):
            values = other.values
        else:
            values = other
        return Base_Lavalamp(np.power(self.values, values))

    def __array_ufunc__(self, ufunc, *args):
        # print(ufunc, *args)
        # return 1
        return Base_Lavalamp(ufunc(self.values))

    def __iadd__(self, other):
        return self.__add__(other)

    def __isub__(self, other):
        return self.__sub__(other)

    def __imul__(self, other):
        return self.__mul__(other)

    def __itruediv__(self, other):
        return self.__truediv__(other)

    def __ipow__(self, other):
        return self.__pow__(other)

    def __radd__(self, other):
        return Base_Lavalamp(other + self.values)

    def __rsub__(self, other):
        return Base_Lavalamp(other - self.values)

    def __rmul__(self, other):
        return Base_Lavalamp(other * self.values)

    def __rtruediv__(self, other):
        return Base_Lavalamp(other / self.values)

    def __rpow__(self, other):
        return Base_Lavalamp(other ** self.values)

    def __neg__(self):
        return Base_Lavalamp(-self.values)

    def __abs__(self):
        return Base_Lavalamp(np.abs(self.values))
    
    def __eq__(self, value):
        return Boolean(self.values == value.values)
    
    def __invert__(self):
        return Boolean(~self.values)

    def __lt__(self, value):
        if isinstance(value, Base_Lavalamp):
            return np.count_nonzero(self.values<value.values) / len(self.values)
        return np.count_nonzero(self.values<value) / len(self.values)

    def __le__(self, value):
        if isinstance(value, Base_Lavalamp):
            return np.count_nonzero(self.values<=value.values) / len(self.values)
        return np.count_nonzero(self.values<=value) / len(self.values)

    def __gt__(self, value):
        if isinstance(value, Base_Lavalamp):
            return np.count_nonzero(self.values>value.values) / len(self.values)
        return np.count_nonzero(self.values>value) / len(self.values)

    def __ge__(self, value):
        if isinstance(value, Base_Lavalamp):
            return np.count_nonzero(self.values>=value.values) / len(self.values)
        return np.count_nonzero(self.values>=value) / len(self.values)

    def __str__(self):
        n = DISP_SAMPLE_AMOUNT
        sampled_values = self.values[0:n].tolist()
        # string = '  '.join([f'{x:.1f}' for x in sampled_values])
        string = '  '.join([number_formatter(x) for x in sampled_values])
        if n < self.values.size:
            string += ' ...'
        return string

    __repr__ = __str__

    def __call__(self, key):
        if type(key) not in (int, float):
            raise ValueError("Input must be a number")
        return self.quantile(key)

    def __getitem__(self, index):
        return self.values[index]

    def quantile(self, quantile_value):
        return np.quantile(self.values, quantile_value)

    @property
    def mean(self):
        return float(self.values.mean())

    @property
    def std(self):
        return float(self.values.std())

    @property
    def max(self):
        return float(self.values.max())

    @property
    def min(self):
        return float(self.values.min())

    @property
    def median(self):
        return float(np.median(self.values))

    @property
    def mode(self):
        hist, hist_edges = np.histogram(self.values, bins=histogram_bins)
        mode_index = np.argmax(hist)
        return float(hist_edges[mode_index:mode_index+2].mean())

    def top(self, value_count):
        sorted_indices = np.argsort(self.values)
        return np.flip(sorted_indices[-value_count:])

    def bottom(self, value_count):
        sorted_indices = np.argsort(self.values)
        return sorted_indices[0:value_count]
    

# Continuous Distributions
class Normal(Base_Lavalamp):

    def __init__(self, mean, st_dev, label=None):
        self.type = 'Continuous'
        values = np.random.normal(loc=mean, scale=st_dev, size=(int(SAMPLE_SIZE),))
        if label:
            self.label = label
        super().__init__(values)


class LogNormal(Base_Lavalamp):

    def __init__(self, mean, st_dev, label=None):
        self.type = 'Continuous'
        values = np.random.lognormal(mean=mean, sigma=st_dev, size=(int(SAMPLE_SIZE),))
        if label:
            self.label = label
        super().__init__(values)


class Rectangular(Base_Lavalamp):

    def __init__(self, low, high, label=None):
        self.type = 'Continuous'
        values = np.random.uniform(low=low, high=high, size=(int(SAMPLE_SIZE),))
        if label:
            self.label = label
        super().__init__(values)


# Discrete Distributions
class DiscreteUniform(Base_Lavalamp):

    def __init__(self, values, label=None):
        self.type = 'Discrete'
        values = np.random.choice(values, size=(int(SAMPLE_SIZE),))
        if label:
            self.label = label
        super().__init__(values)


class Die(Base_Lavalamp):

    def __init__(self, sides=6, label=None):
        self.type = 'Discrete'
        values = np.random.choice(np.arange(1, sides + 1), size=(int(SAMPLE_SIZE),))
        if label:
            self.label = label
        super().__init__(values)


class Unfair_Die(Base_Lavalamp):

    def __init__(self, probabilities=None, weights=None, label=None):
        self.type = 'Discrete'
        if probabilities is not None:
            self.probabilities = np.array(probabilities)
            if sum(probabilities) != 1:
                raise ValueError("Probabilities must sum to 1.")
        elif weights is not None:
            self.probabilities = np.array(weights) / sum(weights)
        else:
            raise ValueError("Either probabilities or weights must be provided.")
        
        sides = len(self.probabilities)
        values = np.random.choice(np.arange(1, sides + 1), size=(int(SAMPLE_SIZE),), p=self.probabilities)
        if label:
            self.label = label
        super().__init__(values)


class Boolean(Base_Lavalamp):
    def __init__(self, values):
        self.type = 'Discrete'
        super().__init__(values)

    def __str__(self):
        return f'{self > 0}'

# vectorisation wrapper
def ready(func):
    # @functools.wraps(func)
    def wrapper():
        vectorized_func = np.frompyfunc(func, 1, 1)
        return vectorized_func
    return wrapper()


# other functions
def number_formatter(value):

    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        if abs(value) > 10:
            return f'{value:.1f}'
        else:
            return f'{value:.2f}'

