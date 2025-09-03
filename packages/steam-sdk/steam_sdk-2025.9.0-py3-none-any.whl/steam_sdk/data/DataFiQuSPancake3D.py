from typing import Literal, Optional, Annotated, Union
from contextvars import ContextVar
import logging
import math
import pathlib
import scipy.integrate
from functools import cached_property
from pydantic import (
    BaseModel,
    PositiveFloat,
    NonNegativeFloat,
    PositiveInt,
    Field,
)
from annotated_types import Len

logger = logging.getLogger(__name__)

# ======================================================================================
# Available materials: =================================================================
NormalMaterialName = Optional[Literal[
    "Copper", "Hastelloy", "Silver", "Indium", "Stainless Steel", "Kapton", "G10"
]]
SuperconductingMaterialName = Optional[Literal["HTSSuperPower", "HTSFujikura", "HTSSucci"]]
# ======================================================================================
# ======================================================================================

# ======================================================================================
# Material information: ================================================================
resistivityMacroNames = {
    "Copper": "MATERIAL_Resistivity_Copper_T_B",
    "Hastelloy": "MATERIAL_Resistivity_Hastelloy_T",
    "Silver": "MATERIAL_Resistivity_Silver_T_B",
    "Indium": "MATERIAL_Resistivity_Indium_T",
    "Stainless Steel": "MATERIAL_Resistivity_SSteel_T",
}
thermalConductivityMacroNames = {
    "Copper": "MATERIAL_ThermalConductivity_Copper_T_B",
    "Hastelloy": "MATERIAL_ThermalConductivity_Hastelloy_T",
    "Silver": "MATERIAL_ThermalConductivity_Silver_T",
    "Indium": "MATERIAL_ThermalConductivity_Indium_T",
    "Stainless Steel": "MATERIAL_ThermalConductivity_SSteel_T",
    "Kapton": "MATERIAL_ThermalConductivity_Kapton_T",
    "G10": "MATERIAL_ThermalConductivity_G10_T",
}
heatCapacityMacroNames = {
    "Copper": "MATERIAL_SpecificHeatCapacity_Copper_T",
    "Hastelloy": "MATERIAL_SpecificHeatCapacity_Hastelloy_T",
    "Silver": "MATERIAL_SpecificHeatCapacity_Silver_T",
    "Indium": "MATERIAL_SpecificHeatCapacity_Indium_T",
    "Stainless Steel": "MATERIAL_SpecificHeatCapacity_SSteel_T",
    "Kapton": "MATERIAL_SpecificHeatCapacity_Kapton_T",
    "G10": "MATERIAL_SpecificHeatCapacity_G10_T",
}
getdpTSAStiffnessThermalConductivityMacroNames = {
    "Indium": "MATERIAL_ThermalConductivity_Indium_TSAStiffness_T",
    "Stainless Steel": "MATERIAL_ThermalConductivity_SSteel_TSAStiffness_T",
    "Kapton": "MATERIAL_ThermalConductivity_Kapton_TSAStiffness_T",
    "G10": "MATERIAL_ThermalConductivity_G10_TSAStiffness_T",
    "Copper": "MATERIAL_ThermalConductivity_Copper_TSAStiffness_T",
}
getdpTSAMassThermalConductivityMacroNames = {
    "Indium": "MATERIAL_ThermalConductivity_Indium_TSAMass_T",
    "Stainless Steel": "MATERIAL_ThermalConductivity_SSteel_TSAMass_T",
    "Kapton": "MATERIAL_ThermalConductivity_Kapton_TSAMass_T",
    "G10": "MATERIAL_ThermalConductivity_G10_TSAMass_T",
    "Copper": "MATERIAL_ThermalConductivity_Copper_TSAMass_T",
}
getdpTSAMassHeatCapacityMacroNames = {
    "Indium": "MATERIAL_SpecificHeatCapacity_Indium_TSAMass_T",
    "Stainless Steel": "MATERIAL_SpecificHeatCapacity_SSteel_TSAMass_T",
    "Kapton": "MATERIAL_SpecificHeatCapacity_Kapton_TSAMass_T",
    "G10": "MATERIAL_SpecificHeatCapacity_G10_TSAMass_T",
    "Copper": "MATERIAL_SpecificHeatCapacity_Copper_TSAMass_T",
}
getdpTSARHSFunctions = {
    "Indium": "TSA_CFUN_rhoIn_T_constantThickness_rhs",
    "Stainless Steel": None,
}
getdpTSATripleFunctions = {
    "Indium": "TSA_CFUN_rhoIn_T_constantThickness_triple",
    "Stainless Steel": None,
}
getdpTSAOnlyResistivityFunctions = {
    "Indium": "TSA_CFUN_rhoIn_T_constantThickness_fct_only",
    "Stainless Steel": None,
}
getdpTSAMassResistivityMacroNames = {
    "Indium": "MATERIAL_Resistivity_Indium_TSAMass_T",
    "Stainless Steel": None,
    "Copper": "MATERIAL_Resistivity_Copper_TSAMass_T",
}
getdpTSAStiffnessResistivityMacroNames = {
    "Indium": "MATERIAL_Resistivity_Indium_TSAStiffness_T",
    "Stainless Steel": None,
    "Copper": "MATERIAL_Resistivity_Copper_TSAStiffness_T",
}
getdpCriticalCurrentDensityFunctions = {
    "HTSSuperPower": "CFUN_HTS_JcFit_SUPERPOWER_T_B_theta",
    "HTSFujikura": "CFUN_HTS_JcFit_Fujikura_T_B_theta",
    "HTSSucci": "CFUN_HTS_JcFit_Succi_T_B",
}
getdpNormalMaterialNames = {
    "Copper": "Copper",
    "Hastelloy": "Hastelloy",
    "Silver": "Silver",
    "Indium": "Indium",
    "Stainless Steel": "StainlessSteel",
    "Kapton": "Kapton",
    "G10": "G10",
}
# ======================================================================================
# ======================================================================================

# ======================================================================================
# Available quantities: ================================================================
PositionRequiredQuantityName = Optional[Literal[
    "magneticField",
    "magnitudeOfMagneticField",
    "currentDensity",
    "magnitudeOfCurrentDensity",
    "resistiveHeating",
    "temperature",
    "criticalCurrentDensity",
    "heatFlux",
    "resistivity",
    "thermalConductivity",
    "specificHeatCapacity",
    "jHTSOverjCritical",
    "criticalCurrent",
    "axialComponentOfTheMagneticField",
    "debug",
    "jHTS",
    "currentSharingIndex",    
    "arcLength",
    "turnNumber"
]]
PositionNotRequiredQuantityName = Optional[Literal[
    "currentThroughCoil",
    "voltageBetweenTerminals",
    "inductance",
    "timeConstant",
    "totalResistiveHeating",
    "magneticEnergy",
    "maximumTemperature",
    "cryocoolerAveragePower",
    "cryocoolerAverageTemperature"
]]
# ======================================================================================
# ======================================================================================

# ======================================================================================
# Quantity information: ================================================================
EMQuantities = [
    "magneticField",
    "magnitudeOfMagneticField",
    "currentDensity",
    "magnitudeOfCurrentDensity",
    "resistiveHeating",
    "criticalCurrentDensity",
    "resistivity",
    "jHTSOverjCritical",
    "criticalCurrent",
    "debug",
    "inductance",
    "timeConstant",
    "currentThroughCoil",
    "voltageBetweenTerminals",
    "totalResistiveHeating",
    "magneticEnergy",
    "axialComponentOfTheMagneticField",
    "jHTS",
    "currentSharingIndex",
    "arcLength",
    "turnNumber"
]
ThermalQuantities = [
    "temperature",
    "heatFlux",
    "thermalConductivity",
    "specificHeatCapacity",
    "maximumTemperature",
    "debug",
    "cryocoolerAveragePower",
    "cryocoolerAverageTemperature"
]
quantityProperNames = {
    "magneticField": "Magnetic Field",
    "magneticEnergy": "Magnetic Energy",
    "magnitudeOfMagenticField": "Magnitude of Magnetic Field",
    "currentDensity": "Current Density",
    "magnitudeOfCurrentDensity": "Magnitude of Current Density",
    "resistiveHeating": "Resistive Heating",
    "totalResistiveHeating": "Total Resistive Heating",
    "temperature": "Temperature",
    "currentThroughCoil": "Current Through Coil",
    "voltageBetweenTerminals": "Voltage Between Terminals",
    "criticalCurrentDensity": "Critical Current Density",
    "heatFlux": "Heat Flux",
    "resistivity": "Resistivity",
    "thermalConductivity": "Thermal Conductivity",
    "specificHeatCapacity": "Specific Heat Capacity",
    "jHTSOverjCritical": "jHTS/jCritical",
    "criticalCurrent": "Critical Current",
    "debug": "Debug",
    "inductance": "Inductance",
    "timeConstant": "Time Constant",
    "axialComponentOfTheMagneticField": "Axial Component of the Magnetic Field",
    "maximumTemperature": "Maximum Temperature",
    "jHTS": "Current Density in HTS Layer",
    "currentSharingIndex": "Current Sharing Index",
    "cryocoolerAveragePower": "Cryocooler Average Power",
    "arcLength": "Arc Length",
    "turnNumber": "Turn Number",
    "cryocoolerAverageTemperature": "Cryocooler Average Temperature"
}

