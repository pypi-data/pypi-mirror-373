import numpy as np

from steam_sdk.utils.misc import progressBar, find_indices


class SelfMutualInductanceCalculation:
    mu0 = 4 * np.pi / 10 ** 7
    EPS = 1e-12

    def __init__(self, x, y, polarities, Ns, Ds, strandToHalfTurn, strandToCoilSection, flag_strandCorrection=0,
                 flag_sumTurnToTurn=1, flag_writeOutput=0, nameMagnet='', verbose: str = False):
        self.nameMagnet = nameMagnet
        self.x = x
        self.y = y
        self.polarities = polarities
        self.Ns = Ns
        self.Ds = Ds
        self.strandToHalfTurn = strandToHalfTurn
        self.flag_strandCorrection = flag_strandCorrection
        self.flag_sumTurnToTurn = flag_sumTurnToTurn
        self.flag_writeOutput = flag_writeOutput
        self.verbose = verbose

    def getNameMagnet(self):
        return self.nameMagnet

    def calculateStrandInductance(self, x, y, polarities, Ns, Ds, strandToHalfTurn):
        """

            **Calculates self-mutual inductances per unit length between strands in a 2D cross-section**

            Function returns an array with self-mutual inductances between strands in [H/m]

            :param x: X-positions of the strands in [m]; one element per strand
            :type x: numpy.ndarray
            :param y: X-positions of the strands in [m]; one element per strand
            :type y: numpy.ndarray
            :param polarities: Polarity of the current through each strand, +-1; one element per strand
            :type polarities: numpy.ndarray
            :param Ns: Number of number of strands in each half-turn [-]; one element per half-turn
            :type Ns: numpy.ndarray
            :param Ds: Diameter of each strand in [m]; one element per strand
            :type Ds: numpy.ndarray
            :param strandToHalfTurn: Vector indicating in which conductor each strand is located [-]
            :type strandToHalfTurn: numpy.ndarray
            :return: numpy.ndarray

            - Example :

            import numpy as np

            # Example to be written

            # Example output to be written
            # >>> 					Example output

        """

        # Define constants
        mu0 = self.mu0
        EPS = self.EPS

        # Calculate number of strands
        nStrands = np.size(x)

        # Only consider the sign of the vector with current polarities
        polarities = np.sign(polarities)

        # Calculate self-mutual inductance between strands
        oneTwentiethStrands = np.round(nStrands / 20)  # This is used only to show progress during the calculation
        if self.verbose: print('Self-mutual inductance between strands - Calculation started')
        if self.flag_strandCorrection == 0:
            if self.verbose: print('Calculation does not include correction for strand diameter.')
            M_strands = np.zeros((nStrands, nStrands))
            # Calculate mutual inductances between strands
            for p1 in range(nStrands):
                if self.verbose and p1 % oneTwentiethStrands == 0:
                    progressBar(p1, nStrands, bar_length=20)
                M_strands[p1, :] = -np.sign(polarities[p1]) / Ns[strandToHalfTurn[p1] - 1] * np.sign(polarities[:]) / \
                                   Ns[strandToHalfTurn[:] - 1] * mu0 / 2 / np.pi * np.log(
                    (((x[p1] - x[:]) ** 2 + (y[p1] - y[:]) ** 2) ** .5 + EPS) / Ds[:])
            # Correct the elements on the diagonal
            idxDiagStrands = np.diag_indices(nStrands)
            M_strands[idxDiagStrands] = mu0 / np.pi / 8 / Ns[strandToHalfTurn[:] - 1]
        else:
            raise Exception('Calculation including correction for strand diameter is currently not supported.')
        #         print('Calculation includes correction for strand diameter.')
        #         # Initialization
        #         M_strands = np.zeros((nStrands,nStrands))
        #         # Calculate mutual inductances between strands
        #         for p1 in range(nStrands):
        #             if p1 % oneTwentiethStrands == 0:
        #                 print('Progress: ' + str(p1) + '/' + str(nStrands))
        #             M_strands[p1,:]=-np.sign(polarities[p1])/Ns[strandToHalfTurn[p1]-1]*np.sign(polarities[:])/Ns[strandToHalfTurn[:]-1]*mu0/2/np.pi*np.log((((x[p1]-x[:])**2+(y[p1]-y[:])**2)**.5-Ds[:]+EPS)/Ds[:])
        #         # Correct the elements on the diagonal
        #         idxDiagStrands = np.diag_indices(nStrands)
        #         M_strands[idxDiagStrands]=mu0/np.pi/8/Ns[strandToHalfTurn[:]-1]

        if self.verbose:
            progressBar(1, 1, bar_length=20)
            print('')
            print('Self-mutual inductance between strands - Calculation finished')
        return M_strands

    def calculateHalfTurnInductance(self, M_strands, strandToHalfTurn):
        if self.verbose: print('Self-mutual inductance between half-turns - Calculation started')

        # Calculate self-mutual inductance between half-turns
        M_halfTurns = self.sumMatrixElements(M_strands, strandToHalfTurn)

        if self.verbose: print('Self-mutual inductance between half-turns - Calculation finished')
        return M_halfTurns

    def calculateTurnInductance(self, M_halfTurns):
        if self.verbose: print('Self-mutual inductance between turns - Calculation started')

        # Calculate number of turns
        # THIS ASSUMES THAT THE SECOND HALF OF THE HALF-TURNS ARE THE RETURN LINES OF THE FIRST HALF
        nTurns = int(np.size(M_halfTurns[0]) / 2)
        halfTurnToTurn = np.tile(np.arange(1, nTurns + 1), 2)

        # Calculate self-mutual inductance between turns
        M_turns = self.sumMatrixElements(M_halfTurns, halfTurnToTurn)

        if self.verbose: print('Self-mutual inductance between turns - Calculation finished')
        return M_turns

    def calculateCoilSectionInductance(self, M_strands, strandToCoilSection):
        # Calculate self-mutual inductance between coil sections
        M_coilSections = self.sumMatrixElements(M_strands, strandToCoilSection)
        return M_coilSections

    def calculateTotalInductance(self, M_strands):
        # Calculate total magnet self-inductance
        L_mag0 = np.sum(M_strands)
        return L_mag0

    def sumMatrixElements_OLD(self, M, indexToGroup):
        nGroups = np.max(indexToGroup)

        # Calculate self-mutual inductance between half-turns
        M_sum = np.empty((nGroups, nGroups))
        for g1 in range(nGroups):
            idxG1 = np.where(indexToGroup == g1 + 1)[0]
            for g2 in range(nGroups):
                idxG2 = np.where(indexToGroup == g2 + 1)[0]
                M_sum[g1, g2] = np.sum(M[idxG1[:, None], idxG2])

        return M_sum

    def sumMatrixElements_OLD(self, M, indexToGroup):
        nGroups = np.max(indexToGroup)

        # Pre-calculate indices
        idxG = []  # initialize an empty list taht will be filled with np.arrays
        for g in range(nGroups):
            idxG.append(np.where(indexToGroup == g + 1)[
                            0])  # each element of the list is an array containing the indices of the elements that belong to group g

        # Calculate self-mutual inductance between half-turns
        M_sum = np.empty((nGroups, nGroups))
        for g1 in range(nGroups):
            for g2 in range(nGroups):
                M_sum[g1, g2] = np.sum(M[idxG[g1][:, None], idxG[g2]])

        return M_sum

    def sumMatrixElements(self, M, indexToGroup):
        # faster implementation of sumMatrixElements_OLD and sumMatrixElements_OLD2 (but less readable)
        # TODO does not pass all the tests
        nGroups = int(np.max(indexToGroup))
        index_mask = indexToGroup[:, None] == np.arange(1, nGroups + 1)
        M_sum = index_mask.T @ M @ index_mask
        return M_sum

    # # It works but it is extremely slow
    # def sumMatrixElements(self, M, indexToGroup):
    #     nGroups = np.max(indexToGroup)
    #
    #     # Calculate self-mutual inductance between half-turns
    #     M_sum = np.empty((nGroups, nGroups))
    #     for g1 in range(nGroups):
    #         idxG1 = find_indices(indexToGroup, lambda s: s == g1 + 1)  # indices of the items belonging to group g1
    #         idxG1_mod = np.array(idxG1)
    #         for g2 in range(nGroups):
    #             idxG2 = find_indices(indexToGroup, lambda s: s == g2 + 1)  # indices of the items belonging to group g2
    #             idxG2_mod = np.array(idxG2)[:,None]
    #             M_sum[g1, g2] = np.sum(M[idxG1_mod, idxG2_mod])
    #
    #     return M_sum

    def calculateInductance(self, x, y, polarities, Ns, Ds, strandToHalfTurn, strandToCoilSection,
                            flag_strandCorrection=0):
        # Check inputs
        if np.size(x) != np.size(y):
            raise Exception('Variables x and y must have the same length.')
        if np.size(x) != np.size(polarities):
            raise Exception('Variables x and polarities must have the same length.')
        if np.size(x) != np.size(Ds):
            raise Exception('Variables x and Ds must have the same length.')
        if np.size(x) != np.size(strandToHalfTurn):
            raise Exception('Variables x and strandToHalfTurn must have the same length.')
        if np.size(x) != np.sum(Ns):
            raise Exception('The sum of the elements of vector Ns must be equal to the number of elements in vector x.')
        if np.size(Ns) < np.max(strandToHalfTurn):
            raise Exception(
                'The variable strandToHalfTurn cannot contain elements higher than the number of half-turns, i.e. the length of Ns.')
        if np.size(Ns) > np.size(np.unique(strandToHalfTurn)):
            print('Warning - ' + 'The variable strandToHalfTurn must assign strands to all half-turns.')

        M_strands = self.calculateStrandInductance(x, y, polarities, Ns, Ds, strandToHalfTurn)
        M_halfTurns = self.calculateHalfTurnInductance(M_strands, strandToHalfTurn)
        M_turns = self.calculateTurnInductance(M_halfTurns)
        M_coilSections = self.calculateCoilSectionInductance(M_strands, strandToCoilSection)
        L_mag0 = self.calculateTotalInductance(M_strands)

        return M_halfTurns, M_turns, M_coilSections, L_mag0

    def writeOutput(self, M_turns, M_coilSections, L_mag0):
        """

            **Write self-mutual inductance matrices in an output file**

        """
        nTurns = len(M_turns[0])
        nCoilSections = len(M_coilSections[0])

        # Write output
        outputFileName = 'SMIC_outputCalculatedInductances_TEST2.txt'
        file_out = open(outputFileName, "w")  ## 'w' overwrites file
        file_out.write("%s\n" % ('Self- and mutual inductances per unit length between each turn [H/m]'))
        for t1 in range(nTurns):
            for t2 in range(nTurns):
                file_out.write("%12.9e, " % (M_turns[t1, t2]))
            file_out.write("%s\n" % (''))

        file_out.write("%s\n" % (''))
        file_out.write("%s\n" % ('Self- and mutual inductances per unit length between each coil section [H/m]'))
        for cs1 in range(nCoilSections):
            for cs2 in range(nCoilSections):
                file_out.write("%12.9e, " % (M_coilSections[cs1, cs2]))
            file_out.write("%s\n" % (''))

        file_out.write("%s\n" % (''))
        file_out.write("%s\n" % ('Total self-inductance per unit length [H/m]'))
        file_out.write("%12.9e" % (L_mag0))
        file_out.close()
