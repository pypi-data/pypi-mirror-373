from dataclasses import dataclass

from .depth import Depth
from .depth_updates import DepthUpdates
from .trades import Trades

@dataclass(frozen=True)
class PublicSubscriptions(
  Depth,
  DepthUpdates,
  Trades,
):
  ...