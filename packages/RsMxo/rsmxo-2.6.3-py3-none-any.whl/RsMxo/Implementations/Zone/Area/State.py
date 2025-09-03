from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, state: bool, zone=repcap.Zone.Default, area=repcap.Area.Default) -> None:
		"""ZONE<*>:AREA<*>:STATe \n
		Snippet: driver.zone.area.state.set(state = False, zone = repcap.Zone.Default, area = repcap.Area.Default) \n
		Enables the selected area. \n
			:param state: No help available
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:param area: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Area')
		"""
		param = Conversions.bool_to_str(state)
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		area_cmd_val = self._cmd_group.get_repcap_cmd_value(area, repcap.Area)
		self._core.io.write(f'ZONE{zone_cmd_val}:AREA{area_cmd_val}:STATe {param}')

	def get(self, zone=repcap.Zone.Default, area=repcap.Area.Default) -> bool:
		"""ZONE<*>:AREA<*>:STATe \n
		Snippet: value: bool = driver.zone.area.state.get(zone = repcap.Zone.Default, area = repcap.Area.Default) \n
		Enables the selected area. \n
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:param area: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Area')
			:return: state: No help available"""
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		area_cmd_val = self._cmd_group.get_repcap_cmd_value(area, repcap.Area)
		response = self._core.io.query_str(f'ZONE{zone_cmd_val}:AREA{area_cmd_val}:STATe?')
		return Conversions.str_to_bool(response)
