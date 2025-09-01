from replan2eplus.ezobjects.subsurface import Subsurface
from replan2eplus.ezobjects.surface import Surface
from replan2eplus.ezobjects.zone import Zone
from replan2eplus.idfobjects.afn import (
    AFNSimpleOpening,
    AFNSimulationControl,
    AFNSurface,
    AFNZone,
)
from replan2eplus.ezobjects.airboundary import Airboundary


from dataclasses import dataclass


@dataclass
class AFNInputs:
    zones_: list[Zone]
    subsurfaces: list[Subsurface]
    airboundaires: list[Airboundary]

    @property
    def sim_control(self):
        return AFNSimulationControl()

    @property
    def zones(self):
        # TODO if there was a parameter map would apply here..
        return [AFNZone(i.zone_name) for i in self.zones_]

    @property
    def surfaces_and_openings(self):
        # Air boundary is allowed by venting is constant, on..
        subsurface_openings: dict[str, AFNSimpleOpening] = {
            i.subsurface_name: AFNSimpleOpening(f"SimpleOpening__{i.subsurface_name}")
            for i in self.subsurfaces
        }
        surface_openings: dict[str, AFNSimpleOpening] = {
            i.surface.surface_name: AFNSimpleOpening(
                f"SimpleOpening__{i.surface.surface_name}"
            )
            for i in self.airboundaires
        }

        openings = subsurface_openings | surface_openings

        openings_list = list(openings.values())
        surfaces = [
            AFNSurface(surface_name, opening.Name)
            for surface_name, opening in openings.items()
        ]
        return surfaces, openings_list
