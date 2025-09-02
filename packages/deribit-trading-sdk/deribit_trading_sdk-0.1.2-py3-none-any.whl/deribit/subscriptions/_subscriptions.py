from dataclasses import dataclass

from .private import PrivateSubscriptions
from .public import PublicSubscriptions

@dataclass(frozen=True)
class Subscriptions(
  PublicSubscriptions,
  PrivateSubscriptions,
):
  ...