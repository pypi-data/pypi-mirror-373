"""Total Connect Device."""

from typing import Any, Dict


class TotalConnectDevice:
    """Device class for Total Connect."""

    def __init__(self, info: Dict[str, Any]) -> None:
        """Initialize device based on DeviceInfoBasic."""
        self.deviceid = info.get("DeviceID")
        self.name = info.get("DeviceName")
        self.class_id = info.get("DeviceClassID")
        self.serial_number = info.get("DeviceSerialNumber")
        self.security_panel_type_id = info.get("SecurityPanelTypeID")
        self.serial_text = info.get("DeviceSerialText")
        self._doorbell_info: Dict[str, Any] = {}
        self._video_info: Dict[str, Any] = {}
        self._unicorn_info: Dict[str, Any] = {}

        flags = info.get("DeviceFlags")
        if not flags:
            self.flags = {}
        else:
            self.flags = dict(x.split("=") for x in flags.split(","))

    def __str__(self) -> str:  # pragma: no cover
        """Return a string that is printable."""
        data = (
            f"DEVICE {self.deviceid} - {self.name}\n"
            f"  ClassID: {self.class_id}\n"
            f"  Security Panel Type ID: {self.security_panel_type_id}\n"
            f"  Serial Number: {self.serial_number}\n"
            f"  Serial Text: {self.serial_text}\n"
        )

        data = data + "  Device Flags:\n"
        for key, value in self.flags.items():
            data = data + f"    {key}: {value}\n"

        data = data + "  WifiDoorbellInfo:\n"
        for key, value in self._doorbell_info.items():
            data = data + f"    {key}: {value}\n"

        data = data + "  VideoPIRInfo:\n"
        for key, value in self._video_info.items():
            data = data + f"    {key}: {value}\n"

        data = data + "  UnicornInfo:\n"
        for key, value in self._unicorn_info.items():
            data = data + f"    {key}: {value}\n"

        return data

    @property
    def doorbell_info(self) -> Dict[str, Any]:
        """Return doorbell info."""
        return self._doorbell_info

    @doorbell_info.setter
    def doorbell_info(self, data: Dict[str, Any]) -> None:
        """Set values based on WifiDoorBellInfo object."""
        if data:
            self._doorbell_info = data

    def is_doorbell(self) -> bool:
        """Return true if a doorbell."""
        if self._doorbell_info and self._doorbell_info["IsExistingDoorBellUser"] == 1:
            return True

        if (
            self._unicorn_info
            and self._unicorn_info["DeviceVariant"] == "home.dv.doorbell"
        ):
            return True

        return False

    @property
    def video_info(self) -> Dict[str, Any]:
        """VideoPIR info."""
        return self._video_info

    @video_info.setter
    def video_info(self, data: Dict[str, Any]) -> None:
        """Set values based on VideoPIRInfo object."""
        if data:
            self._video_info = data

    @property
    def unicorn_info(self) -> Dict[str, Any]:
        """Unicorn info."""
        return self._video_info

    @unicorn_info.setter
    def unicorn_info(self, data: Dict[str, Any]) -> None:
        """Set values based on UnicornInfo object."""
        if data:
            self._unicorn_info = data