quantityUnits = {
    "magneticField": "T",
    "magneticEnergy": "J",
    "magnitudeOfMagneticField": "T",
    "currentDensity": "A/m^2",
    "magnitudeOfCurrentDensity": "A/m^2",
    "resistiveHeating": "W",
    "totalResistiveHeating": "W",
    "temperature": "K",
    "currentThroughCoil": "A",
    "voltageBetweenTerminals": "V",
    "criticalCurrentDensity": "A/m^2",
    "heatFlux": "W/m^2",
    "resistivity": "Ohm*m",
    "thermalConductivity": "W/m*K",
    "specificHeatCapacity": "J/kg*K",
    "jHTSOverjCritical": "-",
    "criticalCurrent": "A",
    "debug": "1",
    "inductance": "H",
    "timeConstant": "s",
    "axialComponentOfTheMagneticField": "T",
    "maximumTemperature": "K",
    "jHTS": "A/m^2",
    "currentSharingIndex": "-",
    "cryocoolerAveragePower": "W",
    "arcLength": "m",
    "turnNumber": "-",
    "cryocoolerAverageTemperature": "K"
}

getdpQuantityNames = {
    "magneticField": "RESULT_magneticField",
    "magneticEnergy": "RESULT_magneticEnergy",
    "magnitudeOfMagneticField": "RESULT_magnitudeOfMagneticField",
    "currentDensity": "RESULT_currentDensity",
    "magnitudeOfCurrentDensity": "RESULT_magnitudeOfCurrentDensity",
    "resistiveHeating": "RESULT_resistiveHeating",
    "totalResistiveHeating": "RESULT_totalResistiveHeating",
    "temperature": "RESULT_temperature",
    "currentThroughCoil": "RESULT_currentThroughCoil",
    "voltageBetweenTerminals": "RESULT_voltageBetweenTerminals",
    "criticalCurrentDensity": "RESULT_criticalCurrentDensity",
    "heatFlux": "RESULT_heatFlux",
    "resistivity": "RESULT_resistivity",
    "thermalConductivity": "RESULT_thermalConductivity",
    "specificHeatCapacity": "RESULT_specificHeatCapacity",
    "jHTSOverjCritical": "RESULT_jHTSOverjCritical",
    "criticalCurrent": "RESULT_criticalCurrent",
    "debug": "RESULT_debug",
    "inductance": "RESULT_inductance",
    "timeConstant": "RESULT_timeConstant",
    "axialComponentOfTheMagneticField": "RESULT_axialComponentOfTheMagneticField",
    "maximumTemperature": "RESULT_maximumTemperature",
    "jHTS": "RESULT_jHTS",
    "currentSharingIndex": "RESULT_currentSharingIndex",
    "cryocoolerAveragePower": "RESULT_cryocoolerAveragePower",
    "arcLength": "RESULT_arcLength",
    "turnNumber": "RESULT_turnNumber",
    "cryocoolerAverageTemperature": "RESULT_cryocoolerAverageTemperature"
}

getdpPostOperationNames = {
    "magneticField": "POSTOP_magneticField",
    "magneticEnergy": "RESULT_magneticEnergy",
    "magnitudeOfMagneticField": "POSTOP_magnitudeOfMagneticField",
    "currentDensity": "POSTOP_currentDensity",
    "magnitudeOfCurrentDensity": "POSTOP_magnitudeOfCurrentDensity",
    "resistiveHeating": "POSTOP_resistiveHeating",
    "totalResistiveHeating": "POSTOP_totalResistiveHeating",
    "temperature": "POSTOP_temperature",
    "currentThroughCoil": "POSTOP_currentThroughCoil",
    "voltageBetweenTerminals": "POSTOP_voltageBetweenTerminals",
    "criticalCurrentDensity": "POSTOP_criticalCurrentDensity",
    "heatFlux": "POSTOP_heatFlux",
    "resistivity": "POSTOP_resistivity",
    "thermalConductivity": "POSTOP_thermalConductivity",
    "specificHeatCapacity": "POSTOP_specificHeatCapacity",
    "jHTSOverjCritical": "POSTOP_jHTSOverjCritical",
    "criticalCurrent": "POSTOP_criticalCurrent",
    "debug": "POSTOP_debug",
    "inductance": "POSTOP_inductance",
    "timeConstant": "POSTOP_timeConstant",
    "axialComponentOfTheMagneticField": "POSTOP_axialComponentOfTheMagneticField",
    "maximumTemperature": "POSTOP_maximumTemperature",
    "jHTS": "POSTOP_jHTS",
    "currentSharingIndex": "POSTOP_currentSharingIndex",
    "cryocoolerAveragePower": "POSTOP_cryocoolerAveragePower",
    "arcLength": "POSTOP_arcLength",
    "turnNumber": "POSTOP_turnNumber",
    "cryocoolerAverageTemperature": "POSTOP_cryocoolerAverageTemperature"
}

# ======================================================================================
# ======================================================================================

# Global variables
geometry_input = ContextVar("geometry")
mesh_input = ContextVar("mesh")
solve_input = ContextVar("solve")
input_file_path = ContextVar("input_file_path")
all_break_points = []

# ======================================================================================
# FUNDAMENTAL CLASSES STARTS ===========================================================
# ======================================================================================
class Pancake3DPositionInCoordinates(BaseModel):
    x: Optional[float] = Field(
        title="x coordinate",
        description="x coordinate of the position.",
    )
    y: Optional[float] = Field(
        title="y coordinate",
        description="y coordinate of the position.",
    )
    z: Optional[float] = Field(
        title="z coordinate",
        description="z coordinate of the position.",
    )


class Pancake3DPositionInTurnNumbers(BaseModel):
    turnNumber: Optional[float] = Field(
        title="Turn Number",
        description=(
            "Winding turn number as a position input. It starts from 0 and it can be a"
            " float."
        ),
    )
    whichPancakeCoil: Optional[PositiveInt] = Field(
        default=None,
        title="Pancake Coil Number",
        description="The first pancake coil is 1, the second is 2, etc.",
    )

    def compute_coordinates(self):
        geometry = geometry_input.get()
        mesh = mesh_input.get()

        if geometry["contactLayer"]["thinShellApproximation"]:
            windingThickness = (
                    geometry["winding"]["thickness"]
                    + geometry["contactLayer"]["thickness"]
                    * (geometry["winding"]["numberOfTurns"] - 1)
                    / geometry["winding"]["numberOfTurns"]
            )
            gapThickness = 0
        else:
            windingThickness = geometry["winding"]["thickness"]
            gapThickness = geometry["contactLayer"]["thickness"]

        innerRadius = geometry["winding"]["innerRadius"]
        initialTheta = 0.0
        if isinstance(mesh["winding"]["azimuthalNumberOfElementsPerTurn"], list):
            ane = mesh["winding"]["azimuthalNumberOfElementsPerTurn"][0]
        elif isinstance(mesh["winding"]["azimuthalNumberOfElementsPerTurn"], int):
            ane = mesh["winding"]["azimuthalNumberOfElementsPerTurn"]
        else:
            raise ValueError(
                "The azimuthal number of elements per turn must be either an integer"
                " or a list of integers."
            )

        numberOfPancakes = geometry["numberOfPancakes"]
        gapBetweenPancakes = geometry["gapBetweenPancakes"]
        windingHeight = geometry["winding"]["height"]

        turnNumber = self.turnNumber
        whichPancake = self.whichPancakeCoil

        elementStartTurnNumber = math.floor(turnNumber / (1 / ane)) * (1 / ane)
        elementEndTurnNumber = elementStartTurnNumber + 1 / ane

        class point:
            def __init__(self, x, y, z):
                self.x = x
                self.y = y
                self.z = z

            def __add__(self, other):
                return point(self.x + other.x, self.y + other.y, self.z + other.z)

            def __sub__(self, other):
                return point(self.x - other.x, self.y - other.y, self.z - other.z)

            def __mul__(self, scalar):
                return point(self.x * scalar, self.y * scalar, self.z * scalar)

            def __truediv__(self, scalar):
                return point(self.x / scalar, self.y / scalar, self.z / scalar)

            def rotate(self, degrees):
                return point(
                    self.x * math.cos(degrees) - self.y * math.sin(degrees),
                    self.x * math.sin(degrees) + self.y * math.cos(degrees),
                    self.z,
                )

            def normalize(self):
                return self / math.sqrt(self.x**2 + self.y**2 + self.z**2)

        if whichPancake % 2 == 1:
            # If the spiral is counter-clockwise, the initial theta angle decreases,
            # and r increases as the theta angle decreases.
            multiplier = 1
        elif whichPancake % 2 == 0:
            # If the spiral is clockwise, the initial theta angle increases, and r
            # increases as the theta angle increases.
            multiplier = -1

        # Mesh element's starting point:
        elementStartTheta = 2 * math.pi * elementStartTurnNumber * multiplier
        elementStartRadius = (
                innerRadius
                + elementStartTheta
                / (2 * math.pi)
                * (gapThickness + windingThickness)
                * multiplier
        )
        elementStartPointX = elementStartRadius * math.cos(
            initialTheta + elementStartTheta
        )
        elementStartPointY = elementStartRadius * math.sin(
            initialTheta + elementStartTheta
        )
        elementStartPointZ = (
                -(
                        numberOfPancakes * windingHeight
                        + (numberOfPancakes - 1) * gapBetweenPancakes
                )
                / 2
                + windingHeight / 2
                + (whichPancake - 1) * (windingHeight + gapBetweenPancakes)
        )
        elementStartPoint = point(
            elementStartPointX, elementStartPointY, elementStartPointZ
        )

        # Mesh element's ending point:
        elementEndTheta = 2 * math.pi * elementEndTurnNumber * multiplier
        elementEndRadius = (
                innerRadius
                + elementEndTheta
                / (2 * math.pi)
                * (gapThickness + windingThickness)
                * multiplier
        )
        elementEndPointX = elementEndRadius * math.cos(initialTheta + elementEndTheta)
        elementEndPointY = elementEndRadius * math.sin(initialTheta + elementEndTheta)
        elementEndPointZ = elementStartPointZ
        elementEndPoint = point(elementEndPointX, elementEndPointY, elementEndPointZ)

        turnNumberFraction = (turnNumber - elementStartTurnNumber) / (
                elementEndTurnNumber - elementStartTurnNumber
        )
        location = (
                           elementStartPoint
                           + (elementEndPoint - elementStartPoint) * turnNumberFraction
                   ) + (elementEndPoint - elementStartPoint).rotate(
            -math.pi / 2
        ).normalize() * windingThickness / 2 * multiplier

        return location.x, location.y, location.z


