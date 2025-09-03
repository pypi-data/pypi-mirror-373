from pydantic import TypeAdapter

from steam_sdk.builders.Solenoids import Solenoid_magnet
from steam_sdk.data.DataModelMagnet import DataModelMagnet
from steam_sdk.data.DataRoxieParser import RoxieData
from steam_sdk.data.DataFiQuS import DataFiQuS #, MultipoleConductor
from steam_sdk.data.DataFiQuSMultipole import MultipoleRoxieGeometry
from steam_sdk.data.DataConductorFiQuS import Conductor as ConductorFiQuS


class BuilderFiQuS:
    """
        Class to generate FiQuS input file
    """

    def __init__(self,
                 model_data: DataModelMagnet = None,
                 roxie_data=None,
                 flag_build: bool = True,
                 verbose: bool = True):
        """
        Object is initialized by defining FiQuS variable structure and file template.
        :param model_data: DataModelMagnet object
        :param roxie_data: RoxieData object
        :param flag_build: boolean, if set to true data objects needed for ParserFiQuS are assembled
        :param verbose: if set to True, additional information is printed
        """
        # Unpack arguments
        self.verbose: bool = verbose

        if flag_build:

            # Data structure

            magnet_type = model_data.GeneralParameters.magnet_type
            if magnet_type == 'solenoid':
                magnet_type = 'multipole'
            self.data_FiQuS = DataFiQuS(magnet={'type': magnet_type})

            # --------- general ----------
            self.data_FiQuS.general.magnet_name = model_data.GeneralParameters.magnet_name
            self.data_FiQuS.magnet.type = magnet_type
            self.data_FiQuS.run = model_data.Options_FiQuS.run

            if model_data.GeneralParameters.magnet_type == 'multipole':
                if not roxie_data:
                    raise Exception(f'Cannot build model instantly without providing RoxieData as input roxie_data')
                self.data_FiQuS_geo = MultipoleRoxieGeometry()
                self.buildDataMultipole(model_data, roxie_data)
            elif model_data.GeneralParameters.magnet_type == 'solenoid':
                self.data_FiQuS_geo = MultipoleRoxieGeometry()
                self.buildDataMultipole(model_data)
            elif model_data.GeneralParameters.magnet_type == 'CCT_straight':
                self.buildDataCCT_straight(model_data)
            elif model_data.GeneralParameters.magnet_type == 'CWS':
                self.buildDataCWS(model_data)
            elif model_data.GeneralParameters.magnet_type == 'Pancake3D':
                self.buildDataPancake3D(model_data)
            elif model_data.GeneralParameters.magnet_type == 'CACStrand':
                self.buildDataCACStrand(model_data)
            elif model_data.GeneralParameters.magnet_type == 'CACRutherford':
                self.buildDataCACRutherford(model_data)
            else:
                raise Exception(f'Magnet type: {model_data.GeneralParameters.magnet_type} is incompatible with FiQuS.')


            # ------------- circuit ---------
            self.data_FiQuS.circuit = model_data.Circuit
            # for key, value in model_data.Circuit.dict().items():  # for keys that are present in the model data and in data FiQuS - they are the same
            #     self.data_FiQuS.circuit.__setattr__(key, value)

            # ------------- power_supply ---------
            self.data_FiQuS.power_supply = model_data.Power_Supply
            # for key, value in model_data.Power_Supply.dict().items():  # for keys that are present in the model data and in data FiQuS - they are the same
            #     self.data_FiQuS.power_supply.__setattr__(key, value)

            # ------------- quench_protection ---------
            self.data_FiQuS.quench_protection.energy_extraction = model_data.Quench_Protection.Energy_Extraction
            # for key, value in model_data.Quench_Protection.Energy_Extraction.dict().items():  # for keys that are present in the model data and in data FiQuS - they are the same
            #     self.data_FiQuS.quench_protection.energy_extraction.__setattr__(key, value)

            # ------------- quench_detection ---------
            self.data_FiQuS.quench_detection = model_data.Quench_Detection

            # ------------- quench_heaters ---------
            #self.data_FiQuS.quench_protection.quench_heaters = model_data.Quench_Protection.Quench_Heaters
            for key, value in model_data.Quench_Protection.Quench_Heaters.model_dump().items():  # for keys that are present in the model data and in data FiQuS - they are the same
                if key in self.data_FiQuS.quench_protection.quench_heaters.model_dump().keys():
                    if key not in ['type_ins']: # this creates pydantic validation error if assigned at this stage.
                        self.data_FiQuS.quench_protection.quench_heaters.__setattr__(key, value)
            # set the params that are renamed in FiQuS

            ins_type = {'1': 'G10', '1.0': 'G10', 'G10': 'G10', 1: 'G10', '2': 'kapton', '2.0': 'kapton', 'Kapton': 'kapton', 2: 'kapton', 'stycast': 'stycast', 'Stycast': 'stycast', 'kapton': 'kapton', 'Kapton': 'kapton'}
            if model_data.Quench_Protection.Quench_Heaters.s_ins:
                if type(model_data.Quench_Protection.Quench_Heaters.s_ins[0]) == list:
                    self.data_FiQuS.quench_protection.quench_heaters.h_ins = [[] for i in range(model_data.Quench_Protection.Quench_Heaters.N_strips)]
                    self.data_FiQuS.quench_protection.quench_heaters.type_ins = [[] for i in range(model_data.Quench_Protection.Quench_Heaters.N_strips)]
                    for ths, types in zip(model_data.Quench_Protection.Quench_Heaters.s_ins, model_data.Quench_Protection.Quench_Heaters.type_ins):
                        for i, (th, ty) in enumerate(zip(ths, types)):
                            self.data_FiQuS.quench_protection.quench_heaters.h_ins[i].append(th)
                            self.data_FiQuS.quench_protection.quench_heaters.type_ins[i].append(ins_type[ty])
                else:
                    self.data_FiQuS.quench_protection.quench_heaters.h_ins = [[th] for th in model_data.Quench_Protection.Quench_Heaters.s_ins]
                    self.data_FiQuS.quench_protection.quench_heaters.type_ins = [[ins_type[ty]] for ty in model_data.Quench_Protection.Quench_Heaters.type_ins]
            if model_data.Quench_Protection.Quench_Heaters.s_ins_He:
                if type(model_data.Quench_Protection.Quench_Heaters.s_ins_He[0]) == list:
                    self.data_FiQuS.quench_protection.quench_heaters.h_ground_ins = [[] for i in range(model_data.Quench_Protection.Quench_Heaters.N_strips)]
                    self.data_FiQuS.quench_protection.quench_heaters.type_ground_ins = [[] for i in range(model_data.Quench_Protection.Quench_Heaters.N_strips)]
                    for ths, types in zip(model_data.Quench_Protection.Quench_Heaters.s_ins_He, model_data.Quench_Protection.Quench_Heaters.type_ins_He):
                        for i, (th, ty) in enumerate(zip(ths, types)):
                            self.data_FiQuS.quench_protection.quench_heaters.h_ground_ins[i].append(th)
                            self.data_FiQuS.quench_protection.quench_heaters.type_ground_ins[i].append(ins_type[ty])
                else:
                    self.data_FiQuS.quench_protection.quench_heaters.h_ground_ins = [[th] for th in model_data.Quench_Protection.Quench_Heaters.s_ins_He]
                    self.data_FiQuS.quench_protection.quench_heaters.type_ground_ins = [[ins_type[ty]] for ty in model_data.Quench_Protection.Quench_Heaters.type_ins_He]
            self.data_FiQuS.quench_protection.quench_heaters.ids = model_data.Quench_Protection.Quench_Heaters.iQH_toHalfTurn_From
            self.data_FiQuS.quench_protection.quench_heaters.turns = model_data.Quench_Protection.Quench_Heaters.iQH_toHalfTurn_To

            self.data_FiQuS.quench_protection.cliq = model_data.Quench_Protection.CLIQ
            # for key, value in model_data.Quench_Protection.CLIQ.dict().items():  # for keys that are present in the model data and in data FiQuS - they are the same
            #     self.data_FiQuS.quench_protection.cliq.__setattr__(key, value)

            self.data_FiQuS.quench_protection.esc = model_data.Quench_Protection.ESC

            # ------------- Conductors ---------- #
            material_dict = {
                'Cu': {'rho_material_stabilizer': 'CFUN_rhoCu', 'Cv_material_stabilizer': 'CFUN_CvCu', 'k_material_stabilizer': 'CFUN_kCu'},
                'NbTi': {'Cv_material_superconductor': 'CFUN_CvNbTi'},
                'Nb3Sn': {'Cv_material_superconductor': 'CFUN_CvNb3Sn'}
            }

            for cond in model_data.Conductors:
                # self.data_FiQuS.conductors[cond.name] =\
                    # MultipoleConductor(cable={'type': cond.cable.type}, strand={'type': cond.strand.type}, Jc_fit={'type': cond.Jc_fit.type})
                self.data_FiQuS.conductors[cond.name] = ConductorFiQuS(cable={'type': cond.cable.type}, strand={'type': cond.strand.type}, Jc_fit={'type': cond.Jc_fit.type})
                conductor = self.data_FiQuS.conductors[cond.name]
                for key, value in cond.cable.model_dump().items():
                    conductor.cable.__setattr__(key, value)
                for key, value in cond.strand.model_dump().items():
                    if key in ['material_superconductor', 'material_stabilizer'] and value in material_dict.keys():
                        for k, v in material_dict[value].items():
                            conductor.strand.__setattr__(k, v)
                    conductor.strand.__setattr__(key, value)
                for key, value in cond.Jc_fit.model_dump().items():
                    conductor.Jc_fit.__setattr__(key, value)

    def buildDataCCT_straight(self, model_data):  # TODO: good idea to make them private?
        """
            Load selected conductor data from DataModelMagnet keys, check inputs, calculate and set missing variables
        """
        # --------- geometry ----------
        # CWSInputs
        for key, value in model_data.Options_FiQuS.cct.geometry.CWS_inputs.model_dump().items():       # for keys that are present in the FiQUS Options model data (but not all keys in data FiQuS)
            self.data_FiQuS.magnet.geometry.CWS_inputs.__setattr__(key, value)

        # windings
        for key, value in model_data.Options_FiQuS.cct.geometry.windings.model_dump().items():       # for keys that are present in the FiQUS Options model data (but not all keys in data FiQuS)
            self.data_FiQuS.magnet.geometry.windings.__setattr__(key, value)
        self.data_FiQuS.magnet.geometry.windings.n_turnss = model_data.CoilWindings.CCT_straight.winding_numberTurnsFormers  # additional, picked form other places in model data

        self.data_FiQuS.magnet.postproc.windings_wwns = model_data.CoilWindings.CCT_straight.winding_numRowStrands
        self.data_FiQuS.magnet.postproc.windings_whns = model_data.CoilWindings.CCT_straight.winding_numColumnStrands
        self.data_FiQuS.magnet.postproc.winding_order = model_data.CoilWindings.CCT_straight.winding_order

        # fqpls
        self.data_FiQuS.magnet.geometry.fqpcs.fndpls = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.fndpls, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpcs.fwhs = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.fwhs, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpcs.fwws = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.fwws, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpcs.n_sbs = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.n_sbs, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpcs.names = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.names, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpcs.r_bs = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.r_bs, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpcs.r_ins = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.r_ins, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpcs.thetas = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.thetas, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpcs.z_ends = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.z_ends, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.geometry.fqpcs.z_starts = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.z_starts, model_data.Quench_Protection.FQPCs.enabled) if flag]

        # formers
        for key, value in model_data.Options_FiQuS.cct.geometry.formers.dict().items():       # for keys that are present in the model data (but not all keys in data FiQuS)
            self.data_FiQuS.magnet.geometry.formers.__setattr__(key, value)
        self.data_FiQuS.magnet.geometry.formers.r_ins = model_data.CoilWindings.CCT_straight.former_inner_radiuses  # additional, picked form other places in model data
        self.data_FiQuS.magnet.geometry.formers.r_outs = model_data.CoilWindings.CCT_straight.former_outer_radiuses  # additional, picked form other places in model data

        # air
        self.data_FiQuS.magnet.geometry.air = model_data.Options_FiQuS.cct.geometry.air   # for keys that are present in the model data and in data FiQuS - they are the same

        # ------------- mesh --------------
        self.data_FiQuS.magnet.mesh = model_data.Options_FiQuS.cct.mesh                # for keys that are present in the model data and in data FiQuS - they are the same

        # ------------- solve -------------
        self.data_FiQuS.magnet.solve.windings = model_data.Options_FiQuS.cct.solve.windings              # for keys that are present in the model data and in data FiQuS - they are the same
        self.data_FiQuS.magnet.solve.fqpcs.mu_rs = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.mu_rs, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.solve.fqpcs.currents = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.currents, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.solve.fqpcs.sigmas = [val for val, flag in zip(model_data.Quench_Protection.FQPCs.sigmas, model_data.Quench_Protection.FQPCs.enabled) if flag]
        self.data_FiQuS.magnet.solve.formers = model_data.Options_FiQuS.cct.solve.formers
        self.data_FiQuS.magnet.solve.air = model_data.Options_FiQuS.cct.solve.air
        self.data_FiQuS.magnet.solve.file_exts = model_data.Options_FiQuS.cct.solve.file_exts
        self.data_FiQuS.magnet.solve.pro_template = model_data.Options_FiQuS.cct.solve.pro_template
        self.data_FiQuS.magnet.solve.variables = model_data.Options_FiQuS.cct.solve.variables
        self.data_FiQuS.magnet.solve.volumes = model_data.Options_FiQuS.cct.solve.volumes

        # ------------- postproc ---------
        for key, value in model_data.Options_FiQuS.cct.postproc.model_dump().items():       # for keys that are present in the model data and in data FiQuS - they are the same
            self.data_FiQuS.magnet.postproc.__setattr__(key, value)

    def buildDataCWS(self, model_data):
        """
        Populates keys from Options_FiQuS to data_FiQuS attribute of this class for magnet type CWS
        """
        self.data_FiQuS.magnet.geometry = model_data.Options_FiQuS.cws.geometry
        self.data_FiQuS.magnet.mesh = model_data.Options_FiQuS.cws.mesh
        self.data_FiQuS.magnet.solve = model_data.Options_FiQuS.cws.solve
        # for key, value in model_data.Options_FiQuS.cws.solve.model_dump().items():       # for keys that are present in the FiQUS Options model data (but not all keys in data FiQuS)
        #     if key not in ['conductors']:
        #         setattr(self.data_FiQuS.magnet.solve, key, value)
        #     else:
        #         self.data_FiQuS.magnet.solve.conductors.excitation.conductors_nw = model_data.Options_FiQuS.cws.solve.conductors.excitation.conductors_nw
        #         self.data_FiQuS.magnet.solve.conductors.excitation.conductors_nh = model_data.Options_FiQuS.cws.solve.conductors.excitation.conductors_nh
        #         self.data_FiQuS.magnet.solve.conductors.excitation.multips = model_data.Options_FiQuS.cws.solve.conductors.excitation.multips
        #         self.data_FiQuS.magnet.solve.conductors.excitation.from_file = model_data.Options_FiQuS.cws.solve.conductors.excitation.from_file
        #         self.data_FiQuS.magnet.solve.conductors.excitation.transient_use = model_data.Options_FiQuS.cws.solve.conductors.excitation.transient_use
        #         self.data_FiQuS.magnet.solve.conductors.excitation.function.names = model_data.Options_FiQuS.cws.solve.conductors.excitation.function.names
        #
        #         # use multips list length to set initial current list length and use Power_Supply.Initial as current
        #         self.data_FiQuS.magnet.solve.conductors.excitation.function.taus = model_data.Options_FiQuS.cws.solve.conductors.excitation.function.taus
        #         self.data_FiQuS.magnet.solve.conductors.excitation.function.initials = model_data.Options_FiQuS.cws.solve.conductors.excitation.function.initials
        #
        #         self.data_FiQuS.magnet.solve.conductors.conductivity_el = model_data.Options_FiQuS.cws.solve.conductors.conductivity_el
        #         self.data_FiQuS.magnet.solve.conductors.permeability = model_data.Options_FiQuS.cws.solve.conductors.permeability

        self.data_FiQuS.magnet.postproc = model_data.Options_FiQuS.cws.postproc

    def buildDataMultipole(self, model_data, roxie_data=None):
        """
            Load selected conductor data from DataModelMagnet keys, check inputs, calculate and set missing variables
        """

        # geom file
        if model_data.GeneralParameters.magnet_type == 'multipole':
            self.data_FiQuS_geo.Roxie_Data = RoxieData(**roxie_data.model_dump())
        elif model_data.GeneralParameters.magnet_type == 'solenoid':
            for coil_i, coil_d in enumerate(model_data.CoilWindings.solenoid.coils):
                conductor = model_data.Conductors[[cond.name for cond in model_data.Conductors].index(coil_d.conductor_name)]
                conductor.cable.th_insulation_along_width = conductor.cable.th_insulation_along_width + coil_d.pre_preg / 2
            sol_obj = Solenoid_magnet(model_data.CoilWindings.solenoid.coils, model_data.Conductors, model_data.Options_LEDET.field_map_files.Iref)
            self.data_FiQuS_geo.Roxie_Data = sol_obj.build_geom_object()

        # --------- run ----------
        self.data_FiQuS.run = model_data.Options_FiQuS.run

        # --------- general ----------
        self.data_FiQuS.general.magnet_name = model_data.GeneralParameters.magnet_name

        # --------- geometry ----------
        self.data_FiQuS.magnet.geometry = model_data.Options_FiQuS.multipole.geometry

        # ------------- mesh --------------
        self.data_FiQuS.magnet.mesh = model_data.Options_FiQuS.multipole.mesh

        # ------------- solve -------------
        self.data_FiQuS.magnet.solve.wedges = model_data.CoilWindings.multipole.wedges
        self.data_FiQuS.magnet.solve.thermal = model_data.Options_FiQuS.multipole.solve.thermal
        self.data_FiQuS.magnet.solve.electromagnetics = model_data.Options_FiQuS.multipole.solve.electromagnetics
        # ------------- solve coil windings ---------
        self.data_FiQuS.magnet.solve.coil_windings = model_data.CoilWindings

        # ------------- postproc ---------
        self.data_FiQuS.magnet.postproc = model_data.Options_FiQuS.multipole.postproc

    def buildDataPancake3D(self, model_data):
        """
        Populates keys from Options_FiQuS to data_FiQuS attribute of this class for magnet type Pancake3D
        """
        self.data_FiQuS.magnet.geometry = model_data.Options_FiQuS.Pancake3D.geometry
        self.data_FiQuS.magnet.mesh = model_data.Options_FiQuS.Pancake3D.mesh
        self.data_FiQuS.magnet.solve = model_data.Options_FiQuS.Pancake3D.solve
        self.data_FiQuS.magnet.postproc = model_data.Options_FiQuS.Pancake3D.postproc

    def buildDataCACStrand(self, model_data):
        """
        Populates keys from Options_FiQuS to data_FiQuS attribute of this class for magnet type ConductorAC Strand
        """
        self.data_FiQuS.magnet.geometry = model_data.Options_FiQuS.CACStrand.geometry
        self.data_FiQuS.magnet.mesh = model_data.Options_FiQuS.CACStrand.mesh

        source = model_data.Options_FiQuS.CACStrand.solve
        target = self.data_FiQuS.magnet.solve

        for key in source.model_fields:
            if key != "general_parameters":
                value = getattr(source, key)
                # this commented code is nicer way of doing it but somehow it does not work
                # the must be some data model overwrite that changes the type
                # field_type = type(getattr(target, key))
                # validated_value = TypeAdapter(field_type).validate_python(value)
                # setattr(target, key, validated_value)
                setattr(target, key, value)
            else:
                self.data_FiQuS.magnet.solve.general_parameters.superconductor_linear = model_data.Options_FiQuS.CACStrand.solve.general_parameters.superconductor_linear
                self.data_FiQuS.magnet.solve.general_parameters.noOfMPITasks = model_data.Options_FiQuS.CACStrand.solve.general_parameters.noOfMPITasks
                self.data_FiQuS.magnet.solve.general_parameters.temperature = model_data.GeneralParameters.T_initial

        self.data_FiQuS.magnet.postproc = model_data.Options_FiQuS.CACStrand.postproc
    
    def buildDataCACRutherford(self, model_data):
        """
        Populates keys from Options_FiQuS to data_FiQuS attribute of this class for magnet type ConductorAC Rutherford
        """
        self.data_FiQuS.magnet.geometry = model_data.Options_FiQuS.CACRutherford.geometry
        self.data_FiQuS.magnet.mesh = model_data.Options_FiQuS.CACRutherford.mesh

        for key, value in model_data.Options_FiQuS.CACRutherford.solve.model_dump().items(): # for keys that are present in the FiQUS Options model data (but not all keys in data FiQuS)
            if key not in ['general_parameters']:
                self.data_FiQuS.magnet.solve.__setattr__(key, value)
            else:
                self.data_FiQuS.magnet.solve.general_parameters.superconductor_linear = model_data.Options_FiQuS.CACRutherford.solve.general_parameters.superconductor_linear
                self.data_FiQuS.magnet.solve.general_parameters.crossing_coupling_resistance = model_data.Options_FiQuS.CACRutherford.solve.general_parameters.crossing_coupling_resistance
                self.data_FiQuS.magnet.solve.general_parameters.temperature = model_data.GeneralParameters.T_initial

