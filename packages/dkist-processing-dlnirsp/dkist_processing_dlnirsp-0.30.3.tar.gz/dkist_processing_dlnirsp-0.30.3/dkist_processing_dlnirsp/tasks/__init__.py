"""Top-level tasks that can be assembled into a pipeline workflow."""

from dkist_processing_dlnirsp.tasks.assemble_movie import *
from dkist_processing_dlnirsp.tasks.bad_pixel_map import *
from dkist_processing_dlnirsp.tasks.dark import *
from dkist_processing_dlnirsp.tasks.geometric import *
from dkist_processing_dlnirsp.tasks.ifu_drift import *
from dkist_processing_dlnirsp.tasks.instrument_polarization import *
from dkist_processing_dlnirsp.tasks.l1_output_data import *
from dkist_processing_dlnirsp.tasks.lamp import *
from dkist_processing_dlnirsp.tasks.linearity_correction import *
from dkist_processing_dlnirsp.tasks.make_movie_frames import *
from dkist_processing_dlnirsp.tasks.parse import *
from dkist_processing_dlnirsp.tasks.quality_metrics import *
from dkist_processing_dlnirsp.tasks.science import *
from dkist_processing_dlnirsp.tasks.solar import *
from dkist_processing_dlnirsp.tasks.wavelength_calibration import *
from dkist_processing_dlnirsp.tasks.write_l1 import *
