from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SelectCls:
	"""Select commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("select", core, parent)

	def set(self, max_gap_select: bool, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:ARINc:MAXGap:SELect \n
		Snippet: driver.sbus.arinc.maxGap.select.set(max_gap_select = False, serialBus = repcap.SerialBus.Default) \n
		Enables the detection of the maximum gap time during decoding. You can specify the maximum gap time withmethod RsMxo.Sbus.
		Arinc.MaxGap.Bits.set. \n
			:param max_gap_select: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.bool_to_str(max_gap_select)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:ARINc:MAXGap:SELect {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> bool:
		"""SBUS<*>:ARINc:MAXGap:SELect \n
		Snippet: value: bool = driver.sbus.arinc.maxGap.select.get(serialBus = repcap.SerialBus.Default) \n
		Enables the detection of the maximum gap time during decoding. You can specify the maximum gap time withmethod RsMxo.Sbus.
		Arinc.MaxGap.Bits.set. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: max_gap_select: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:ARINc:MAXGap:SELect?')
		return Conversions.str_to_bool(response)
