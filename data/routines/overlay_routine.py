from routine.routine import Routine
from data.data import Data


class OverlayRoutine(Routine):
    """
    Class to proceed to full ETL
    """

    @property
    def name(self):
        return "overlay"

    def run_routine(self):
        data = Data(self._config, use_cache=True)

        # 1. Block to update financial/promo master

        # 1.1 Update financials
        data._etls["financials_master"].update_cache_after_manual_overlay()

        # 1.2 Update the promo master accordingly
        data.update_etl("promo_master")
