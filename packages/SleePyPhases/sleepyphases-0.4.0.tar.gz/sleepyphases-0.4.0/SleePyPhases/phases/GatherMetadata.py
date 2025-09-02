import pandas as pd
from pyPhasesRecordloader import RecordLoader

from pyPhases import Phase

class GatherMetadata(Phase):
    """
    gather metadata
    """
    def main(self):
        rl = RecordLoader.get()
        meta = rl.getAllMetaData()
        pd.DataFrame(meta).to_csv("metadata.csv")