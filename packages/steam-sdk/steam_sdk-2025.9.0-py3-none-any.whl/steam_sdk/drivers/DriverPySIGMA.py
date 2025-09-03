import os
import subprocess
import pandas as pd
from steam_sdk.parsers.ParserCOMSOLToTxt import ParserCOMSOLToTxt
from steam_pysigma.MainPySIGMA import MainPySIGMA


class DriverPySIGMA:
    """
        Class to drive SIGMA models
    """

    def __init__(self, path_input_folder):
        self.path_input_folder = path_input_folder

    def run_PySIGMA(self, magnet_name):
        sigma_obj = MainPySIGMA(model_folder=self.path_input_folder)
        sigma_obj.run_pysigma(magnet_name)