Pancake3DPosition = Pancake3DPositionInCoordinates | Pancake3DPositionInTurnNumbers


# ======================================================================================
# FUNDAMENTAL CLASSES ENDS =============================================================
# ======================================================================================


# ======================================================================================
# GEOMETRY CLASSES STARTS ==============================================================
# ======================================================================================
class Pancake3DGeometryWinding(BaseModel):
    # Mandatory:
    innerRadius: Optional[PositiveFloat] = Field(
        title="Inner Radius",
        description="Inner radius of the winding.",
    )
    thickness: Optional[PositiveFloat] = Field(
        title="Winding Thickness",
        description="Thickness of the winding.",
    )
    numberOfTurns: Optional[float] = Field(
        ge=3,
        title="Number of Turns",
        description="Number of turns of the winding.",
    )
    height: Optional[PositiveFloat] = Field(
        title="Winding Height",
        description="Height/width of the winding.",
    )

    # Optionals:
    name: Optional[str] = Field(
        default="winding",
        title="Winding Name",
        description="The The name to be used in the mesh..",
        examples=["winding", "myWinding"],
    )
    numberOfVolumesPerTurn: Optional[int] = Field(
        default=2,
        validate_default=True,
        ge=2,
        title="Number of Volumes Per Turn (Advanced Input)",
        description="The number of volumes per turn (CAD related, not physical).",
    )

class Pancake3DGeometryContactLayer(BaseModel):
    # Mandatory:
    thinShellApproximation: Optional[bool] = Field(
        title="Use Thin Shell Approximation",
        description=(
            "If True, the contact layer will be modeled with 2D shell elements (thin"
            " shell approximation), and if False, the contact layer will be modeled"
            " with 3D elements."
        ),
    )
    thickness: Optional[PositiveFloat] = Field(
        title="Contact Layer Thickness",
        description=("Thickness of the contact layer."
                     "It is the total thickness of the contact or insulation layer."
                     "In particular, for perfect insulation this would be the sum of the insulation layer of the two adjacent CC with an insulation layer of "
                     "thickness t/2 on each side."
                     ),
    )

    # Optionals:
    name: Optional[str] = Field(
        default="contactLayer",
        title="Contact Layer Name",
        description="The name to be used in the mesh.",
        examples=["myContactLayer"],
    )


class Pancake3DGeometryTerminalBase(BaseModel):
    # Mandatory:
    thickness: Optional[PositiveFloat] = Field(
        title="Terminal Thickness",
        description="Thickness of the terminal's tube.",
    )  # thickness

class Pancake3DGeometryInnerTerminal(Pancake3DGeometryTerminalBase):
    name: Optional[str] = Field(
        default="innerTerminal",
        title="Terminal Name",
        description="The name to be used in the mesh.",
        examples=["innerTerminal", "outerTeminal"],
    )


class Pancake3DGeometryOuterTerminal(Pancake3DGeometryTerminalBase):
    name: Optional[str] = Field(
        default="outerTerminal",
        title="Terminal Name",
        description="The name to be used in the mesh.",
        examples=["innerTerminal", "outerTeminal"],
    )


class Pancake3DGeometryTerminals(BaseModel):
    # 1) User inputs:
    inner: Pancake3DGeometryInnerTerminal = Field()
    outer: Pancake3DGeometryOuterTerminal = Field()

    # Optionals:
    firstName: Optional[str] = Field(
        default="firstTerminal", description="name of the first terminal"
    )
    lastName: Optional[str] = Field(
        default="lastTerminal", description="name of the last terminal"
    )

class Pancake3DGeometryAirBase(BaseModel):
    # Mandatory:
    axialMargin: Optional[PositiveFloat] = Field(
        title="Axial Margin of the Air",
        description=(
            "Axial margin between the ends of the air and first/last pancake coils."
        ),
    )  # axial margin

    # Optionals:
    name: Optional[str] = Field(
        default="air",
        title="Air Name",
        description="The name to be used in the mesh.",
        examples=["air", "myAir"],
    )
    shellTransformation: Optional[bool] = Field(
        default=False,
        title="Use Shell Transformation",
        description=(
            "Generate outer shell air to apply shell transformation if True (GetDP"
            " related, not physical)"
        ),
    )
    shellTransformationMultiplier: Optional[float] = Field(
        default=1.2,
        gt=1.1,
        title="Shell Transformation Multiplier (Advanced Input)",
        description=(
            "multiply the air's outer dimension by this value to get the shell's outer"
            " dimension"
        ),
    )
    cutName: Optional[str] = Field(
        default="Air-Cut",
        title="Air Cut Name",
        description="name of the cut (cochain) to be used in the mesh",
        examples=["Air-Cut", "myAirCut"],
    )
    shellVolumeName: Optional[str] = Field(
        default="air-Shell",
        title="Air Shell Volume Name",
        description="name of the shell volume to be used in the mesh",
        examples=["air-Shell", "myAirShell"],
    )
    generateGapAirWithFragment: Optional[bool] = Field(
        default=False,
        title="Generate Gap Air with Fragment (Advanced Input)",
        description=(
            "generate the gap air with gmsh/model/occ/fragment if true (CAD related,"
            " not physical)"
        ),
    )

class Pancake3DGeometryAirCylinder(Pancake3DGeometryAirBase):
    type: Literal["cylinder"] = Field(default="cylinder", title="Air Type")
    radius: Optional[PositiveFloat] = Field(
        default=None,
        title="Air Radius",
        description="Radius of the air (for cylinder type air).",
    )


class Pancake3DGeometryAirCuboid(Pancake3DGeometryAirBase):
    type: Literal["cuboid"] = Field(default="cuboid", title="Air Type")
    sideLength: Optional[PositiveFloat] = Field(
        default=None,
        title="Air Side Length",
        description="Side length of the air (for cuboid type air).",
    )


Pancake3DGeometryAir = Pancake3DGeometryAirCylinder | Pancake3DGeometryAirCuboid

# ======================================================================================
# GEOMETRY CLASSES ENDS ================================================================
# ======================================================================================


