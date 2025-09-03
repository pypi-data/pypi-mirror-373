import numpy as np
from pathlib import Path


class ParserCond2d:
    def __init__(self, conductor, block, xyCorner):
        self.conductor = conductor
        self.block = block
        self.xyCorner = xyCorner

    def toString(self):
        xyCornerStr = "("
        for row in self.xyCorner:
            xyCornerStr += "[{}, {}], ".format(row[0], row[1])
        xyCornerStr += ")"

        return "{}, {}, {}".format(self.conductor, self.block, xyCornerStr)


def getConductorPositionsFromInputFile(fileNameCond2d: Path):
    """
        Read input file and return list of ConductorPosition objects

        # input: fileName
        # output: conductorPositionsList

    """
    # conductorStartKeyword = "CONDUCTOR POSITION IN THE CROSS-SECTION"
    blockStartKeyword = "BLOCK POSITION IN THE CROSS-SECTION"

    fileContent = open(fileNameCond2d, "r").read()

    # separate rows
    fileContentByRow = fileContent.split("\n")

    # Find block definition
    for i in range(len(fileContentByRow)):
        if blockStartKeyword in fileContentByRow[i]:
            startOfBlockDefinitionIndex = i

    # separate part of the data with conductor position information
    conductorPositions = fileContentByRow[5:startOfBlockDefinitionIndex - 2]

    # drop every 5th row
    conductorPositionsFourVertices = list(conductorPositions)
    del conductorPositionsFourVertices[4::5]

    # arrange data in a list of lists
    outputConductorPositions = []
    for row in conductorPositionsFourVertices:
        rowSplitStr = row.split(',')
        rowSplitFloat = [float(elem) for elem in rowSplitStr]
        outputConductorPositions.append(rowSplitFloat)

    # arrange data from list to numpy.array
    outputConductorPositionsMatrix = np.array(outputConductorPositions)

    # input: outputConductorPositions
    # output: conductorPositionsList
    conductorPositionsList = []
    for i in range(0, len(outputConductorPositions), 4):
        out = outputConductorPositions[i]
        conductor = int(out[1])
        block = int(out[2])
        xyCorner = outputConductorPositionsMatrix[i:i + 4, 4:6]
        conductorPositionsList.append(ParserCond2d(conductor, block, xyCorner))

    return conductorPositionsList
