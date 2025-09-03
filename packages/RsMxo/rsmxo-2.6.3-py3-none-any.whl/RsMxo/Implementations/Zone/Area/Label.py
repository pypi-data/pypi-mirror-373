from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LabelCls:
	"""Label commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("label", core, parent)

	def set(self, label: str, zone=repcap.Zone.Default, area=repcap.Area.Default) -> None:
		"""ZONE<*>:AREA<*>:LABel \n
		Snippet: driver.zone.area.label.set(label = 'abc', zone = repcap.Zone.Default, area = repcap.Area.Default) \n
		Defines a label for the selected area. \n
			:param label: No help available
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:param area: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Area')
		"""
		param = Conversions.value_to_quoted_str(label)
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		area_cmd_val = self._cmd_group.get_repcap_cmd_value(area, repcap.Area)
		self._core.io.write(f'ZONE{zone_cmd_val}:AREA{area_cmd_val}:LABel {param}')

	def get(self, zone=repcap.Zone.Default, area=repcap.Area.Default) -> str:
		"""ZONE<*>:AREA<*>:LABel \n
		Snippet: value: str = driver.zone.area.label.get(zone = repcap.Zone.Default, area = repcap.Area.Default) \n
		Defines a label for the selected area. \n
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:param area: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Area')
			:return: label: No help available"""
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		area_cmd_val = self._cmd_group.get_repcap_cmd_value(area, repcap.Area)
		response = self._core.io.query_str(f'ZONE{zone_cmd_val}:AREA{area_cmd_val}:LABel?')
		return trim_str_response(response)
