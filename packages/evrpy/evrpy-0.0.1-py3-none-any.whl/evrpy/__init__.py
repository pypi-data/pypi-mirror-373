# __init__.py

# 1) Expose package version (near the top)
try:
    from importlib.metadata import version, PackageNotFoundError  # Python 3.8+
except Exception:  # pragma: no cover
    version = None
    PackageNotFoundError = Exception

try:
    __version__ = version("evrpy") if version else "0.0.0"
except PackageNotFoundError:
    __version__ = "0.0.0"

# Public class imports
from .rpc_calls.addressindex import AddressindexRPC
from .rpc_calls.assets import AssetsRPC
from .rpc_calls.blockchain import BlockchainRPC
from .rpc_calls.control import ControlRPC
from .rpc_calls.generating import GeneratingRPC
from .rpc_calls.messages import MessagesRPC
from .rpc_calls.mining import MiningRPC
from .rpc_calls.network import NetworkRPC
from .rpc_calls.rawtransactions import RawtransactionsRPC
from .rpc_calls.restricted import RestrictedRPC
from .rpc_calls.restrictedassets import RestrictedassetsRPC
from .rpc_calls.rewards import RewardsRPC
from .rpc_calls.util import UtilRPC
from .rpc_calls.wallet import WalletRPC

__all__ = [
    "AddressindexRPC",
    "AssetsRPC",
    "BlockchainRPC",
    "ControlRPC",
    "GeneratingRPC",
    "MessagesRPC",
    "MiningRPC",
    "NetworkRPC",
    "RawtransactionsRPC",
    "RestrictedRPC",
    "RestrictedassetsRPC",
    "RewardsRPC",
    "UtilRPC",
    "WalletRPC",
]

# 2) Make reprs/docs show `evrpy.ClassName` (at the very end)
for _name in __all__:
    _obj = globals().get(_name)
    if _obj is not None and hasattr(_obj, "__module__"):
        _obj.__module__ = "evrpy"
