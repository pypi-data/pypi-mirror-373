"""Total Connect Partition."""

import logging
from typing import Any, Dict

from .const import PROJECT_URL, ArmingState, ArmType
from .exceptions import PartialResponseError, TotalConnectError

LOGGER = logging.getLogger(__name__)


class TotalConnectPartition:
    """Partition class for Total Connect."""

    def __init__(self, details: Dict[str, Any], parent):
        """Initialize Partition based on PartitionDetails."""
        self.parent = parent
        self.partitionid = details.get("PartitionID")
        self.name = details.get("PartitionName")
        self.is_stay_armed = details.get("IsStayArmed")
        self.is_fire_enabled = details.get("IsFireEnabled")
        self.is_common_enabled = details.get("IsCommonEnabled")
        self.is_locked = details.get("IsLocked")
        self.is_new_partition = details.get("IsNewPartition")
        self.is_night_stay_enabled = details.get("IsNightStayEnabled")
        self.exit_delay_timer = details.get("ExitDelayTimer")
        self._update(details)

    def __str__(self) -> str:  # pragma: no cover
        """Return a string that is printable."""
        data = (
            f"PARTITION {self.partitionid} - {self.name}\n"
            f"  {self.arming_state}\n"
            f"  Stay armed: {self.is_stay_armed}\tFire enabled: {self.is_fire_enabled}\n"
            f"  Common enabled: {self.is_common_enabled}\tLocked: {self.is_locked}\n"
            f"  New: {self.is_new_partition}\tNight Stay enabled: {self.is_night_stay_enabled}\n"
            f"  Exit delay: {self.exit_delay_timer}\n"
        )

        return data

    def arm(self, arm_type: ArmType, usercode: str = "") -> None:
        """Arm the partition."""
        self.parent.arm(arm_type, self.partitionid, usercode)

    def disarm(self, usercode: str = "") -> None:
        """Disarm the partition."""
        self.parent.disarm(self.partitionid, usercode)

    def _update(self, info: Dict[str, Any]) -> None:
        """Update partition based on PartitionInfo."""
        astate = (info or {}).get("ArmingState")
        if astate is None:
            raise PartialResponseError("no ArmingState")
        try:
            self.arming_state = ArmingState(astate)
        except ValueError:
            LOGGER.error(
                f"unknown partition ArmingState {astate} in {info}: report at {PROJECT_URL}/issues"
            )
            raise TotalConnectError(
                f"unknown partition ArmingState {astate} in {info}"
            ) from None
