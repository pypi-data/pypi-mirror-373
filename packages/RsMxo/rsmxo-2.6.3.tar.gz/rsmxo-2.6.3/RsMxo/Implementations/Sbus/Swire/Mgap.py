from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MgapCls:
	"""Mgap commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mgap", core, parent)

	def set(self, min_gap_time: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SWIRe:MGAP \n
		Snippet: driver.sbus.swire.mgap.set(min_gap_time = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets the minimum duration of a gap. Any inactivity greater than this time is interpreted as a gap and leads to a
		resynchronization to the signal. \n
			:param min_gap_time: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(min_gap_time)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SWIRe:MGAP {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:SWIRe:MGAP \n
		Snippet: value: float = driver.sbus.swire.mgap.get(serialBus = repcap.SerialBus.Default) \n
		Sets the minimum duration of a gap. Any inactivity greater than this time is interpreted as a gap and leads to a
		resynchronization to the signal. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: min_gap_time: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SWIRe:MGAP?')
		return Conversions.str_to_float(response)
