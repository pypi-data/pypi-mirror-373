from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class IntersectCls:
	"""Intersect commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("intersect", core, parent)

	def set(self, intersection: enums.Intersection, zone=repcap.Zone.Default, area=repcap.Area.Default) -> None:
		"""ZONE<*>:AREA<*>:INTersect \n
		Snippet: driver.zone.area.intersect.set(intersection = enums.Intersection.MUST, zone = repcap.Zone.Default, area = repcap.Area.Default) \n
		Defines if the signal must intersect the zone to allow the instrument to trigger, or if it must not intersect the zone. \n
			:param intersection: No help available
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:param area: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Area')
		"""
		param = Conversions.enum_scalar_to_str(intersection, enums.Intersection)
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		area_cmd_val = self._cmd_group.get_repcap_cmd_value(area, repcap.Area)
		self._core.io.write(f'ZONE{zone_cmd_val}:AREA{area_cmd_val}:INTersect {param}')

	# noinspection PyTypeChecker
	def get(self, zone=repcap.Zone.Default, area=repcap.Area.Default) -> enums.Intersection:
		"""ZONE<*>:AREA<*>:INTersect \n
		Snippet: value: enums.Intersection = driver.zone.area.intersect.get(zone = repcap.Zone.Default, area = repcap.Area.Default) \n
		Defines if the signal must intersect the zone to allow the instrument to trigger, or if it must not intersect the zone. \n
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:param area: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Area')
			:return: intersection: No help available"""
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		area_cmd_val = self._cmd_group.get_repcap_cmd_value(area, repcap.Area)
		response = self._core.io.query_str(f'ZONE{zone_cmd_val}:AREA{area_cmd_val}:INTersect?')
		return Conversions.str_to_scalar_enum(response, enums.Intersection)
