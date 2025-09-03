def lookupModelDataToProteCCT(key: str, mode='data2protecct'):
    """
        Retrieves the correct ProteCCT parameter name for a DataModelMagnet input
        The argument mode is used to define the direction, either "data2protecct" or "protecct2data"
    """
    lookup = {
        'GeneralParameters.magnet_name': 'magnetIdentifier',
        'GeneralParameters.T_initial': 'TOp',
        'GeneralParameters.magnetic_length': 'magneticLength',

        # winding
        'CoilWindings.CCT_straight.winding_numberTurnsFormers': 'numTurnsPerStrandTotal',
        'CoilWindings.CCT_straight.winding_numRowStrands': 'numRowStrands',
        'CoilWindings.CCT_straight.winding_numColumnStrands': 'numColumnStrands',


        # formers
        'CoilWindings.CCT_straight.formers_inner_radius': 'innerRadiusFormers',
        'CoilWindings.CCT_straight.former_thickness_underneath_coil': 'formerThicknessUnderneathCoil',


        'CoilWindings.CCT_straight.inner_radius_outer_cylinder': 'innerRadiusOuterCylinder',
        'CoilWindings.CCT_straight.thickness_outer_cylinder': 'thicknessOuterCylinder',

        'Conductors.strand.diameter': 'DStrand',
        'Conductors.strand.Cu_noCu_in_strand': '',
        'Conductors.strand.RRR': 'RRRStrand',

        'Power_Supply.I_initial': 'IOpInitial',
        'Power_Supply.R_crowbar': 'RCrowbar',

        'Quench_Protection.Energy_Extraction.t_trigger': 'tSwitchDelay',
        'Quench_Protection.Energy_Extraction.R_EE': 'RDumpPreconstant',
        'Quench_Protection.Energy_Extraction.power_R_EE': 'RDumpPower',

        'Options_ProteCCT.time_vector.tMaxStopCondition': 'tMaxStopCondition',
        'Options_ProteCCT.time_vector.minTimeStep': 'minTimeStep',
        'Options_ProteCCT.geometry_generation_options.totalConductorLength': 'totalConductorLength',

        'Options_ProteCCT.geometry_generation_options.thFormerInsul': 'thFormerInsul',
        'Options_ProteCCT.geometry_generation_options.wStrandSlot': 'wStrandSlot',

        'Options_ProteCCT.geometry_generation_options.IcFactor': 'IcFactor',
        'Options_ProteCCT.geometry_generation_options.polyimideToEpoxyRatio': 'polyimideToEpoxyRatio',
        'CoilWindings.CCT_straight.winding_order': 'windingOrder',
        'Options_ProteCCT.physics.M': 'M',
        'Options_ProteCCT.physics.BMaxAtNominal': 'BMaxAtNominal',
        'Options_ProteCCT.physics.BMinAtNominal': 'BMinAtNominal',
        'Options_ProteCCT.physics.INominal': 'INominal',
        'Options_ProteCCT.physics.fieldPeriodicity': 'fieldPeriodicity',
        'Options_ProteCCT.physics.RRRFormer': 'RRRFormer',
        'Options_ProteCCT.physics.RRROuterCylinder': 'RRROuterCylinder',
        'Options_ProteCCT.physics.coolingToHeliumBath': 'coolingToHeliumBath',
        'Options_ProteCCT.physics.fLoopLength': 'fLoopLength',
        'Options_ProteCCT.physics.addedHeCpFrac': 'addedHeCpFrac',
        'Options_ProteCCT.physics.addedHeCoolingFrac': 'addedHeCoolingFrac',
        'Options_ProteCCT.simulation.tempMaxStopCondition': 'tempMaxStopCondition',
        'Options_ProteCCT.simulation.IOpFractionStopCondition': 'IOpFractionStopCondition',
        'Options_ProteCCT.simulation.fracCurrentChangeMax': 'fracCurrentChangeMax',
        'Options_ProteCCT.simulation.resultsAtTimeStep': 'resultsAtTimeStep',
        'Options_ProteCCT.simulation.deltaTMaxAllowed': 'deltaTMaxAllowed',
        'Options_ProteCCT.simulation.turnLengthElements': 'turnLengthElements',
        'Options_ProteCCT.simulation.externalWaveform': 'externalWaveform',
        'Options_ProteCCT.simulation.saveStateAtEnd': 'saveStateAtEnd',
        'Options_ProteCCT.simulation.restoreStateAtStart': 'restoreStateAtStart',
        'Options_ProteCCT.simulation.silentRun': 'silentRun',
        'Options_ProteCCT.plots.withPlots': 'withPlots',
        'Options_ProteCCT.plots.plotPauseTime': 'plotPauseTime',
        'Options_ProteCCT.post_processing.withVoltageEvaluation': 'withVoltageEvaluation',
        'Options_ProteCCT.post_processing.voltageToGroundOutputSelection': 'voltageToGroundOutputSelection',
    }

    if mode == 'data2protecct':
        returned_key = lookup[key] if key in lookup else None
    elif mode == 'protecct2data':
        # Generate an inverted dictionary
        lookup_inverted = {v: k for k, v in lookup.items()}
        returned_key = lookup_inverted[key] if key in lookup_inverted else None

    return returned_key
