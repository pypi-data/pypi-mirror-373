from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CountCls:
	"""Count commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("count", core, parent)

	def set(self, count: int, zone=repcap.Zone.Default, area=repcap.Area.Default, point=repcap.Point.Default) -> None:
		"""ZONE<*>:AREA<*>:POINt<*>:COUNt \n
		Snippet: driver.zone.area.point.count.set(count = 1, zone = repcap.Zone.Default, area = repcap.Area.Default, point = repcap.Point.Default) \n
		Queries the number of the defined points in the area. ZONE<m>:AREA<n>:POINt:COUNt? MAX returns the maximum number of
		points that can be created. \n
			:param count: No help available
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:param area: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Area')
			:param point: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Point')
		"""
		param = Conversions.decimal_value_to_str(count)
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		area_cmd_val = self._cmd_group.get_repcap_cmd_value(area, repcap.Area)
		point_cmd_val = self._cmd_group.get_repcap_cmd_value(point, repcap.Point)
		self._core.io.write(f'ZONE{zone_cmd_val}:AREA{area_cmd_val}:POINt{point_cmd_val}:COUNt {param}')

	def get(self, zone=repcap.Zone.Default, area=repcap.Area.Default, point=repcap.Point.Default) -> int:
		"""ZONE<*>:AREA<*>:POINt<*>:COUNt \n
		Snippet: value: int = driver.zone.area.point.count.get(zone = repcap.Zone.Default, area = repcap.Area.Default, point = repcap.Point.Default) \n
		Queries the number of the defined points in the area. ZONE<m>:AREA<n>:POINt:COUNt? MAX returns the maximum number of
		points that can be created. \n
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:param area: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Area')
			:param point: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Point')
			:return: count: No help available"""
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		area_cmd_val = self._cmd_group.get_repcap_cmd_value(area, repcap.Area)
		point_cmd_val = self._cmd_group.get_repcap_cmd_value(point, repcap.Point)
		response = self._core.io.query_str(f'ZONE{zone_cmd_val}:AREA{area_cmd_val}:POINt{point_cmd_val}:COUNt?')
		return Conversions.str_to_int(response)
