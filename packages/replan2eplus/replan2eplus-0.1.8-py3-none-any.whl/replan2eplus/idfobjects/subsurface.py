from typing import Literal, NamedTuple



class SubsurfaceObject(NamedTuple):
    Name: str
    Building_Surface_Name: str
    # Outside_Boundary_Condition_Object: str
    Starting_X_Coordinate: float
    Starting_Z_Coordinate: float
    Length: float
    Height: float


SubsurfaceKey = Literal["DOOR", "WINDOW", "DOOR:INTERZONE"] 
