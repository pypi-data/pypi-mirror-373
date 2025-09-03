import sys
import matplotlib.pyplot as plt
import os

from IPython import get_ipython


def progressBar(value, endvalue, bar_length=20):
    """

        **Show a simple progress bar during calculation**

        Function updates the last printed line and visualizes a progress bar

        :param value: Value indicating the current progress
        :type value: float or int
        :param value: Value indicating the end of the process
        :type value: float or int
        :param bar_length: Length of characters used in the display window
        :type value: int
        :return:

        - Example :

        utils.progressBar(value=15, endvalue=50, bar_length=20) # 15/50=30%
        # >>> 					Status: [----->              ] 30%

    """

    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rStatus: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()


def isnotebook() -> bool:
    '''
        Function checks whether the script is run in a notebook or not
    '''
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True  # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def makeCopyFile(nameInputFile: str, nameOutputFile: str):
    """

        **Copy file (funtion also works when called from a notebook)**

        :param nameInputFile: Name of the original file (including path)
        :type nameInputFile: str
        :param nameOutputFile: Name of the new file (including path)
        :type nameOutputFile: str
        :return:

        - Example :

        utils.progressBar(value=15, endvalue=50, bar_length=20) # 15/50=30%
        # >>> 					Status: [----->              ] 30%

    """
    if os.path.isfile(nameInputFile):
        f = open(nameOutputFile, 'w')
        with open(nameInputFile) as inputfile:
            for line in inputfile:
                f.write(line)
        f.close()
    else:
        print("Copying ", str(nameInputFile), " failed. Not existing.")
        return


def displayWaitAndClose(waitTimeBeforeMessage: float, waitTimeAfterMessage: float = 0, flag_isnotebook: bool = isnotebook(), flag_show_text: bool = True):
    """

        **Function useful in Pycharm tests; it allows closing plots after some time that they are displayed **

        Wait a certain time, display a message, and wait a certain time

        :param waitTimeBeforeMessage: Time to wait before the message [s]
        :type waitTimeBeforeMessage: float
        :param waitTimeAfterMessage: Time to wait after the message [s]
        :type waitTimeAfterMessage: float
        :return:


    """

    if flag_isnotebook:
        plt.tight_layout()
        plt.show()
    else:
        # Show plots in Pycharm, wait a certain time, alert time is up, and close the window
        plt.ion()
        plt.tight_layout()
        plt.show()
        plt.draw()
        plt.pause(waitTimeBeforeMessage)
        if flag_show_text == True:
            plt.title('Figure will close in {} seconds...'.format(waitTimeAfterMessage))
        plt.pause(waitTimeAfterMessage)


def isnotebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter


def find_indices(a, func):
    '''
    From:
    https://stackoverflow.com/questions/5957470/matlab-style-find-function-in-python

    Function that takes a callable parameter which will be used in the condition part of a list comprehension.
    Then one can use a lambda or another function object to pass an arbitrary condition:

    Example:
    a = [1, 2, 3, 1, 2, 3, 1, 2, 3]
    inds = find_indices(a, lambda x: x > 2)
    inds --> [2, 5, 8]
    '''
    return [i for (i, val) in enumerate(a) if func(val)]