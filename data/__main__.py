from data.routines.etl_routine import EtlRoutine
from data.routines.upload_to_db_routine import EtlUploadDB
from routine.routine_cli import run_routine_from_cli

if __name__ == "__main__":
    run_routine_from_cli(
        routines={"etl": EtlRoutine, "etl_to_db": EtlUploadDB}, default="etl"
    )
