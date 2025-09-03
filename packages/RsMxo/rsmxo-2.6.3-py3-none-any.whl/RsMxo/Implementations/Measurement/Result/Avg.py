from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AvgCls:
	"""Avg commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("avg", core, parent)

	def get(self, measIndex=repcap.MeasIndex.Default) -> float:
		"""MEASurement<*>:RESult:AVG \n
		Snippet: value: float = driver.measurement.result.avg.get(measIndex = repcap.MeasIndex.Default) \n
		Return the statistic results of the specified measurement. The measurement type is defined with method RsMxo.Measurement.
		Main.set.
			- [:ACTual]: current measurement result
			- AVG: average of the measurement results
			- EVTCount: number of measurement results in the measurement
			- NPEak: negative peak value of the measurement results
			- PPEak: positive peak value of the measurement results
			- RMS: RMS value of the measurement results
			- STDDev: standard deviation of the measurement results  \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: average: Numeric result value"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:RESult:AVG?')
		return Conversions.str_to_float(response)