# ======================================================================================
# MESH CLASSES STARTS ==================================================================
# ======================================================================================
class Pancake3DMeshWinding(BaseModel):
    # Mandatory:
    axialNumberOfElements: Optional[list[PositiveInt] | PositiveInt] = Field(
        title="Axial Number of Elements",
        description=(
            "The number of axial elements for the whole height of the coil. It can be"
            " either a list of integers to specify the value for each pancake coil"
            " separately or an integer to use the same setting for each pancake coil."
        ),
    )

    azimuthalNumberOfElementsPerTurn: Optional[list[PositiveInt] | PositiveInt] = Field(
        title="Azimuthal Number of Elements Per Turn",
        description=(
            "The number of azimuthal elements per turn of the coil. It can be either a"
            " list of integers to specify the value for each pancake coil separately or"
            " an integer to use the same setting for each pancake coil."
        ),
    )

    radialNumberOfElementsPerTurn: Optional[list[PositiveInt] | PositiveInt] = Field(
        title="Winding Radial Number of Elements Per Turn",
        description=(
            "The number of radial elements per tape of the winding. It can be either a"
            " list of integers to specify the value for each pancake coil separately or"
            " an integer to use the same setting for each pancake coil."
        ),
    )

    # Optionals:
    axialDistributionCoefficient: Optional[list[PositiveFloat] | PositiveFloat] = Field(
        default=[1],
        title="Axial Bump Coefficients",
        description=(
            "If 1, it won't affect anything. If smaller than 1, elements will get finer"
            " in the axial direction at the ends of the coil. If greater than 1,"
            " elements will get coarser in the axial direction at the ends of the coil."
            " It can be either a list of floats to specify the value for each pancake"
            " coil separately or a float to use the same setting for each pancake coil."
        ),
    )

    elementType: Optional[(
            list[Literal["tetrahedron", "hexahedron", "prism"]]
            | Literal["tetrahedron", "hexahedron", "prism"]
    )] = Field(
        default=["tetrahedron"],
        title="Element Type",
        description=(
            "The element type of windings and contact layers. It can be either a"
            " tetrahedron, hexahedron, or a prism. It can be either a list of strings"
            " to specify the value for each pancake coil separately or a string to use"
            " the same setting for each pancake coil."
        ),
    )


class Pancake3DMeshContactLayer(BaseModel):
    # Mandatory:
    radialNumberOfElementsPerTurn: Optional[list[PositiveInt]] = Field(
        title="Contact Layer Radial Number of Elements Per Turn",
        description=(
            "The number of radial elements per tape of the contact layer. It can be"
            " either a list of integers to specify the value for each pancake coil"
            " separately or an integer to use the same setting for each pancake coil."
        ),
    )


class Pancake3DMeshAirAndTerminals(BaseModel):
    # Optionals:
    structured: Optional[bool] = Field(
        default=False,
        title="Structure Mesh",
        description=(
            "If True, the mesh will be structured. If False, the mesh will be"
            " unstructured."
        ),
    )
    radialElementSize: Optional[PositiveFloat] = Field(
        default=1,
        title="Radial Element Size",
        description=(
            "If structured mesh is used, the radial element size can be set. It is the"
            " radial element size in terms of the winding's radial element size."
        ),
    )


# ======================================================================================
# MESH CLASSES ENDS ====================================================================
# ======================================================================================


# ======================================================================================
# SOLVE CLASSES STARTS =================================================================
# ======================================================================================
class Pancake3DSolveAir(BaseModel):
    # 1) User inputs:

    # Mandatory:
    permeability: Optional[PositiveFloat] = Field(
        title="Permeability of Air",
        description="Permeability of air.",
    )


class Pancake3DSolveIcVsLengthList(BaseModel):
    lengthValues: Optional[list[float]] = Field(
        title="Tape Length Values",
        description="Tape length values that corresponds to criticalCurrentValues.",
    )
    criticalCurrentValues: Optional[list[float]] = Field(
        title="Critical Current Values",
        description="Critical current values that corresponds to lengthValues.",
    )
    lengthUnit: Optional[str] = Field(
        title="Unit",
        description=(
            "Unit of the critical current values. "
            "It can be either the arc length in meter or "
            "the number of turns."
        ),
        examples=["meter", "turnNumber"],
    )

class Pancake3DSolveIcVsLengthCSV(BaseModel):
    csvFile: Optional[str] = Field(
        title="CSV File",
        description="The path of the CSV file that contains the critical current values.",
    )

    lengthUnit: Optional[str] = Field(
        title="Unit",
        description=(
            "Unit of the critical current values. "
            "It can be either the arc length in meter or "
            "the number of turns."
        ),
        examples=["meter", "turnNumber"],
    )


class Pancake3DSolveMaterialBase(BaseModel):
    name: Optional[str]

    # Optionals:
    RRR: Optional[PositiveFloat] = Field(
        default=100,
        title="Residual Resistance Ratio",
        description=(
            "Residual-resistivity ratio (also known as Residual-resistance ratio or"
            " just RRR) is the ratio of the resistivity of a material at reference"
            " temperature and at 0 K."
        ),
    )
    RRRRefTemp: Optional[PositiveFloat] = Field(
        default=295,
        title="Residual Resistance Ratio Reference Temperature",
        description="Reference temperature for residual resistance ratio",
    )


class Pancake3DSolveNormalMaterial(Pancake3DSolveMaterialBase):
    # Mandatory:
    name: NormalMaterialName = Field(
        title="Material Name",
    )

class Pancake3DSolveSuperconductingMaterial(Pancake3DSolveMaterialBase):
    # Mandatory:
    name: SuperconductingMaterialName = Field(
        title="Superconducting Material Name",
    )
    nValue: Optional[PositiveFloat] = Field(
        default=30,
        description="N-value for E-J power law.",
    )
    IcAtTAndBref: Optional[PositiveFloat | Pancake3DSolveIcVsLengthCSV | Pancake3DSolveIcVsLengthList] = Field(
        title="Critical Current at Reference Temperature and Field in A",
        description=(
            "Critical current in A at reference temperature and magnetic field."
            "The critical current value will"
            " change with temperature depending on the superconductor material.Either"
            " the same critical current for the whole tape or the critical current with"
            " respect to the tape length can be specified. To specify the same critical"
            " current for the entire tape, just use a scalar. To specify critical"
            " current with respect to the tape length: a CSV file can be used, or"
            " lengthValues and criticalCurrentValues can be given as lists. The data"
            " will be linearly interpolated.If a CSV file is to be used, the input"
            " should be the name of a CSV file (which is in the same folder as the"
            " input file) instead of a scalar. The first column of the CSV file will be"
            " the tape length in m, and the second column will be the critical current in A. "
        ),
        examples=[230, "IcVSlength.csv"],
    )

    # Optionals:
    electricFieldCriterion: Optional[PositiveFloat] = Field(
        default=1e-4,
        title="Electric Field Criterion",
        description=(
            "The electric field that defines the critical current density, i.e., the"
            " electric field at which the current density reaches the critical current"
            " density."
        ),
    )
    jCriticalScalingNormalToWinding: Optional[PositiveFloat] = Field(
        default=1,
        title="Critical Current Scaling Normal to Winding",
        description=(
            "Critical current scaling normal to winding, i.e., along the c_axis. "
            " We have Jc_cAxis = scalingFactor * Jc_abPlane."
            " A factor of 1 means no scaling such that the HTS layer is isotropic."
        ),
    )

    IcReferenceTemperature: Optional[PositiveFloat] = Field(
        default=77,
        title="Critical Current Reference Temperature",
        description="Critical current reference temperature in Kelvin.",
    )

    IcReferenceBmagnitude: Optional[NonNegativeFloat] = Field(
        default=0.0,
        title="Critical Current Reference Magnetic Field Magnitude",
        description="Critical current reference magnetic field magnitude in Tesla.",
    )

    IcReferenceBangle: Optional[NonNegativeFloat] = Field(
        default=90.0,
        title="Critical Current Reference Magnetic Field Angle",
        description= (
            "Critical current reference magnetic field angle in degrees."
            "0 degrees means the magnetic field is normal to the tape's wide surface"
            "and 90 degrees means the magnetic field is parallel to the tape's wide"
            "surface."
        ),
    )

class Pancake3DSolveHTSMaterialBase(BaseModel):
    relativeThickness: Optional[float] = Field(
        le=1,
        title="Relative Thickness (only for winding)",
        description=(
            "Winding tapes generally consist of more than one material. Therefore, when"
            " materials are given as a list in winding, their relative thickness,"
            " (thickness of the material) / (thickness of the bare conductor), should be"
            " specified."
        ),
    )


class Pancake3DSolveHTSNormalMaterial(
    Pancake3DSolveHTSMaterialBase, Pancake3DSolveNormalMaterial
):
    pass


class Pancake3DSolveHTSSuperconductingMaterial(
    Pancake3DSolveHTSMaterialBase, Pancake3DSolveSuperconductingMaterial
):
    pass


class Pancake3DSolveHTSShuntLayerMaterial(Pancake3DSolveNormalMaterial):
    name: Optional[NormalMaterialName] = Field(
        default="Copper",
        title="Material Name",
    )
    relativeHeight: Optional[float] = Field(
        default=0.0,
        ge=0,
        le=1,
        title="Relative Height of the Shunt Layer",
        description=(
            "HTS 2G coated conductor are typically plated, usually "
            " using copper. The relative height of the shunt layer is the "
            " width of the shunt layer divided by the width of the tape. "
            " 0 means no shunt layer."
        ),
    )


