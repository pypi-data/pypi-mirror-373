from dataclasses import dataclass


@dataclass
class AirboundaryConstructionObject:
    Name: str
    # remaining fields are ignored when AFN is active
    Air_Exchange_Method: str = "SimpleMixing"  # or None..
    Simple_Mixing_Air_Changes_per_Hour: float = 0.5
    Simple_Mixing_Schedule_Name: str = ""  # otherwise reference a schedulr


DEFAULT_AIRBOUNDARY_OBJECT = AirboundaryConstructionObject("Default Airboundary")
