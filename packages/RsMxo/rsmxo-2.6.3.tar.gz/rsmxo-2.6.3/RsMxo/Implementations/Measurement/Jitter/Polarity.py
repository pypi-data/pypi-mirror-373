from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PolarityCls:
	"""Polarity commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("polarity", core, parent)

	def set(self, polarity: enums.PulseSlope, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:JITTer:POLarity \n
		Snippet: driver.measurement.jitter.polarity.set(polarity = enums.PulseSlope.EITHer, measIndex = repcap.MeasIndex.Default) \n
		For cycle-cycle width and the cycle-cycle duty cycle measurements, the command sets the polarity of pulses for which the
		pulse width is measured: POSitive or NEGative. method RsMxo.Measurement.Main.set is set to measurements CCWidth |
		CCDutycycle. For skew delay and skew phase measurements, the command sets the edge of the first waveform from which the
		measurements starts: POSitive, NEGative or EITHer. method RsMxo.Measurement.Main.set is set to measurements SKWDelay |
		SKWPhase. \n
			:param polarity: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.enum_scalar_to_str(polarity, enums.PulseSlope)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:JITTer:POLarity {param}')

	# noinspection PyTypeChecker
	def get(self, measIndex=repcap.MeasIndex.Default) -> enums.PulseSlope:
		"""MEASurement<*>:JITTer:POLarity \n
		Snippet: value: enums.PulseSlope = driver.measurement.jitter.polarity.get(measIndex = repcap.MeasIndex.Default) \n
		For cycle-cycle width and the cycle-cycle duty cycle measurements, the command sets the polarity of pulses for which the
		pulse width is measured: POSitive or NEGative. method RsMxo.Measurement.Main.set is set to measurements CCWidth |
		CCDutycycle. For skew delay and skew phase measurements, the command sets the edge of the first waveform from which the
		measurements starts: POSitive, NEGative or EITHer. method RsMxo.Measurement.Main.set is set to measurements SKWDelay |
		SKWPhase. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: polarity: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:JITTer:POLarity?')
		return Conversions.str_to_scalar_enum(response, enums.PulseSlope)
