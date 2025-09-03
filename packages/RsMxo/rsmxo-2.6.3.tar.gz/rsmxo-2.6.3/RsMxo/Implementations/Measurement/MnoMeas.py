from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MnoMeasCls:
	"""MnoMeas commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mnoMeas", core, parent)

	def set(self, global_max_meas_per_acq: int, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:MNOMeas \n
		Snippet: driver.measurement.mnoMeas.set(global_max_meas_per_acq = 1, measIndex = repcap.MeasIndex.Default) \n
		Sets the maximum number of measurements per acquisition if method RsMxo.Measurement.Multiple.set is on. The setting
		affects all measurements. \n
			:param global_max_meas_per_acq: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.decimal_value_to_str(global_max_meas_per_acq)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:MNOMeas {param}')

	def get(self, measIndex=repcap.MeasIndex.Default) -> int:
		"""MEASurement<*>:MNOMeas \n
		Snippet: value: int = driver.measurement.mnoMeas.get(measIndex = repcap.MeasIndex.Default) \n
		Sets the maximum number of measurements per acquisition if method RsMxo.Measurement.Multiple.set is on. The setting
		affects all measurements. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: global_max_meas_per_acq: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:MNOMeas?')
		return Conversions.str_to_int(response)
