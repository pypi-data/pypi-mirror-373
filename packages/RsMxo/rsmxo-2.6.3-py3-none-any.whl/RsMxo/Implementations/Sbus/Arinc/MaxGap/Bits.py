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

	def set(self, max_gap_bits: int, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:ARINc:MAXGap:BITS \n
		Snippet: driver.sbus.arinc.maxGap.bits.set(max_gap_bits = 1, serialBus = repcap.SerialBus.Default) \n
		Sets the value for the maximum gap between two words. See also: method RsMxo.Sbus.Arinc.MaxGap.Select.set. \n
			:param max_gap_bits: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(max_gap_bits)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:ARINc:MAXGap:BITS {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> int:
		"""SBUS<*>:ARINc:MAXGap:BITS \n
		Snippet: value: int = driver.sbus.arinc.maxGap.bits.get(serialBus = repcap.SerialBus.Default) \n
		Sets the value for the maximum gap between two words. See also: method RsMxo.Sbus.Arinc.MaxGap.Select.set. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: max_gap_bits: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:ARINc:MAXGap:BITS?')
		return Conversions.str_to_int(response)
