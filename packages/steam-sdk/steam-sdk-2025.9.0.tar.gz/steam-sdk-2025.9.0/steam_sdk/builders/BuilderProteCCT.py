from math import isclose
from steam_sdk.data import DataModelMagnet
from steam_sdk.data.DataProteCCT import ProteCCTInputs


class BuilderProteCCT:
    """
        Class to generate ProteCCT models
    """

    def __init__(self,
                 input_model_data: DataModelMagnet = None,
                 flag_build: bool = True,
                 verbose: bool = True):
        """
            Object is initialized by defining ProteCCT variable structure and file template.
            Optionally, the argument model_data can be passed to read the variables of a BuilderModel object.
            If flagInstantBuild is set to True, the ProteCCT input file is generated.
            If verbose is set to True, additional information will be displayed
        """
        # Unpack arguments
        self.verbose: bool = verbose
        self.model_data: DataModelMagnet = input_model_data

        # Data structure
        self.Inputs = ProteCCTInputs()

        if not self.model_data and flag_build:
            raise Exception('Cannot build model instantly without providing DataModelMagnet')

        if flag_build:
            # Add method to translate all ProteCCT parameters from model_data to ProteCCT dataclasses
            self.translateModelDataToProteCCT()

            # Load conductor data from DataModelMagnet keys, and calculate+set relevant parameters
            self.loadConductorData()

            # Edit the entry magnet_name (required for ProteCCT)
            self.Inputs.magnetIdentifier = '\"' + self.Inputs.magnetIdentifier

    def setAttribute(self, ProteCCTclass, attribute: str, value):
        try:
            setattr(ProteCCTclass, attribute, value)
        except:
            setattr(getattr(self, ProteCCTclass), attribute, value)

    def getAttribute(self, ProteCCTclass, attribute):
        try:
            return getattr(ProteCCTclass, attribute)
        except:
            return getattr(getattr(self, ProteCCTclass), attribute)

    @staticmethod
    def _all_equal(iterator):
        iterator = iter(iterator)
        try:
            first = next(iterator)
        except StopIteration:
            return True
        return all(first == x for x in iterator)

    def translateModelDataToProteCCT(self):

        self.Inputs.magnetIdentifier = self.model_data.GeneralParameters.magnet_name
        self.Inputs.TOp = self.model_data.GeneralParameters.T_initial
        self.Inputs.magneticLength = self.model_data.GeneralParameters.magnetic_length

        # ----------------  winding -------------------
        self.Inputs.windingOrder = ''.join(['[']+[str(turn)+' ' for turn in self.model_data.CoilWindings.CCT_straight.winding_order[:-1]]+[str(self.model_data.CoilWindings.CCT_straight.winding_order[-1])]+[']'])

        if self._all_equal(self.model_data.CoilWindings.CCT_straight.winding_numberTurnsFormers):
            self.Inputs.numTurnsPerStrandTotal = self.model_data.CoilWindings.CCT_straight.winding_numberTurnsFormers[0]
        else:
            raise Exception(f'ProteCCT can only deal with equal number of turns in each former but, {self.model_data.CoilWindings.CCT_straight.winding_numRowStrands} was given.')

        # check if w of channels are the same in each former in terms of number of strands in columns and rows:
        if self._all_equal(self.model_data.CoilWindings.CCT_straight.winding_numRowStrands):
            self.Inputs.numRowStrands = self.model_data.CoilWindings.CCT_straight.winding_numRowStrands[0]
        else:
            raise Exception(f'ProteCCT can only deal with equal number of strands in rows in each former but, {self.model_data.CoilWindings.CCT_straight.winding_numRowStrands} was given.')

        if self._all_equal(self.model_data.CoilWindings.CCT_straight.winding_numColumnStrands):
            self.Inputs.numColumnStrands = self.model_data.CoilWindings.CCT_straight.winding_numColumnStrands[0]
        else:
            raise Exception(f'ProteCCT can only deal with equal number of strands in columns in each former but, {self.model_data.CoilWindings.CCT_straight.winding_numColumnStrands} was given.')

        # check if w of channels are the same in each former in terms of widht and height:
        if self._all_equal(self.model_data.CoilWindings.CCT_straight.winding_chws):
            wStrandSlot = self.model_data.CoilWindings.CCT_straight.winding_chws[0] / self.Inputs.numRowStrands
        else:
            raise Exception(f'ProteCCT can only deal with the same channel sizes in each former, but {self.model_data.CoilWindings.CCT_straight.winding_chws} was given.')
        if self._all_equal(self.model_data.CoilWindings.CCT_straight.winding_chhs):
            hStrandSlot = self.model_data.CoilWindings.CCT_straight.winding_chhs[0] / self.Inputs.numColumnStrands
        else:
            raise Exception(f'ProteCCT can only deal with the same channel sizes in each former, but {self.model_data.CoilWindings.CCT_straight.winding_chhs} was given.')

        # ----------------  formers -------------------
        self.Inputs.innerRadiusFormers = self.model_data.CoilWindings.CCT_straight.former_inner_radiuses
        thicknesses = []
        for r_i_f, r_o_f, in zip(self.model_data.CoilWindings.CCT_straight.former_inner_radiuses, self.model_data.CoilWindings.CCT_straight.former_outer_radiuses):
            thicknesses.append(r_o_f - r_i_f - wStrandSlot * self.Inputs.numColumnStrands)
        if self._all_equal(thicknesses):
            self.Inputs.formerThicknessUnderneathCoil = thicknesses[0]
        else:
            raise Exception(f'ProteCCT can only deal with one thickness of formers underneath the coils, but inner and outer radiuses are not resulting in the same value for each former')

        if self._all_equal(self.model_data.CoilWindings.CCT_straight.former_RRRs):
            self.Inputs.RRRFormer = self.model_data.CoilWindings.CCT_straight.former_RRRs[0]
        else:
            raise Exception(f'ProteCCT can only deal with one RRR value for formers, so values in former_RRRs i.e. {self.model_data.CoilWindings.CCT_straight.former_RRRs} must be all the same.')

        # ----------------  cylinder -------------------
        if len(self.model_data.CoilWindings.CCT_straight.cylinder_inner_radiuses) == 1:
            self.Inputs.innerRadiusOuterCylinder = self.model_data.CoilWindings.CCT_straight.cylinder_inner_radiuses[0]
        else:
            raise Exception(f'ProteCCT can only deal with one outer cylinder but {len(self.model_data.CoilWindings.CCT_straight.cylinder_inner_radiuses)} were given with inner radiuses.')
        if len(self.model_data.CoilWindings.CCT_straight.cylinder_outer_radiuses) != 1:
            raise Exception(f'ProteCCT can only deal with one outer cylinder but {len(self.model_data.CoilWindings.CCT_straight.cylinder_outer_radiuses)} were given with outer radiuses.')
        else:
            self.Inputs.thicknessOuterCylinder = self.model_data.CoilWindings.CCT_straight.cylinder_outer_radiuses[0] - self.model_data.CoilWindings.CCT_straight.cylinder_inner_radiuses[0]

        self.Inputs.thFormerInsul = self.model_data.Options_ProteCCT.geometry_generation_options.thFormerInsul

        if isclose(wStrandSlot, hStrandSlot, rel_tol=1e-09, abs_tol=0):
            self.Inputs.wStrandSlot = wStrandSlot

        if self._all_equal(self.model_data.CoilWindings.CCT_straight.cylinder_RRRs):
            self.Inputs.RRROuterCylinder = self.model_data.CoilWindings.CCT_straight.cylinder_RRRs[0]
        else:
            raise Exception(f'ProteCCT can only deal with one RRR value for cylinder, so values in cylinder_RRRs i.e. {self.model_data.CoilWindings.CCT_straight.cylinder_RRRs} must be all the same.')

        if len(self.model_data.Conductors) == 1:
            self.Inputs.DStrand = self.model_data.Conductors[0].strand.diameter
            #self.Inputs.Cu_noCu_in_strand = self.model_data.Conductors[0].strand.Cu_noCu_in_strand
            self.Inputs.RRRStrand = self.model_data.Conductors[0].strand.RRR
        else:
            raise Exception(f'ProteCCT can only deal with one strand type, but {len(self.model_data.Conductors)} types were given.')

        self.Inputs.IOpInitial = self.model_data.Power_Supply.I_initial
        self.Inputs.RCrowbar = self.model_data.Power_Supply.R_crowbar

        self.Inputs.tSwitchDelay = self.model_data.Quench_Protection.Energy_Extraction.t_trigger
        self.Inputs.RDumpPreconstant = self.model_data.Quench_Protection.Energy_Extraction.R_EE
        self.Inputs.RDumpPower = self.model_data.Quench_Protection.Energy_Extraction.power_R_EE

        self.Inputs.tMaxStopCondition = self.model_data.Options_ProteCCT.time_vector.tMaxStopCondition
        self.Inputs.minTimeStep = self.model_data.Options_ProteCCT.time_vector.minTimeStep
        self.Inputs.totalConductorLength = self.model_data.Options_ProteCCT.geometry_generation_options.totalConductorLength

        self.Inputs.IcFactor = self.model_data.Options_ProteCCT.geometry_generation_options.IcFactor
        self.Inputs.polyimideToEpoxyRatio = self.model_data.Options_ProteCCT.geometry_generation_options.polyimideToEpoxyRatio

        self.Inputs.M = self.model_data.Options_ProteCCT.physics.M
        self.Inputs.BMaxAtNominal = self.model_data.Options_ProteCCT.physics.BMaxAtNominal
        self.Inputs.BMinAtNominal = self.model_data.Options_ProteCCT.physics.BMinAtNominal
        self.Inputs.INominal = self.model_data.Options_ProteCCT.physics.INominal
        self.Inputs.fieldPeriodicity = self.model_data.Options_ProteCCT.physics.fieldPeriodicity

        self.Inputs.coolingToHeliumBath = self.model_data.Options_ProteCCT.physics.coolingToHeliumBath
        self.Inputs.fLoopLength = self.model_data.Options_ProteCCT.physics.fLoopLength
        self.Inputs.addedHeCpFrac = self.model_data.Options_ProteCCT.physics.addedHeCpFrac
        self.Inputs.addedHeCoolingFrac = self.model_data.Options_ProteCCT.physics.addedHeCoolingFrac

        self.Inputs.tempMaxStopCondition = self.model_data.Options_ProteCCT.simulation.tempMaxStopCondition
        self.Inputs.IOpFractionStopCondition = self.model_data.Options_ProteCCT.simulation.IOpFractionStopCondition
        self.Inputs.fracCurrentChangeMax = self.model_data.Options_ProteCCT.simulation.fracCurrentChangeMax
        self.Inputs.resultsAtTimeStep = self.model_data.Options_ProteCCT.simulation.resultsAtTimeStep
        self.Inputs.deltaTMaxAllowed = self.model_data.Options_ProteCCT.simulation.deltaTMaxAllowed
        self.Inputs.turnLengthElements = self.model_data.Options_ProteCCT.simulation.turnLengthElements
        self.Inputs.externalWaveform = self.model_data.Options_ProteCCT.simulation.externalWaveform
        self.Inputs.saveStateAtEnd = self.model_data.Options_ProteCCT.simulation.saveStateAtEnd
        self.Inputs.restoreStateAtStart = self.model_data.Options_ProteCCT.simulation.restoreStateAtStart
        self.Inputs.silentRun = self.model_data.Options_ProteCCT.simulation.silentRun

        self.Inputs.withPlots = self.model_data.Options_ProteCCT.plots.withPlots
        self.Inputs.plotPauseTime = self.model_data.Options_ProteCCT.plots.plotPauseTime
        self.Inputs.withVoltageEvaluation = self.model_data.Options_ProteCCT.post_processing.withVoltageEvaluation
        self.Inputs.voltageToGroundOutputSelection = self.model_data.Options_ProteCCT.post_processing.voltageToGroundOutputSelection

    def loadConductorData(self):
        """
            Load selected conductor data from DataModelMagnet keys, check inputs, calculate and set missing variables
        """

        # Check inputs and unpack variables
        if len(self.model_data.Conductors) > 1:
            raise Exception('For ProteCCT models, the key Conductors cannot contain more than one entry.')
        conductor_type = self.model_data.Conductors[0].cable.type
        if conductor_type != 'Mono':
            raise Exception('For ProteCCT models, the only supported cable type is Mono.')

        # Load variables
        DStrand = self.model_data.Conductors[0].strand.diameter
        Cu_noCu = self.model_data.Conductors[0].strand.Cu_noCu_in_strand
        RRRStrand = self.model_data.Conductors[0].strand.RRR

        # Calculate Cu fraction
        CuFraction = Cu_noCu / (1 + Cu_noCu)

        # Set calculated variables
        self.setAttribute(self.Inputs, 'DStrand', DStrand)
        self.setAttribute(self.Inputs, 'CuFraction', CuFraction)
        self.setAttribute(self.Inputs, 'RRRStrand', RRRStrand)
