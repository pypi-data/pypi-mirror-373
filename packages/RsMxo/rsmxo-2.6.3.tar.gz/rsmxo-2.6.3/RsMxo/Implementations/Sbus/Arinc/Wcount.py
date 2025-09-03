from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class WcountCls:
	"""Wcount commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("wcount", core, parent)

	def get(self, serialBus=repcap.SerialBus.Default) -> int:
		"""SBUS<*>:ARINc:WCOunt \n
		Snippet: value: int = driver.sbus.arinc.wcount.get(serialBus = repcap.SerialBus.Default) \n
		Returns the number of decoded words. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: count: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:ARINc:WCOunt?')
		return Conversions.str_to_int(response)
