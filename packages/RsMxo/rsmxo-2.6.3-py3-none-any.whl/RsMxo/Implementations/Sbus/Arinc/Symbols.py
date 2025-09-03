from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SymbolsCls:
	"""Symbols commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("symbols", core, parent)

	def set(self, show_symbols: bool, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:ARINc:SYMBols \n
		Snippet: driver.sbus.arinc.symbols.set(show_symbols = False, serialBus = repcap.SerialBus.Default) \n
		Activates the symbol list to be used for decoding. \n
			:param show_symbols: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.bool_to_str(show_symbols)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:ARINc:SYMBols {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> bool:
		"""SBUS<*>:ARINc:SYMBols \n
		Snippet: value: bool = driver.sbus.arinc.symbols.get(serialBus = repcap.SerialBus.Default) \n
		Activates the symbol list to be used for decoding. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: show_symbols: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:ARINc:SYMBols?')
		return Conversions.str_to_bool(response)
