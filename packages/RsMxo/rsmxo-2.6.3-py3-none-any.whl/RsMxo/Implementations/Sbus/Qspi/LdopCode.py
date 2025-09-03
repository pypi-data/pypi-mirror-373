from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LdopCodeCls:
	"""LdopCode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ldopCode", core, parent)

	def set(self, filename: str, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:QSPI:LDOPcode \n
		Snippet: driver.sbus.qspi.ldopCode.set(filename = 'abc', serialBus = repcap.SerialBus.Default) \n
		Loads an opcode file from the selected file. \n
			:param filename: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.value_to_quoted_str(filename)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:QSPI:LDOPcode {param}')