class Pancake3DSolveMaterial(BaseModel):
    # 1) User inputs:

    # Mandatory:

    # Optionals:
    resistivity: Optional[PositiveFloat] = Field(
        default=None,
        title="Resistivity",
        description=(
            "A scalar value. If this is given, material properties won't be used for"
            " resistivity."
        ),
    )
    thermalConductivity: Optional[PositiveFloat] = Field(
        default=None,
        title="Thermal Conductivity",
        description=(
            "A scalar value. If this is given, material properties won't be used for"
            " thermal conductivity."
        ),
    )
    specificHeatCapacity: Optional[PositiveFloat] = Field(
        default=None,
        title="Specific Heat Capacity",
        description=(
            "A scalar value. If this is given, material properties won't be used for"
            " specific heat capacity."
        ),
    )
    material: Optional[Pancake3DSolveNormalMaterial] = Field(
        default=None,
        title="Material",
        description="Material from STEAM material library.",
    )

class Pancake3DSolveShuntLayerMaterial(Pancake3DSolveMaterial):
    material: Optional[Pancake3DSolveHTSShuntLayerMaterial] = Field(
        default=Pancake3DSolveHTSShuntLayerMaterial(),
        title="Material",
        description="Material from STEAM material library.",
    )


class Pancake3DSolveContactLayerMaterial(Pancake3DSolveMaterial):
    resistivity: Optional[PositiveFloat | Literal["perfectlyInsulating"]] = Field(
        default=None,
        title="Resistivity",
        description=(
            'A scalar value or "perfectlyInsulating". If "perfectlyInsulating" is'
            " given, the contact layer will be perfectly insulating. If this value is"
            " given, material properties won't be used for resistivity."
        ),
    )
    numberOfThinShellElements: Optional[PositiveInt] = Field(
        default=1,
        title="Number of Thin Shell Elements (Advanced Input)",
        description=(
            "Number of thin shell elements in the FE formulation (GetDP related, not"
            " physical and only used when TSA is set to True)"
        ),
    )


Pancake3DHTSMaterial = Pancake3DSolveHTSNormalMaterial | Pancake3DSolveHTSSuperconductingMaterial


class Pancake3DSolveWindingMaterial(Pancake3DSolveMaterial):
    material: Optional[list[Pancake3DHTSMaterial]] = Field(
        default=None,
        title="Materials of HTS CC",
        description="List of materials of HTS CC.",
    )

    shuntLayer: Pancake3DSolveShuntLayerMaterial = Field(
        default=Pancake3DSolveShuntLayerMaterial(),
        title="Shunt Layer Properties",
        description="Material properties of the shunt layer.",
    )

    isotropic: Optional[bool] = Field(
        default=False,
        title="Isotropic Material",
        description=(
            "If True, resistivity and thermal conductivity are isotropic. If False, they are anisotropic. "
            "The default is anisotropic material."
        ),
    )

    minimumPossibleResistivity: Optional[NonNegativeFloat] = Field(
        default=1e-20,
        title="Minimum Possible Resistivity",
        description=(
            "The resistivity of the winding won't be lower than this value, no matter"
            " what."
        ),
    )
    
    maximumPossibleResistivity: Optional[PositiveFloat] = Field(
        default=0.01,
        title="Maximum Possible Resistivity",
        description=(
            "The resistivity of the winding won't be higher than this value, no matter"
            " what."
        ),
    )
class Pancake3DTerminalCryocoolerLumpedMass(Pancake3DSolveMaterial):

    material: Optional[Pancake3DSolveNormalMaterial] = Field(
        default=Pancake3DSolveNormalMaterial(name="Copper", RRR=295),
        title="Material",
        description="Material from STEAM material library.",
    )

    volume: Optional[NonNegativeFloat] = Field(
        default=0,
        title="Cryocooler Lumped Block Volume",
        description=(
        "Volume of the lumped thermal mass between second stage of the cryocooler and pancake coil in m^3. "
        "A zero value effectively disables the lumped thermal mass between second stage of the cryocooler and pancake coil."
        )
    )

    numberOfThinShellElements: Optional[PositiveInt] = Field(
        default=1,
        title="Number of Thin Shell Elements for Cryocooler Lumped Mass",
        description=(
            "Number of thin shell elements in the FE formulation (GetDP related, not"
            " physical and only used when TSA is set to True)"
        ),
    )
    
class Pancake3DTerminalCryocoolerBoundaryCondition(BaseModel):

    coolingPowerMultiplier: Optional[NonNegativeFloat] = Field(
        default=1,
        title="Cooling Power Multiplier",
        description=(
            "Multiplier for the cooling power. It can be used to scale"
            " the cooling power given by the coldhead capacity map by a non-negative float factor."
        ),
    )

    staticHeatLoadPower: Optional[NonNegativeFloat] = Field(
        default=0,
        title="Static Heat Load Power",
        description=(
            "Static heat load power in W. It can be used to add a static heat load"
            " to the cryocooler, i.e., decrease the power available for cooling. "
            " The actual cooling power is P(t) = P_cryocooler(T) - P_staticLoad."
        ),
    )

    lumpedMass: Optional[Pancake3DTerminalCryocoolerLumpedMass] = Field(
        default = Pancake3DTerminalCryocoolerLumpedMass(),
        title="Cryocooler Lumped Mass",
        description="Thermal lumped mass between second stage of the cryocooler and pancake coil modeled via TSA.",
    )

class Pancake3DSolveTerminalMaterialAndBoundaryCondition(Pancake3DSolveMaterial):
    cooling: Literal["adiabatic", "fixedTemperature", "cryocooler"] = Field(
        default="fixedTemperature",
        title="Cooling condition",
        description=(
            "Cooling condition of the terminal. It can be either adiabatic, fixed"
            " temperature, or cryocooler."
        ),
    )

    cryocoolerOptions: Optional[Pancake3DTerminalCryocoolerBoundaryCondition] = Field(
        default=Pancake3DTerminalCryocoolerBoundaryCondition(),
        title="Cryocooler Boundary Condition",
        description="Additional inputs for the cryocooler boundary condition.",
    )

    transitionNotch: Optional[Pancake3DSolveMaterial] = Field(
        title="Transition Notch Properties",
        description="Material properties of the transition notch volume.",
    )
    terminalContactLayer: Optional[Pancake3DSolveMaterial] = Field(
        title="Transition Layer Properties",
        description=(
            "Material properties of the transition layer between terminals and"
            " windings."
        ),
    )


class Pancake3DSolveToleranceBase(BaseModel):
    # Mandatory:
    quantity: Optional[str]
    relative: Optional[NonNegativeFloat] = Field(
        title="Relative Tolerance",
        description="Relative tolerance for the quantity.",
    )
    absolute: Optional[NonNegativeFloat] = Field(
        title="Absolute Tolerance", description="Absolute tolerance for the quantity"
    )

    # Optionals:
    normType: Optional[Literal["L1Norm", "MeanL1Norm", "L2Norm", "MeanL2Norm", "LinfNorm"]] = (
        Field(
            default="L2Norm",
            title="Norm Type",
            description=(
                "Sometimes, tolerances return a vector instead of a scalar (ex,"
                " solutionVector). Then, the magnitude of the tolerance should be"
                " calculated with a method. Norm type selects this method."
            ),
        )
    )


class Pancake3DSolvePositionRequiredTolerance(Pancake3DSolveToleranceBase):
    # Mandatory:
    quantity: Optional[PositionRequiredQuantityName] = Field(
        title="Quantity", description="Name of the quantity for tolerance."
    )
    position: Optional[Pancake3DPosition] = Field(
        title="Probing Position of the Quantity",
        description="Probing position of the quantity for tolerance.",
    )


class Pancake3DSolvePositionNotRequiredTolerance(Pancake3DSolveToleranceBase):
    # Mandatory:
    quantity: (
        Optional[Literal[
            "electromagneticSolutionVector",
            "thermalSolutionVector",
            "coupledSolutionVector",
        ]
        | PositionNotRequiredQuantityName]
    ) = Field(
        title="Quantity",
        description="Name of the quantity for tolerance.",
    )


Pancake3DSolveTolerance = Pancake3DSolvePositionRequiredTolerance | Pancake3DSolvePositionNotRequiredTolerance

class Pancake3DSolveSettingsWithTolerances(BaseModel):
    tolerances: Optional[list[Pancake3DSolveTolerance]]= Field(
        title="Tolerances for Adaptive Time Stepping",
        description=(
            "Time steps or nonlinear iterations will be refined until the tolerances"
            " are satisfied."
        ),
    )


