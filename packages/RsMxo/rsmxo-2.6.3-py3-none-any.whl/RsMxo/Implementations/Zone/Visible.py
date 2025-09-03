from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class VisibleCls:
	"""Visible commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("visible", core, parent)

	def set(self, display_state: bool, zone=repcap.Zone.Default) -> None:
		"""ZONE<*>[:VISible] \n
		Snippet: driver.zone.visible.set(display_state = False, zone = repcap.Zone.Default) \n
		Enables the display of the zone on the screen. \n
			:param display_state: No help available
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
		"""
		param = Conversions.bool_to_str(display_state)
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		self._core.io.write(f'ZONE{zone_cmd_val}:VISible {param}')

	def get(self, zone=repcap.Zone.Default) -> bool:
		"""ZONE<*>[:VISible] \n
		Snippet: value: bool = driver.zone.visible.get(zone = repcap.Zone.Default) \n
		Enables the display of the zone on the screen. \n
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:return: display_state: No help available"""
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		response = self._core.io.query_str(f'ZONE{zone_cmd_val}:VISible?')
		return Conversions.str_to_bool(response)
