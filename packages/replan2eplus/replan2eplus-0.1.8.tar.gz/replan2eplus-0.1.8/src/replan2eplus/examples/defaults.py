from pathlib import Path
from replan2eplus.paths import static_paths

# external paths
ENERGY_PLUS_LOCATION = Path.home().parent.parent / "Applications/EnergyPlus-22-2-0"
PATH_TO_IDD = (
    ENERGY_PLUS_LOCATION / "Energy+.idd"
)  # TODO this is something that people have to specify on their own laptop to make it a valid default..

# static paths -> shipped with code.. 
PATH_TO_MINIMAL_IDF = static_paths.inputs / "base/01example/Minimal_AP.idf"
PATH_TO_SAMPLE_IDF =  static_paths.models / "three_plan/out.idf"
