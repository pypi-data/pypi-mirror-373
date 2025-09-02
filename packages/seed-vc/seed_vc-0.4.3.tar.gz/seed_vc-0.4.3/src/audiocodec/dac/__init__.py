__version__ = "1.0.0"

# preserved here for legacy reasons
__model_version__ = "latest"

from audiotools.audiotools.ml import BaseModel

BaseModel.INTERN += ["dac.**"]
BaseModel.EXTERN += ["einops"]


from . import nn
from . import model
from . import utils
from .model import DAC
from .model import DACFile
