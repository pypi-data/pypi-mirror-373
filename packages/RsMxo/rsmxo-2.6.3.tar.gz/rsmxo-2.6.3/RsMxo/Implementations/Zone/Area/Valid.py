from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValidCls:
	"""Valid commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("valid", core, parent)

	def get(self, zone=repcap.Zone.Default, area=repcap.Area.Default) -> bool:
		"""ZONE<*>:AREA<*>:VALid \n
		Snippet: value: bool = driver.zone.area.valid.get(zone = repcap.Zone.Default, area = repcap.Area.Default) \n
		Checks the validity of the indicated zone area. The area is invalid if one of its points is invalid. See Figure 'Invalid
		zone area (left) and valid zone area (right) '. \n
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:param area: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Area')
			:return: valid: No help available"""
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		area_cmd_val = self._cmd_group.get_repcap_cmd_value(area, repcap.Area)
		response = self._core.io.query_str(f'ZONE{zone_cmd_val}:AREA{area_cmd_val}:VALid?')
		return Conversions.str_to_bool(response)
