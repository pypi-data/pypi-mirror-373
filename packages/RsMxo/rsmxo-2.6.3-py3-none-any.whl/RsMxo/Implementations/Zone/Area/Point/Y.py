from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class YCls:
	"""Y commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("y", core, parent)

	def set(self, y: float, zone=repcap.Zone.Default, area=repcap.Area.Default, point=repcap.Point.Default) -> None:
		"""ZONE<*>:AREA<*>:POINt<*>:Y \n
		Snippet: driver.zone.area.point.y.set(y = 1.0, zone = repcap.Zone.Default, area = repcap.Area.Default, point = repcap.Point.Default) \n
		Sets the vertical Y coordinates for the selected point of the area. \n
			:param y: No help available
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:param area: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Area')
			:param point: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Point')
		"""
		param = Conversions.decimal_value_to_str(y)
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		area_cmd_val = self._cmd_group.get_repcap_cmd_value(area, repcap.Area)
		point_cmd_val = self._cmd_group.get_repcap_cmd_value(point, repcap.Point)
		self._core.io.write(f'ZONE{zone_cmd_val}:AREA{area_cmd_val}:POINt{point_cmd_val}:Y {param}')

	def get(self, zone=repcap.Zone.Default, area=repcap.Area.Default, point=repcap.Point.Default) -> float:
		"""ZONE<*>:AREA<*>:POINt<*>:Y \n
		Snippet: value: float = driver.zone.area.point.y.get(zone = repcap.Zone.Default, area = repcap.Area.Default, point = repcap.Point.Default) \n
		Sets the vertical Y coordinates for the selected point of the area. \n
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:param area: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Area')
			:param point: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Point')
			:return: y: No help available"""
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		area_cmd_val = self._cmd_group.get_repcap_cmd_value(area, repcap.Area)
		point_cmd_val = self._cmd_group.get_repcap_cmd_value(point, repcap.Point)
		response = self._core.io.query_str(f'ZONE{zone_cmd_val}:AREA{area_cmd_val}:POINt{point_cmd_val}:Y?')
		return Conversions.str_to_float(response)
