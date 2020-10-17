from routine.routine import Routine
from data.data import Data


class EtlRoutine(Routine):
    """
    Class to proceed to full ETL
    """

    @property
    def name(self):
        return "etl"

    def run_routine(self):
        data = Data(self._config, use_cache=False)
        data.update_etls()
