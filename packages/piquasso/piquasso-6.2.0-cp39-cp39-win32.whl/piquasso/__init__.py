#
# Copyright 2021-2025 Budapest Quantum Computing Group
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The Piquasso module.

One can access all the instructions and states from here as attributes.
"""


# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'piquasso.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-piquasso-6.2.0')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-piquasso-6.2.0')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

from piquasso import cvqnn
from piquasso import fermionic

from piquasso.api.mode import Q
from piquasso.api.config import Config
from piquasso.api.instruction import (
    Instruction,
    Preparation,
    Gate,
    Measurement,
)
from piquasso.api.program import Program
from piquasso.api.state import State
from piquasso.api.computer import Computer
from piquasso.api.simulator import Simulator
from piquasso.api.utils import as_code

from piquasso._simulators.sampling import SamplingState, SamplingSimulator

from piquasso._simulators.gaussian import GaussianState, GaussianSimulator
from piquasso._simulators.fock import (
    FockState,
    PureFockState,
    BatchPureFockState,
    FockSimulator,
    PureFockSimulator,
)

from piquasso._simulators.connectors import (
    NumpyConnector,
    TensorflowConnector,
    JaxConnector,
)

from .instructions.preparations import (
    Vacuum,
    Mean,
    Covariance,
    Thermal,
    StateVector,
    DensityMatrix,
    Create,
    Annihilate,
)

from .instructions.gates import (
    GaussianTransform,
    Phaseshifter,
    Beamsplitter,
    Beamsplitter5050,
    MachZehnder,
    Fourier,
    Displacement,
    PositionDisplacement,
    MomentumDisplacement,
    Squeezing,
    QuadraticPhase,
    Squeezing2,
    Kerr,
    CrossKerr,
    ControlledX,
    ControlledZ,
    Interferometer,
    Graph,
    CubicPhase,
)

from .instructions.measurements import (
    ParticleNumberMeasurement,
    ThresholdMeasurement,
    HomodyneMeasurement,
    HeterodyneMeasurement,
    GeneraldyneMeasurement,
    PostSelectPhotons,
    ImperfectPostSelectPhotons,
)

from .instructions.channels import (
    DeterministicGaussianChannel,
    Attenuator,
    Loss,
    LossyInterferometer,
)

from .instructions.batch import (
    BatchPrepare,
    BatchApply,
)


__all__ = [
    # API
    "Program",
    "Q",
    "Config",
    "Instruction",
    "Preparation",
    "Gate",
    "Measurement",
    "State",
    "Computer",
    "Simulator",
    "as_code",
    # Simulators
    "GaussianSimulator",
    "SamplingSimulator",
    "FockSimulator",
    "PureFockSimulator",
    # Connectors
    "NumpyConnector",
    "TensorflowConnector",
    "JaxConnector",
    # States
    "GaussianState",
    "SamplingState",
    "FockState",
    "PureFockState",
    "BatchPureFockState",
    # Preparations
    "Vacuum",
    "Mean",
    "Covariance",
    "Thermal",
    "StateVector",
    "DensityMatrix",
    "Create",
    "Annihilate",
    # Gates
    "GaussianTransform",
    "Phaseshifter",
    "Beamsplitter",
    "Beamsplitter5050",
    "MachZehnder",
    "Fourier",
    "Displacement",
    "PositionDisplacement",
    "MomentumDisplacement",
    "Squeezing",
    "QuadraticPhase",
    "Squeezing2",
    "Kerr",
    "CrossKerr",
    "CubicPhase",
    "ControlledX",
    "ControlledZ",
    "Interferometer",
    "Graph",
    # Measurements
    "ParticleNumberMeasurement",
    "ThresholdMeasurement",
    "HomodyneMeasurement",
    "HeterodyneMeasurement",
    "GeneraldyneMeasurement",
    "PostSelectPhotons",
    "ImperfectPostSelectPhotons",
    # Channels
    "DeterministicGaussianChannel",
    "Attenuator",
    "Loss",
    "LossyInterferometer",
    # Batch
    "BatchPrepare",
    "BatchApply",
    # Modules
    "cvqnn",
    "fermionic",
]

__version__ = "6.2.0"
