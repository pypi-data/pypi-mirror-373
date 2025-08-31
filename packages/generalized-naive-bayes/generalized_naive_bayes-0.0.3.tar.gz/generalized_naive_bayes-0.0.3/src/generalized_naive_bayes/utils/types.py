from typing import Annotated

import numpy as np
from numpy.typing import NDArray

Vector1D = Annotated[NDArray[np.float64], (1,)]
Vector2D = Annotated[NDArray[np.float64], (2,)]
