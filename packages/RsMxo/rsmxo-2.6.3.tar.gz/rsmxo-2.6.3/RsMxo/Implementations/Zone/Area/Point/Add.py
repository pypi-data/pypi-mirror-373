from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AddCls:
	"""Add commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("add", core, parent)

	def set(self, zone=repcap.Zone.Default, area=repcap.Area.Default, point=repcap.Point.Default) -> None:
		"""ZONE<*>:AREA<*>:POINt<*>:ADD \n
		Snippet: driver.zone.area.point.add.set(zone = repcap.Zone.Default, area = repcap.Area.Default, point = repcap.Point.Default) \n
		Adds a new point to the area at the indicated point index. To define the coordinates of the point, use method RsMxo.Zone.
		Area.Point.X.set and method RsMxo.Zone.Area.Point.Y.set. \n
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:param area: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Area')
			:param point: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Point')
		"""
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		area_cmd_val = self._cmd_group.get_repcap_cmd_value(area, repcap.Area)
		point_cmd_val = self._cmd_group.get_repcap_cmd_value(point, repcap.Point)
		self._core.io.write(f'ZONE{zone_cmd_val}:AREA{area_cmd_val}:POINt{point_cmd_val}:ADD')

	def set_and_wait(self, zone=repcap.Zone.Default, area=repcap.Area.Default, point=repcap.Point.Default, opc_timeout_ms: int = -1) -> None:
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		area_cmd_val = self._cmd_group.get_repcap_cmd_value(area, repcap.Area)
		point_cmd_val = self._cmd_group.get_repcap_cmd_value(point, repcap.Point)
		"""ZONE<*>:AREA<*>:POINt<*>:ADD \n
		Snippet: driver.zone.area.point.add.set_and_wait(zone = repcap.Zone.Default, area = repcap.Area.Default, point = repcap.Point.Default) \n
		Adds a new point to the area at the indicated point index. To define the coordinates of the point, use method RsMxo.Zone.
		Area.Point.X.set and method RsMxo.Zone.Area.Point.Y.set. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:param area: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Area')
			:param point: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Point')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'ZONE{zone_cmd_val}:AREA{area_cmd_val}:POINt{point_cmd_val}:ADD', opc_timeout_ms)
