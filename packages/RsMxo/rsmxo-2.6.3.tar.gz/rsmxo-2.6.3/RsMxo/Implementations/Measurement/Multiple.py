from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MultipleCls:
	"""Multiple commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("multiple", core, parent)

	def set(self, global_meass_all: bool, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:MULTiple \n
		Snippet: driver.measurement.multiple.set(global_meass_all = False, measIndex = repcap.MeasIndex.Default) \n
		If ON, the measurement is performed repeatedly if the measured parameter occurs several times inside the acquisition or
		defined gate. All results are included in evaluation, e.g. in statistics. To set the number of results to be considered,
		use method RsMxo.Measurement.MnoMeas.set. \n
			:param global_meass_all: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.bool_to_str(global_meass_all)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:MULTiple {param}')

	def get(self, measIndex=repcap.MeasIndex.Default) -> bool:
		"""MEASurement<*>:MULTiple \n
		Snippet: value: bool = driver.measurement.multiple.get(measIndex = repcap.MeasIndex.Default) \n
		If ON, the measurement is performed repeatedly if the measured parameter occurs several times inside the acquisition or
		defined gate. All results are included in evaluation, e.g. in statistics. To set the number of results to be considered,
		use method RsMxo.Measurement.MnoMeas.set. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: global_meass_all: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:MULTiple?')
		return Conversions.str_to_bool(response)
