from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CountCls:
	"""Count commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("count", core, parent)

	def get(self, measIndex=repcap.MeasIndex.Default) -> int:
		"""MEASurement<*>:COUNt \n
		Snippet: value: int = driver.measurement.count.get(measIndex = repcap.MeasIndex.Default) \n
		Returns the maximum number of measurements, which is the maximum value for the <mg> suffix. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: count: Maximum number of measurements"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:COUNt?')
		return Conversions.str_to_int(response)
