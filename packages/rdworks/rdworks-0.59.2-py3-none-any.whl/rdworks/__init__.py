__version__ = '0.59.2'

from rdworks.conf    import Conf
from rdworks.mol     import Mol
from rdworks.mollibr import MolLibr

from rdworks.readin import read_csv, merge_csv, read_dataframe, read_smi, read_sdf, read_mae 
from rdworks.std import desalt_smiles, standardize_smiles, standardize

from rdworks.complete import complete_stereoisomers, complete_tautomers
from rdworks.ionized import IonizedStates

from rdworks.rgroup import expand_rgroup, most_common, most_common_in_NP
from rdworks.scaffold import scaffold_network, scaffold_tree, BRICS_fragmented, BRICS_fragment_indices
from rdworks.matchedseries import MatchedSeries

from rdworks.descriptor import rd_descriptor, rd_descriptor_f
from rdworks.xml import list_predefined_xml, get_predefined_xml, parse_xml

import rdkit
import logging

__rdkit_version__ = rdkit.rdBase.rdkitVersion

rdkit_logger = rdkit.RDLogger.logger().setLevel(rdkit.RDLogger.CRITICAL)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # level: DEBUG < INFO < WARNING < ERROR < CRITICAL

logger_stream = logging.StreamHandler() # sys.stdout or sys.stderr
logger_format = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', 
                                  datefmt='%Y-%m-%d %H:%M:%S')
logger_stream.setFormatter(logger_format)
logger.addHandler(logger_stream)
