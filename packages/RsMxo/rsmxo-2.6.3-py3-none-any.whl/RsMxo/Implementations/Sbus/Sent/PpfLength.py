from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PpfLengthCls:
	"""PpfLength commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ppfLength", core, parent)

	def set(self, frame_length: int, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SENT:PPFLength \n
		Snippet: driver.sbus.sent.ppfLength.set(frame_length = 1, serialBus = repcap.SerialBus.Default) \n
		No command help available \n
			:param frame_length: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(frame_length)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SENT:PPFLength {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> int:
		"""SBUS<*>:SENT:PPFLength \n
		Snippet: value: int = driver.sbus.sent.ppfLength.get(serialBus = repcap.SerialBus.Default) \n
		No command help available \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: frame_length: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SENT:PPFLength?')
		return Conversions.str_to_int(response)
