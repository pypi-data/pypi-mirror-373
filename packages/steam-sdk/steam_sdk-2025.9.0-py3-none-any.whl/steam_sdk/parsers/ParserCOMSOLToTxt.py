import pandas as pd

class ParserCOMSOLToTxt:

    def __init__(self, verbose=True):
        pass


    def loadTxtCOMSOL(self, txt_file_path: str, header: list = None):
        df = pd.read_csv(txt_file_path, sep="\s+|\t+|\s+\t+|\t+\s+", comment='%',  names=header, engine="python")
        return df

