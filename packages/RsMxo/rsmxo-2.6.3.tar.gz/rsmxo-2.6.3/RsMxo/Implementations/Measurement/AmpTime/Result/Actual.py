from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ActualCls:
	"""Actual commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("actual", core, parent)

	def get(self, measIndex=repcap.MeasIndex.Default) -> float:
		"""MEASurement<*>:AMPTime:RESult:ACTual \n
		Snippet: value: float = driver.measurement.ampTime.result.actual.get(measIndex = repcap.MeasIndex.Default) \n
		No command help available \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: actual: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:AMPTime:RESult:ACTual?')
		return Conversions.str_to_float(response)