class Pancake3DSolveAdaptiveTimeLoopSettings(Pancake3DSolveSettingsWithTolerances):
    # Mandatory:
    initialStep: Optional[PositiveFloat] = Field(
        title="Initial Step for Adaptive Time Stepping",
        description="Initial step for adaptive time stepping",
    )
    minimumStep: Optional[PositiveFloat] = Field(
        title="Minimum Step for Adaptive Time Stepping",
        description=(
            "The simulation will be aborted if a finer time step is required than this"
            " minimum step value."
        ),
    )
    maximumStep: Optional[PositiveFloat] = Field(
        description="Bigger steps than this won't be allowed",
    )

    # Optionals:
    integrationMethod: Optional[Literal[
        "Euler", "Gear_2", "Gear_3", "Gear_4", "Gear_5", "Gear_6"
    ]] = Field(
        default="Euler",
        title="Integration Method",
        description="Integration method for transient analysis",
    )
    breakPoints_input: Optional[list[float]] = Field(
        default=[0],
        title="Break Points for Adaptive Time Stepping",
        description="Make sure to solve the system for these times.",
    )


class Pancake3DSolveFixedTimeLoopSettings(BaseModel):
    # Mandatory:
    step: Optional[PositiveFloat] = Field(
        title="Step for Fixed Time Stepping",
        description="Time step for fixed time stepping.",
    )


class Pancake3DSolveFixedLoopInterval(BaseModel):
    # Mandatory:
    startTime: Optional[NonNegativeFloat] = Field(
        title="Start Time of the Interval",
        description="Start time of the interval.",
    )
    endTime: Optional[NonNegativeFloat] = Field(
        title="End Time of the Interval",
        description="End time of the interval.",
    )
    step: Optional[PositiveFloat] = Field(
        title="Step for the Interval",
        description="Time step for the interval",
    )


class Pancake3DSolveTimeBase(BaseModel):
    # Mandatory:
    start: Optional[float] = Field(
        title="Start Time", description="Start time of the simulation."
    )
    end: Optional[float] = Field(title="End Time", description="End time of the simulation.")

    # Optionals:
    extrapolationOrder: Literal[0, 1, 2, 3] = Field(
        default=1,
        title="Extrapolation Order",
        description=(
            "Before solving for the next time steps, the previous solutions can be"
            " extrapolated for better convergence."
        ),
    )


class Pancake3DSolveTimeAdaptive(Pancake3DSolveTimeBase):
    timeSteppingType: Optional[Literal["adaptive"]] = "adaptive"
    adaptiveSteppingSettings: Pancake3DSolveAdaptiveTimeLoopSettings = Field(
        title="Adaptive Time Loop Settings",
        description=(
            "Adaptive time loop settings (only used if stepping type is adaptive)."
        ),
    )


class Pancake3DSolveTimeFixed(Pancake3DSolveTimeBase):
    timeSteppingType: Optional[Literal["fixed"]] = "fixed"
    fixedSteppingSettings: (
            list[Pancake3DSolveFixedLoopInterval] | Pancake3DSolveFixedTimeLoopSettings
    ) = Field(
        title="Fixed Time Loop Settings",
        description="Fixed time loop settings (only used if stepping type is fixed).",
    )

Pancake3DSolveTime = Pancake3DSolveTimeAdaptive | Pancake3DSolveTimeFixed

class Pancake3DSolveNonlinearSolverSettings(Pancake3DSolveSettingsWithTolerances):
    # Optionals:
    maximumNumberOfIterations: Optional[PositiveInt] = Field(
        default=100,
        title="Maximum Number of Iterations",
        description="Maximum number of iterations allowed for the nonlinear solver.",
    )
    relaxationFactor: Optional[float] = Field(
        default=0.7,
        gt=0,
        title="Relaxation Factor",
        description=(
            "Calculated step changes of the solution vector will be multiplied with"
            " this value for better convergence."
        ),
    )


class Pancake3DSolveInitialConditions(BaseModel):
    # 1) User inputs:

    # Mandatory:
    temperature: Optional[PositiveFloat] = Field(
        title="Initial Temperature",
        description="Initial temperature of the pancake coils.",
    )

class Pancake3DSolveImposedField(BaseModel):

    imposedAxialField: float = Field(
        title="Imposed Axial Magnetic Field",
        description="Imposed axial magnetic field in Tesla. Only constant, purely axial magnetic fields are supported at the moment.",
)

class Pancake3DSolveLocalDefect(BaseModel):
    # Mandatory:
    value: Optional[NonNegativeFloat] = Field(
        title="Value",
        description="Value of the local defect.",
    )
    startTurn: Optional[NonNegativeFloat] = Field(
        title="Start Turn",
        description="Start turn of the local defect.",
    )
    endTurn: Optional[PositiveFloat] = Field(
        title="End Turn",
        description="End turn of the local defect.",
    )

    startTime: Optional[NonNegativeFloat] = Field(
        title="Start Time",
        description="Start time of the local defect.",
    )

    # Optionals:
    transitionDuration: Optional[NonNegativeFloat] = Field(
        default=0,
        title="Transition Duration",
        description=(
            "Transition duration of the local defect. If not given, the transition will"
            " be instantly."
        ),
    )
    whichPancakeCoil: Optional[PositiveInt] = Field(
        default=None,
        title="Pancake Coil Number",
        description="The first pancake coil is 1, the second is 2, etc.",
    )


class Pancake3DSolveLocalDefects(BaseModel):
    # 1) User inputs:

    criticalCurrentDensity: Optional[Pancake3DSolveLocalDefect] = Field(
        default=None,
        title="Local Defect for Critical Current Density",
        description="Set critical current density locally.",
    )

class Pancake3DSolveConvectiveCooling(BaseModel):

    heatTransferCoefficient: Optional[Union[NonNegativeFloat, Literal["nitrogenBath"]]] = Field(
        default=0,
        title="Heat Transfer Coefficient",
        description=(
            "The heat transfer coefficient for the heat transfer between the winding and the air. "
            "If zero, no heat transfer to the air is considered."
            "This feature is only implemented for the thin shell approximation."
            "At the moment, only constant values are supported."
        ),
    )

    solveHeatEquationTerminalsTransitionNotch: bool = Field(
        default=True,
        title="Solve Heat Equation in Terminals",
        description=(
            "If True, the heat equation is solved in the terminals and transition notch."
            "If False, the heat equation is not solved in the terminals and transition notches."
            "In the latter case, neither heat conduction nor generation are considered."
            "In other words, the temperature is not an unknown of the problem in the terminals."
        ),
    )

    exteriorBathTemperature: Optional[NonNegativeFloat] = Field(
        default=4.2,
        title="Exterior Bath Temperature",
        description=(
            "The temperature of the exterior bath for convective cooling boundary condition. "
        ),
    )

class Pancake3DSolveEECircuit(BaseModel):

    inductanceInSeriesWithPancakeCoil: Optional[NonNegativeFloat] = Field(
        default=0,
        title="Inductance in Series with Pancake Coil",
        description=(
            "A lumped inductance in series with the pancake coil to model a bigger coil. "
        ),
    )
        
    enable: Optional[bool] = Field(
        default=False,
        title="Enable Detection Circuit",
        description=(
            "Enable the detection circuit for the pancake coil. "
        ),
    )

    ResistanceEnergyExtractionOpenSwitch: Optional[NonNegativeFloat] = Field(
        default=1E6,
        title="Resistance of Energy Extraction Open Switch",
        description=(
            "The resistance of the energy extraction switch when modeled as open. "
        ),
    )

    ResistanceEnergyExtractionClosedSwitch: Optional[NonNegativeFloat] = Field(
        default=1E-6,
        title="Resistance of Energy Extraction Closed Switch",
        description=(
            "The resistance of the energy extraction switch when modeled as closed. "
        ),
    )

    ResistanceCrowbarOpenSwitch: Optional[NonNegativeFloat] = Field(
        default=1E6,
        title="Resistance of Crowbar Open Switch",
        description=(
            "The resistance of the crowbar switch when modeled as open. "
        ),
    )

    ResistanceCrowbarClosedSwitch: Optional[NonNegativeFloat] = Field(
        default=1E-6,
        title="Resistance of Crowbar Closed Switch",
        description=(
            "The resistance of the crowbar switch when modeled as closed. "
        ),
    )

    stopSimulationAtCurrent: Optional[NonNegativeFloat] = Field(
        default=0,
        title="Stop Simulation at Current",
        description=(
            "If a quench is detected and the current reaches this value, the simulation will be stopped after. "
            "stopSimulationWaitingTime seconds."
        ),
    )

    stopSimulationWaitingTime: Optional[NonNegativeFloat] = Field(
        default=0,
        title="Stop Simulation Waiting Time",
        description=(
            "The time to wait after a quench is detected and the current reaches stopSimulationAtCurrent before stopping the simulation."
        ),
    )

    # or use t_off from power supply? I don't like it since it's used as time value to turn off and not time interval.
    TurnOffDeltaTimePowerSupply: Optional[NonNegativeFloat] = Field(
        default=0,
        title="Time Interval Between Quench Detection and Power Supply Turn Off",
        description=(
            "The time it takes for the power supply to be turned off after quench detection. "
            "A linear ramp-down is assumed between the time of quench detection and the time of power supply turn off."
        ),
    )

