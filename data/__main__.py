from data.routines.etl_routine import EtlRoutine
from data.routines.overlay_routine import OverlayRoutine
from routine.routine_cli import run_routine_from_cli

if __name__ == "__main__":
    run_routine_from_cli(
        routines={"etl": EtlRoutine, "overlay": OverlayRoutine}, default="etl"
    )
