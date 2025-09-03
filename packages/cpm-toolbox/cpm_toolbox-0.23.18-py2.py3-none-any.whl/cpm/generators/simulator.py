"""
Runs a simulation for each ppt in the data.
"""

import numpy as np
import pandas as pd
import copy
import pickle as pkl
import warnings

from .parameters import Parameters
from ..core.data import unpack_participants
from ..core.generators import cast_parameters
from ..core.exports import simulation_export


class Simulator:
    """
    A `Simulator` class for a model in the CPM toolbox. It is designed to run a model for **multiple** participants and store the output in a format that can be used for further analysis.

    Parameters
    ----------
    wrapper : Wrapper
        An initialised Wrapper object for the model.
    data : pandas.core.groupby.generic.DataFrameGroupBy or list of dictionaries
        The data required for the simulation.
        If it is a pandas.core.groupby.generic.DataFrameGroupBy, as returned by `pandas.DataFrame.groupby()`, each group must contain the data (or environment) for a single participant.
        If it is a list of dictionaries, each dictionary must contain the data (or environment) for a single participant.
    parameters : Parameters, pd.DataFrame, pd.Series or list
        The parameters required for the simulation. It can be a Parameters object or a list of dictionaries whose length is equal to data. If it is a Parameters object, Simulator will use the same parameters for all simulations. It is a list of dictionaries, it will use match the parameters with data, so that for example parameters[6] will be used for the simulation of data[6].

    Returns
    -------
    simulator : Simulator
        A Simulator object.

    """

    def __init__(self, wrapper=None, data=None, parameters=None):
        self.wrapper = wrapper
        self.data = data

        self.groups = None
        self.__run__ = False
        self.__pandas__ = isinstance(data, pd.api.typing.DataFrameGroupBy)
        self.__parameter__pandas__ = isinstance(parameters, pd.DataFrame)
        if isinstance(self.__pandas__, pd.DataFrame):
            raise TypeError(
                "Data should be a pandas.DataFrameGroupBy object, not a pandas.DataFrame."
            )
        if self.__pandas__:
            self.groups = list(self.data.groups.keys())
        else:
            self.groups = np.arange(len(self.data))
        self.parameters = cast_parameters(parameters, len(self.groups))
        self.parameter_names = self.wrapper.parameter_names

        if len(self.groups) != len(parameters):
            raise ValueError(
                "The number of groups in the data and parameters should be equal."
            )

        self.simulation = pd.DataFrame()
        self.generated = []

    def run(self):
        """
        Runs the simulation.

        Note
        ----
        Data is sorted according to the group IDs as ordered by pandas.

        """

        for i in range(len(self.groups)):
            self.wrapper.reset()
            evaluate = copy.deepcopy(self.wrapper)
            ppt_data = unpack_participants(
                self.data, i, self.groups, pandas=self.__pandas__
            )
            ppt_parameter = unpack_participants(
                self.parameters, i, self.groups, pandas=self.__parameter__pandas__
            )
            evaluate.reset(parameters=ppt_parameter, data=ppt_data)
            evaluate.run()
            output = copy.deepcopy(evaluate.export())
            output["ppt"] = self.groups[i]
            self.simulation = pd.concat([self.simulation, output], axis=0)
            del evaluate, output

        self.simulation.reset_index(drop=True, inplace=True)
        self.__run__ = True
        return None

    def export(self, save=False, path=None):
        """
        Return the trial- and participant-level information about the simulation.

        Parameters
        ----------

        save : bool
            If True, the output will be saved to a file.
        path : str
            The path to save the output to.

        Returns
        ------
        pandas.DataFrame
            A dataframe containing the the model output for each participant and trial.
            If the output variable is organised as an array with more than one dimension, the output will be flattened.
        """
        ## check whether the simulation has been run
        if not self.__run__:
            raise ValueError("The simulation has not been run yet.")
        ## export the simulation to file
        if save:
            if path is None:
                raise ValueError("Please provide a path to save the output.")
            self.simulation.to_csv(path)
        return self.simulation

    def update(self, parameters=None):
        """
        Updates the parameters of the simulation.
        """
        if isinstance(parameters, Parameters):
            raise TypeError("Parameters must be a dictionary or array_like.")
        ## if parameters is a single set of parameters, then repeat for each ppt
        if isinstance(parameters, dict):
            self.parameters = [
                (copy.deepcopy(parameters)) for i in range(1, len(self.data) + 1)
            ]
        if isinstance(parameters, list) or isinstance(parameters, np.ndarray):
            self.parameters = parameters
        return None

    def generate(self, variable="dependent"):
        """
        Generate data for parameter recovery, etc.

        Parameters
        ----------
        variable: str
            Name of the variable to pull out from model output.
        """
        if not self.__run__:
            raise ValueError("The simulation has not been run yet.")
            
        append = []
        # Group by participant
        for ppt_id, ppt_data in self.simulation.groupby("ppt"):
            # Get the length of trials for this participant
            n_trials = len(ppt_data)
            # Create the observation container
            one = {"observed": np.zeros((n_trials, 1))}
            # Extract the variable values for this participant
            one["observed"][:, 0] = ppt_data[variable].values
            append.append(one)
        
        self.generated = copy.deepcopy(append)
        return None

    def reset(self):
        """
        Resets the simulation.
        """
        self.simulation = pd.DataFrame()
        self.generated = []
        self.__run__ = False
        return None

    def save(self, filename=None):
        """
        Saves the simulation results.

        Parameters
        ----------
        filename : str
            The name of the file to save the results to.
        """
        if filename is None:
            filename = "simulation"
        pkl.dump(self, open(filename + ".pkl", "wb"))
        return None