class Pancake3DSolvePowerDensity(BaseModel):
    power: Optional[NonNegativeFloat] = Field(
            default=0,
            title="Power Density",
            description=(
                "The power in W for an imposed power density in the winding. "
                "'startTime', 'endTime', 'startTurn', and 'endTurn' "
                "are also required to be set."
            ),
        )

    startTime: Optional[NonNegativeFloat] = Field(
        default=0,
        title="Power Density Start Time",
        description=(
            "The start time for the imposed power density in the winding. "
            "'power', 'endTime', 'startTurn', and 'endTurn' "
            "are also required to be set."
        ),
    )

    endTime: Optional[NonNegativeFloat] = Field(
        default=0,
        title="Power Density End Time",
        description=(
            "The end time for the imposed power density in the winding. "
            "'power', 'startTime', 'startTurn', and 'endTurn' "
            "are also required to be set."
        ),
    )

    startArcLength: Optional[NonNegativeFloat] = Field(
        default=0,
        title="Power Density Start Arc Length",
        description=(
            "The start arc length in m for the imposed power density in the winding. "
            "'power', 'startTime', 'endTime', and 'endArcLength' "
            "are also required to be set."
        ),
    )

    endArcLength: Optional[NonNegativeFloat] = Field(
        default=0,
        title="Power Density End Arc Length",
        description=(
            "The end arc length in m for the imposed power density in the winding. "
            "'power', 'startTime', 'endTime', and 'startArcLength' "
            "are also required to be set."
        ),
    )

class Pancake3DSolveQuantityBase(BaseModel):
    # Mandatory:
    quantity: Optional[PositionNotRequiredQuantityName | PositionRequiredQuantityName] = Field(
        title="Quantity",
        description="Name of the quantity to be saved.",
    )

class Pancake3DSolveSaveQuantity(Pancake3DSolveQuantityBase):
    # Optionals:
    timesToBeSaved: Optional[Union[list[float], None]] = Field(
        default=None,
        title="Times to be Saved",
        description=(
            "List of times that wanted to be saved. If not given, all the time steps"
            " will be saved."
        ),
    )

# ======================================================================================
# SOLVE CLASSES ENDS ===================================================================
# ======================================================================================

# ======================================================================================
# POSTPROCESS CLASSES STARTS ===========================================================
# ======================================================================================


class Pancake3DPostprocessTimeSeriesPlotBase(Pancake3DSolveQuantityBase):
    # Mandatory:
    quantity: Optional[str]


class Pancake3DPostprocessTimeSeriesPlotPositionRequired(
    Pancake3DPostprocessTimeSeriesPlotBase
):
    # Mandatory:
    quantity: PositionRequiredQuantityName = Field(
        title="Quantity",
        description="Name of the quantity to be plotted.",
    )

    position: Pancake3DPosition = Field(
        title="Probing Position",
        description="Probing position of the quantity for time series plot.",
    )


class Pancake3DPostprocessTimeSeriesPlotPositionNotRequired(
    Pancake3DPostprocessTimeSeriesPlotBase
):
    # Mandatory:
    quantity: Optional[PositionNotRequiredQuantityName] = Field(
        title="Quantity",
        description="Name of the quantity to be plotted.",
    )


Pancake3DPostprocessTimeSeriesPlot = Pancake3DPostprocessTimeSeriesPlotPositionRequired | Pancake3DPostprocessTimeSeriesPlotPositionNotRequired


class Pancake3DPostprocessMagneticFieldOnPlane(BaseModel):
    # Optional:
    colormap: Optional[str] = Field(
        default="viridis",
        title="Colormap",
        description="Colormap for the plot.",
    )
    streamLines: Optional[bool] = Field(
        default=True,
        title="Stream Lines",
        description=(
            "If True, streamlines will be plotted. Note that magnetic field vectors may"
            " have components perpendicular to the plane, and streamlines will be drawn"
            " depending on the vectors' projection onto the plane."
        ),
    )
    interpolationMethod: Literal["nearest", "linear", "cubic"] = Field(
        default="linear",
        title="Interpolation Method",
        description=(
            "Interpolation type for the plot.Because of the FEM basis function"
            " selections of FiQuS, each mesh element has a constant magnetic field"
            " vector. Therefore, for smooth 2D plots, interpolation can be"
            " used.Types:nearest: it will plot the nearest magnetic field value to"
            " the plotting point.linear: it will do linear interpolation to the"
            " magnetic field values.cubic: it will do cubic interpolation to the"
            " magnetic field values."
        ),
    )
    timesToBePlotted: Optional[list[float]] = Field(
        default=None,
        title="Times to be Plotted",
        description=(
            "List of times that wanted to be plotted. If not given, all the time steps"
            " will be plotted."
        ),
    )
    planeNormal: Optional[Annotated[list[float], Len(min_length=3, max_length=3)]] = Field(
        default=[1, 0, 0],
        title="Plane Normal",
        description="Normal vector of the plane. The default is YZ-plane (1, 0, 0).",
    )
    planeXAxisUnitVector: Optional[Annotated[list[float], Len(min_length=3, max_length=3)]] = (
        Field(
            default=[0, 1, 0],
            title="Plane X Axis",
            description=(
                "If an arbitrary plane is wanted to be plotted, the arbitrary plane's X"
                " axis unit vector must be specified. The dot product of the plane's X"
                " axis and the plane's normal vector must be zero."
            ),
        )
    )


# ======================================================================================
# POSTPROCESS CLASSES ENDS =============================================================
# ======================================================================================


class Pancake3DGeometry(BaseModel):
    conductorWrite: Optional[bool] = Field(
        default=False,
        title="Flag:to Write the Conductor File",
        description="To Write the Conductor File"
    )

    # Mandatory:
    numberOfPancakes: Optional[PositiveInt] = Field(
        default=None,
        ge=1,
        title="Number of Pancakes",
        description="Number of pancake coils stacked on top of each other.",
    )

    gapBetweenPancakes: Optional[PositiveFloat] = Field(
        default=None,
        title="Gap Between Pancakes",
        description="Gap distance between the pancake coils.",
    )

    winding: Optional[Pancake3DGeometryWinding] = Field(
        default=None,
        title="Winding Geometry",
        description="This dictionary contains the winding geometry information.",
    )

    contactLayer: Optional[Pancake3DGeometryContactLayer] = Field(
        default=None,
        title="Contact Layer Geometry",
        description="This dictionary contains the contact layer geometry information.",
    )

    terminals: Optional[Pancake3DGeometryTerminals] = Field(
        default=None,
        title="Terminals Geometry",
        description="This dictionary contains the terminals geometry information.",
    )

    air: Optional[Pancake3DGeometryAir] = Field(
        default=None,
        title="Air Geometry",
        description="This dictionary contains the air geometry information.",
    )

    # Optionals:
    dimensionTolerance: Optional[PositiveFloat] = Field(
        default=1e-8,
        description="dimension tolerance (CAD related, not physical)",
    )
    pancakeBoundaryName: Optional[str] = Field(
        default="PancakeBoundary",
        description=(
            "name of the pancake's curves that touches the air to be used in the mesh"
        ),
    )
    contactLayerBoundaryName: Optional[str] = Field(
        default="contactLayerBoundary",
        description=(
            "name of the contact layers's curves that touches the air to be used in the"
            " mesh (only for TSA)"
        ),
    )


class Pancake3DMesh(BaseModel):
    # Mandatory:
    winding: Optional[Pancake3DMeshWinding] = Field(
        default=None,
        title="Winding Mesh",
        description="This dictionary contains the winding mesh information.",
    )
    contactLayer: Optional[Pancake3DMeshContactLayer] = Field(
        default=None,
        title="Contact Layer Mesh",
        description="This dictionary contains the contact layer mesh information.",
    )

    # Optionals:
    terminals: Optional[Pancake3DMeshAirAndTerminals] = Field(
        default=Pancake3DMeshAirAndTerminals(),
        title="Terminal Mesh",
        description="This dictionary contains the terminal mesh information.",
    )
    air: Optional[Pancake3DMeshAirAndTerminals] = Field(
        default=Pancake3DMeshAirAndTerminals(),
        title="Air Mesh",
        description="This dictionary contains the air mesh information.",
    )

    computeCohomologyForInsulating: Optional[bool] = Field(
        default=True,
        title="Compute Cohomology for Insulating",
        description=(
            "Expert option only. "
            "If False, the cohomology regions needed for simulating an insulating coil"
            "will not be computed. This will reduce the time spent for the meshing "
            "or more accurately the cohomology computing phase. BEWARE: The simulation "
            "will fail if set to False and a perfectlyInsulating coil is simulated."
        ),
    )

    # Mandatory:
    minimumElementSize: Optional[PositiveFloat] = Field(
        default=None,
        title="Minimum Element Size",
        description=(
            "The minimum mesh element size in terms of the largest mesh size in the"
            " winding. This mesh size will be used in the regions close the the"
            " winding, and then the mesh size will increate to maximum mesh element"
            " size as it gets away from the winding."
        ),
    )
    maximumElementSize: Optional[PositiveFloat]= Field(
        default=None,
        title="Maximum Element Size",
        description=(
            "The maximum mesh element size in terms of the largest mesh size in the"
            " winding. This mesh size will be used in the regions close the the"
            " winding, and then the mesh size will increate to maximum mesh element"
            " size as it gets away from the winding."
        ),
    )

