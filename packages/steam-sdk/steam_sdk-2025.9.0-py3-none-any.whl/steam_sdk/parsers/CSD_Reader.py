'''
    CSD_reader file to to read PSPICE csd into Jupyter notebooks
    Mariusz Wozniak, CERN, July 2021
'''

import numpy as np
import re

class CSD_read():
    def __init__(self, csd_file_path):
        """
        Read csd file and returns it content as object attribute .data_dict that is a dictionary.
        :param csd_file_path: Full path to csd file, including file name and extension.
        """
        self.FILE_HEADER_KEYWORD = '#H'
        self.SIGNAL_HEADERS_KEYWORD = '#N'
        self.DATA_KEYWORD = '#C'
        self.END_KEYWORD = '#;'
        self.COMPLEX_VALUES_CHECK = "'COMPLEXVALUES='YES'"
        self.N_SIGNALS_KEYWORD = 'NODES='
        with open(csd_file_path) as f:
            self.contents = f.read()
        self.transient = self.__transient()
        self.header = self.__header()
        if self.transient == 'Transient Analysis':
            self.signal_names = self.__signal_names_transient()
            self.data, self.time = self.__data_transient()
        elif self.transient == 'AC Sweep':
            self.signal_names = self.__signal_names_AC()
            self.data, self.time = self.__data_AC()
        self.data_dict = {'Time': self.time}
        for i, name in enumerate(self.signal_names):
            self.data_dict[name] = self.data[:, i]
        self.__parsing_check()

    def __header(self):
        return self.contents[self.contents.find(self.FILE_HEADER_KEYWORD)+len(self.FILE_HEADER_KEYWORD):self.contents.find(self.SIGNAL_HEADERS_KEYWORD)]

    def __transient(self):
        return self.contents[self.contents.find('ANALYSIS')+10:self.contents.find('SERIALNO')-2]

    def __parsing_check(self):
        if self.header.find(self.COMPLEX_VALUES_CHECK) > 0:
            raise Exception('Complex values in the csd file. This can not be parsed with this parser.')
        nodes = int(re.split("'", self.header[self.header.find(self.N_SIGNALS_KEYWORD)+len(self.N_SIGNALS_KEYWORD):])[1])
        if self.transient == 'AC Sweep': nodes = nodes * 2
        if nodes != self.data.shape[1] or nodes != len(self.signal_names):
            raise Exception('Ups, something went wrong with parsing the file. The number of signals parsed does not match header specified number!')

    def __signal_names_transient(self):
        signal_string = self.contents[self.contents.find(self.SIGNAL_HEADERS_KEYWORD)+len(self.SIGNAL_HEADERS_KEYWORD):self.contents.find(self.DATA_KEYWORD)]
        signal_string = re.sub('\n', ' ', signal_string)
        signal_string = re.sub('\'', ' ', signal_string)
        signal_list = re.split(' ', signal_string)
        return list(filter(('').__ne__, signal_list))

    def __signal_names_AC(self):
        signal_string = self.contents[self.contents.find(self.SIGNAL_HEADERS_KEYWORD)+len(self.SIGNAL_HEADERS_KEYWORD):self.contents.find(self.DATA_KEYWORD)]
        signal_string = re.sub('\n', ' ', signal_string)
        signal_string = re.sub('\'', ' ', signal_string)
        signal_list = re.split(' ', signal_string)
        signal_list = list(filter(('').__ne__, signal_list))

        AC_signals = []
        for signal in signal_list:
            AC_signals = AC_signals + [f'Re_{signal}',f'Im_{signal}']
        return AC_signals


    def __data_transient(self):
        out_strs = self.contents[self.contents.find(self.DATA_KEYWORD)+len(self.DATA_KEYWORD):self.contents.find(self.END_KEYWORD)]
        out_strs = re.sub('\n', ' ', out_strs)
        out_strs = re.split(self.DATA_KEYWORD, out_strs)
        val_arr = []
        for line in out_strs:
            values = list(filter(('').__ne__, re.split(' ', line)))
            val_arr.append([float(value.split(':', 1)[0]) for value in values])
        for i in range(len(val_arr)):
            if len(val_arr[i])!=len(val_arr[0]):
                val_arr.pop(i)
        arr_out = np.array(val_arr)         # convert to np array
        time = arr_out[:, 0]                # extract time from the zero column
        arr_out = np.delete(np.array(val_arr),  np.s_[0:2], axis=1) # delete time vector at 0 column and number of data signals at 1st column
        return arr_out, time

    def __data_AC(self):
        out_strs = self.contents[self.contents.find(self.DATA_KEYWORD)+len(self.DATA_KEYWORD):self.contents.find(self.END_KEYWORD)]
        out_strs = re.sub('\n', ' ', out_strs)
        out_strs = re.split(self.DATA_KEYWORD, out_strs)
        val_arr = []
        for line in out_strs:
            values = list(filter(('').__ne__, re.split(' ', line)))
            ReImParts = [value.split(':', 1)[0].split('/') for value in values]
            ReImParts = [float(x) for xs in ReImParts for x in xs]
            val_arr.append(ReImParts)
        arr_out = np.array(val_arr)         # convert to np array
        freq = arr_out[:, 0]                # extract freq from the zero column
        arr_out = np.delete(np.array(val_arr),  np.s_[0:2], axis=1) # delete time vector at 0 column and number of data signals at 1st column
        return arr_out, freq

