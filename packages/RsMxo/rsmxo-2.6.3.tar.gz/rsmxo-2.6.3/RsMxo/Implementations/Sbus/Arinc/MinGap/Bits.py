from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BitsCls:
	"""Bits commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("bits", core, parent)

	def set(self, min_gap_bits: int, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:ARINc:MINGap:BITS \n
		Snippet: driver.sbus.arinc.minGap.bits.set(min_gap_bits = 1, serialBus = repcap.SerialBus.Default) \n
		Sets a value for the minimum timing gap between two words. See also: method RsMxo.Sbus.Arinc.MinGap.Select.set. \n
			:param min_gap_bits: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(min_gap_bits)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:ARINc:MINGap:BITS {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> int:
		"""SBUS<*>:ARINc:MINGap:BITS \n
		Snippet: value: int = driver.sbus.arinc.minGap.bits.get(serialBus = repcap.SerialBus.Default) \n
		Sets a value for the minimum timing gap between two words. See also: method RsMxo.Sbus.Arinc.MinGap.Select.set. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: min_gap_bits: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:ARINc:MINGap:BITS?')
		return Conversions.str_to_int(response)
