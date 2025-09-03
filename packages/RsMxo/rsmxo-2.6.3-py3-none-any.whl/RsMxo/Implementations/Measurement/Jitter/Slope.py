from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SlopeCls:
	"""Slope commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("slope", core, parent)

	def set(self, slope: enums.PeriodSlope, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:JITTer:SLOPe \n
		Snippet: driver.measurement.jitter.slope.set(slope = enums.PeriodSlope.EITHer, measIndex = repcap.MeasIndex.Default) \n
		For cycle-cycle jitter, N-cycle jitter, and cycle-cycle duty cycle measurements, the setting selects the slope at which
		the periods and thus the jitter is measured: FIRSt, POSitive, NEGative or EITHer. method RsMxo.Measurement.Main.set is
		set to measurements CCJitter | NCJitter | CCDutycycle. For time-interval error measurements, the command sets the edges
		of the data signal that are used for measurements: POSitive, NEGative or EITHer. method RsMxo.Measurement.Main.set is set
		to TIE. \n
			:param slope:
				- FIRSt: Measures the period from the first edge that is found, no matter of its direction.
				- POSitive: Measures the period at positive going edges.
				- NEGative: Measures the period at negative going edges.
				- EITHer: Measures the period at both positive and negative going edges. This option is useful, for example, to check the clock stability of a double data rate clock.
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')"""
		param = Conversions.enum_scalar_to_str(slope, enums.PeriodSlope)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:JITTer:SLOPe {param}')

	# noinspection PyTypeChecker
	def get(self, measIndex=repcap.MeasIndex.Default) -> enums.PeriodSlope:
		"""MEASurement<*>:JITTer:SLOPe \n
		Snippet: value: enums.PeriodSlope = driver.measurement.jitter.slope.get(measIndex = repcap.MeasIndex.Default) \n
		For cycle-cycle jitter, N-cycle jitter, and cycle-cycle duty cycle measurements, the setting selects the slope at which
		the periods and thus the jitter is measured: FIRSt, POSitive, NEGative or EITHer. method RsMxo.Measurement.Main.set is
		set to measurements CCJitter | NCJitter | CCDutycycle. For time-interval error measurements, the command sets the edges
		of the data signal that are used for measurements: POSitive, NEGative or EITHer. method RsMxo.Measurement.Main.set is set
		to TIE. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: slope:
				- FIRSt: Measures the period from the first edge that is found, no matter of its direction.
				- POSitive: Measures the period at positive going edges.
				- NEGative: Measures the period at negative going edges.
				- EITHer: Measures the period at both positive and negative going edges. This option is useful, for example, to check the clock stability of a double data rate clock."""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:JITTer:SLOPe?')
		return Conversions.str_to_scalar_enum(response, enums.PeriodSlope)
