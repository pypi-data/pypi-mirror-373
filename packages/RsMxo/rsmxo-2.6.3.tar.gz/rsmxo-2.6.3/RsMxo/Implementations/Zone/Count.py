from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CountCls:
	"""Count commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("count", core, parent)

	def set(self, count: int, zone=repcap.Zone.Default) -> None:
		"""ZONE<*>:COUNt \n
		Snippet: driver.zone.count.set(count = 1, zone = repcap.Zone.Default) \n
		Returns the number of zones. ZONE:COUNt? MAX returns the maximum number of zones that can be created. \n
			:param count: Number of defined zones
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
		"""
		param = Conversions.decimal_value_to_str(count)
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		self._core.io.write(f'ZONE{zone_cmd_val}:COUNt {param}')

	def get(self, zone=repcap.Zone.Default) -> int:
		"""ZONE<*>:COUNt \n
		Snippet: value: int = driver.zone.count.get(zone = repcap.Zone.Default) \n
		Returns the number of zones. ZONE:COUNt? MAX returns the maximum number of zones that can be created. \n
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:return: count: Number of defined zones"""
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		response = self._core.io.query_str(f'ZONE{zone_cmd_val}:COUNt?')
		return Conversions.str_to_int(response)
