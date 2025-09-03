from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, protocol_state: bool, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>[:STATe] \n
		Snippet: driver.sbus.state.set(protocol_state = False, serialBus = repcap.SerialBus.Default) \n
		Enables the decoding of the specified bus. \n
			:param protocol_state: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.bool_to_str(protocol_state)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:STATe {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> bool:
		"""SBUS<*>[:STATe] \n
		Snippet: value: bool = driver.sbus.state.get(serialBus = repcap.SerialBus.Default) \n
		Enables the decoding of the specified bus. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: protocol_state: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:STATe?')
		return Conversions.str_to_bool(response)
