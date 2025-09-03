from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RemoveCls:
	"""Remove commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("remove", core, parent)

	def set(self, zone=repcap.Zone.Default, area=repcap.Area.Default) -> None:
		"""ZONE<*>:AREA<*>:REMove \n
		Snippet: driver.zone.area.remove.set(zone = repcap.Zone.Default, area = repcap.Area.Default) \n
		Removes the selected area from the trigger zone. \n
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:param area: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Area')
		"""
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		area_cmd_val = self._cmd_group.get_repcap_cmd_value(area, repcap.Area)
		self._core.io.write(f'ZONE{zone_cmd_val}:AREA{area_cmd_val}:REMove')

	def set_and_wait(self, zone=repcap.Zone.Default, area=repcap.Area.Default, opc_timeout_ms: int = -1) -> None:
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		area_cmd_val = self._cmd_group.get_repcap_cmd_value(area, repcap.Area)
		"""ZONE<*>:AREA<*>:REMove \n
		Snippet: driver.zone.area.remove.set_and_wait(zone = repcap.Zone.Default, area = repcap.Area.Default) \n
		Removes the selected area from the trigger zone. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:param area: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Area')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'ZONE{zone_cmd_val}:AREA{area_cmd_val}:REMove', opc_timeout_ms)
