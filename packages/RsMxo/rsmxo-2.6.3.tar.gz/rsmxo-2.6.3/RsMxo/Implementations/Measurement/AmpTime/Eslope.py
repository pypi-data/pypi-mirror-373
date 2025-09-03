from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EslopeCls:
	"""Eslope commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("eslope", core, parent)

	def set(self, edges_slope: enums.PulseSlope, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:AMPTime:ESLope \n
		Snippet: driver.measurement.ampTime.eslope.set(edges_slope = enums.PulseSlope.EITHer, measIndex = repcap.MeasIndex.Default) \n
		Sets the edge direction to be counted: rising edges, falling edges, or both. The setting is only relevant for edge count
		measurement method RsMxo.Measurement.Main.set is set to EDGecount. \n
			:param edges_slope: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.enum_scalar_to_str(edges_slope, enums.PulseSlope)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:AMPTime:ESLope {param}')

	# noinspection PyTypeChecker
	def get(self, measIndex=repcap.MeasIndex.Default) -> enums.PulseSlope:
		"""MEASurement<*>:AMPTime:ESLope \n
		Snippet: value: enums.PulseSlope = driver.measurement.ampTime.eslope.get(measIndex = repcap.MeasIndex.Default) \n
		Sets the edge direction to be counted: rising edges, falling edges, or both. The setting is only relevant for edge count
		measurement method RsMxo.Measurement.Main.set is set to EDGecount. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: edges_slope: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:AMPTime:ESLope?')
		return Conversions.str_to_scalar_enum(response, enums.PulseSlope)
