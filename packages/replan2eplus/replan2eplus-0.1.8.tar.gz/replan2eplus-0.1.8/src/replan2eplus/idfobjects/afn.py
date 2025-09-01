from typing import Literal, NamedTuple
from enum import StrEnum

VentilationControlMode = Literal["Constant", "NoVent"]


class AFNKeys(StrEnum):
    SIM_CONTROL = "AIRFLOWNETWORK:SIMULATIONCONTROL"
    ZONE = "AIRFLOWNETWORK:MULTIZONE:ZONE"
    OPENING = "AIRFLOWNETWORK:MULTIZONE:COMPONENT:SIMPLEOPENING"
    SURFACE = "AIRFLOWNETWORK:MULTIZONE:SURFACE"


DEFAULT_DISCHARGE_COEFF = 1
DEFAULT_AIR_MASS_FLOW_COEFF = 0.001  # 10E-2  kg/s-m
DEFAULT_MIN_DENSITY_DIFFERENCE = 0.0001  # 10E^-3 kg/m3


class AFNSimulationControl(NamedTuple):
    Name: str = "Default"
    AirflowNetwork_Control: Literal["MultizoneWithoutDistribution"] = (
        "MultizoneWithoutDistribution"
    )
    Building_Type: Literal["LowRise", "HighRise"] = "LowRise"
    Azimuth_Angle_of_Long_Axis_of_Building: float = 0
    Ratio_of_Building_Width_Along_Short_Axis_to_Width_Along_Long_Axis: float = (
        1  # 1 => square aspect ratio
    )
    # TODO this should be calculated! -> but do experiment to see how much it matters...


class AFNZone(NamedTuple):
    Zone_Name: str
    Ventilation_Control_Mode: Literal["Constant", "NoVent"] = (
        "Constant"  # Constant -> depends on venting availability schedule
    )
    Venting_Availability_Schedule_Name: str = (
        ""  # TODO dont add if its none..  #TODO add venting availability schedules..
    )


class AFNSimpleOpening(NamedTuple):
    Name: str  # subsurface name -> simple opening..
    Discharge_Coefficient: float = 1
    Air_Mass_Flow_Coefficient_When_Opening_is_Closed: float = DEFAULT_DISCHARGE_COEFF
    Minimum_Density_Difference_for_TwoWay_Flow: float = DEFAULT_MIN_DENSITY_DIFFERENCE


class AFNSurface(NamedTuple):
    Surface_Name: str  # subsurface name
    Leakage_Component_Name: str  # has to been in AFN simple opening!
    Ventilation_Control_Mode: Literal["ZoneLevel", "NoVent", "Constant"] = "ZoneLevel"
    # NOTE -> can do temperature / enthalpy based controls..