class Pancake3DSolve(BaseModel):
    # 1) User inputs:
    time: Optional[Pancake3DSolveTime] = Field(
        default=None,
        title="Time Settings",
        description="All the time related settings for transient analysis.",
    )

    nonlinearSolver: Optional[Pancake3DSolveNonlinearSolverSettings] = Field(
        default=None,
        title="Nonlinear Solver Settings",
        description="All the nonlinear solver related settings.",
    )

    winding: Optional[Pancake3DSolveWindingMaterial] = Field(
        default=None,       
        title="Winding Properties",
        description="This dictionary contains the winding material properties.",
    )
    contactLayer: Optional[Pancake3DSolveContactLayerMaterial] = Field(
        default=None,
        title="Contact Layer Properties",
        description="This dictionary contains the contact layer material properties.",
    )
    terminals: Optional[Pancake3DSolveTerminalMaterialAndBoundaryCondition] = Field(
        default=None,
        title="Terminals Properties",
        description=(
            "This dictionary contains the terminals material properties and cooling"
            " condition."
        ),
    )
    air: Optional[Pancake3DSolveAir] = Field(
        default=None,
        title="Air Properties",
        description="This dictionary contains the air material properties.",
    )

    initialConditions: Optional[Pancake3DSolveInitialConditions] = Field(
        default=None,
        title="Initial Conditions",
        description="Initial conditions of the problem.",
    )

    boundaryConditions: Optional[Union[Literal["vanishingTangentialElectricField"], Pancake3DSolveImposedField]] = Field(
        default="vanishingTangentialElectricField",
        title="Boundary Conditions",
        description="Boundary conditions of the problem.",
    )

    quantitiesToBeSaved: Optional[list[Pancake3DSolveSaveQuantity]] = Field(
        default=None,
        title="Quantities to be Saved",
        description="List of quantities to be saved.",
    )

    # Mandatory:
    type: Optional[Literal["electromagnetic", "thermal", "weaklyCoupled", "stronglyCoupled"]] = (
        Field(
            default=None,
            title="Simulation Type",
            description=(
                "FiQuS/Pancake3D can solve only electromagnetic and thermal or"
                " electromagnetic and thermal coupled. In the weaklyCoupled setting,"
                " thermal and electromagnetics systems will be put into different"
                " matrices, whereas in the stronglyCoupled setting, they all will be"
                " combined into the same matrix. The solution should remain the same."
            ),
        )
    )

    # Optionals:
    proTemplate: Optional[str] = Field(
        default="Pancake3D_template.pro",
        description="file name of the .pro template file",
    )

    localDefects: Pancake3DSolveLocalDefects = Field(
        default=Pancake3DSolveLocalDefects(),
        title="Local Defects",
        description=(
            "Local defects (like making a small part of the winding normal conductor at"
            " some time) can be introduced."
        ),
    )

    initFromPrevious: Optional[str] = Field(
        default="",
        title="Full path to res file to continue from",
        description=(
            "The simulation is continued from an existing .res file.  The .res file is"
            " from a previous computation on the same geometry and mesh. The .res file"
            " is taken from the folder Solution_<<initFromPrevious>>."
            " IMPORTANT: When the option is used, the start time should be identical to the last "
            " time value for the <<initFromPrevious>> simulation."
        ),
    )

    isothermalInAxialDirection: Optional[bool] = Field(
        default=False,
        title="Equate DoF along axial direction",
        description=(
            "If True, the DoF along the axial direction will be equated. This means"
            " that the temperature will be the same along the axial direction reducing"
            " the number of DoF. This is only valid for the thermal analysis."
        ),
    )

    voltageTapPositions: Optional[list[Pancake3DPosition]] = Field(
        default=[],
        title="Voltage Tap Positions",
        description=(
            "List of voltage tap positions. The "
            "position can be given in the form of a list of [x, y, z] coordinates or "
            "as turnNumber and number of pancake coil."
        ),
    )

    EECircuit: Optional[Pancake3DSolveEECircuit] = Field(
        default = Pancake3DSolveEECircuit(),
        title="Detection Circuit",
        description=(
            "This dictionary contains the detection circuit settings."
        ),
    )

    noOfMPITasks: Optional[Union[bool, int]] = Field(
        default=False,
        title="No. of tasks for MPI parallel run of GetDP",
        description=(
            "If integer, GetDP will be run in parallel using MPI. This is only valid"
            " if MPI is installed on the system and an MPI-enabled GetDP is used."
            " If False, GetDP will be run in serial without invoking mpiexec."
        ),
    )

    resistiveHeatingTerminals: Optional[bool] = Field(
        default=True,
        title="Resistive Heating in Terminals",
        description=(
            "If True, terminals are subject to Joule heating. If False, terminal regions are"
            " not subject to Joule heating. In both cases, heat conduction through the terminal is "
            " considered."
        ),
    )

    heatFlowBetweenTurns: Optional[bool] = Field(
        default=True,
        title="Heat Equation Between Turns",
        description=(
            "If True, heat flow between turns is considered. If False, it is not considered. "
            "In the latter case, heat conduction is only considered to the middle of the winding in the thin shell approximation "
            "in order to keep the thermal mass of the insulation included. In the middle between the turns, an adiabatic condition is applied. "
            "Between the turns refers to the region between the winding turns, NOT to the region between terminals "
            "and the first and last turn. "
            "This feature is only implemented for the thin shell approximation."
        ),
    )

    convectiveCooling: Optional[Pancake3DSolveConvectiveCooling] = Field(
        default=Pancake3DSolveConvectiveCooling(),
        title="Convective Cooling",
        description=(
            "This dictionary contains the convective cooling settings."
        ),
    )

    imposedPowerDensity: Optional[Pancake3DSolvePowerDensity] = Field(
        default=None,
        title="Power Density",
        description=(
            "The power density for an imposed power density in the winding."
        ),
    )

    materialParametersUseCoilField: Optional[bool] = Field(
        default=True,
        title="Use Coil Field for Critical Current",
        description=(
            "If True, the total field (i.e., coil field plus potentially imposed field)"
             "will be used for the material (default)."
            "If False, only the imposed field (can be zero) will be used."
        ),
    )

    stopWhenTemperatureReaches: Optional[float] = Field(
        default=0,
        title="Stop When Temperature Reaches",
        description=(
            "If the maximum temperature reaches this value, the simulation will"
            " be stopped."
        ),
    )

class Pancake3DPostprocess(BaseModel):
    """
    TO BE UPDATED
    """

    # 1) User inputs:
    timeSeriesPlots: Optional[list[Pancake3DPostprocessTimeSeriesPlot]] = Field(
        default=None,
        title="Time Series Plots",
        description="Values can be plotted with respect to time.",
    )

    magneticFieldOnCutPlane: Optional[Pancake3DPostprocessMagneticFieldOnPlane] = Field(
        default=None,
        title="Magnetic Field on a Cut Plane",
        description=(
            "Color map of the magnetic field on the YZ plane can be plotted with"
            " streamlines."
        ),
    )


class Pancake3D(BaseModel):
    """
    Level 1: Class for FiQuS Pancake3D
    """

    type: Literal["Pancake3D"]
    geometry: Pancake3DGeometry = Field(
        default=None,
        title="Geometry",
        description="This dictionary contains the geometry information.",
    )
    mesh: Pancake3DMesh = Field(
        default=None,
        title="Mesh",
        description="This dictionary contains the mesh information.",
    )
    solve: Pancake3DSolve = Field(
        default=None,
        title="Solve",
        description="This dictionary contains the solve information.",
    )
    postproc: Pancake3DPostprocess = Field(
        default=None,
        title="Postprocess",
        description="This dictionary contains the postprocess information.",
    )
    input_file_path: Optional[str] = Field(
        default=None,
        description="path of the input file (calculated by FiQuS)",
        exclude=True,
    )
