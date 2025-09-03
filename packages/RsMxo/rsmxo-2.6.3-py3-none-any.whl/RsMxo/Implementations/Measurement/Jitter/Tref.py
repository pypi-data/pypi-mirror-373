from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TrefCls:
	"""Tref commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("tref", core, parent)

	def set(self, tim_ref: float, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:JITTer:TREF \n
		Snippet: driver.measurement.jitter.tref.set(tim_ref = 1.0, measIndex = repcap.MeasIndex.Default) \n
		Selects the timing reference, which is one of the available clock configurations. The timing reference must be defined
		before it can be used. \n
			:param tim_ref: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.decimal_value_to_str(tim_ref)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:JITTer:TREF {param}')

	def get(self, measIndex=repcap.MeasIndex.Default) -> float:
		"""MEASurement<*>:JITTer:TREF \n
		Snippet: value: float = driver.measurement.jitter.tref.get(measIndex = repcap.MeasIndex.Default) \n
		Selects the timing reference, which is one of the available clock configurations. The timing reference must be defined
		before it can be used. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: tim_ref: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:JITTer:TREF?')
		return Conversions.str_to_float(response)
