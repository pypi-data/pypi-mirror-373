from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SlopeCls:
	"""Slope commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("slope", core, parent)

	def set(self, slope: enums.PulseSlope, measIndex=repcap.MeasIndex.Default, delay=repcap.Delay.Default) -> None:
		"""MEASurement<*>:AMPTime:DELay<*>:SLOPe \n
		Snippet: driver.measurement.ampTime.delay.slope.set(slope = enums.PulseSlope.EITHer, measIndex = repcap.MeasIndex.Default, delay = repcap.Delay.Default) \n
		Sets the edge of each source, between which the delay is measured. \n
			:param slope: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:param delay: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Delay')
		"""
		param = Conversions.enum_scalar_to_str(slope, enums.PulseSlope)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		delay_cmd_val = self._cmd_group.get_repcap_cmd_value(delay, repcap.Delay)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:AMPTime:DELay{delay_cmd_val}:SLOPe {param}')

	# noinspection PyTypeChecker
	def get(self, measIndex=repcap.MeasIndex.Default, delay=repcap.Delay.Default) -> enums.PulseSlope:
		"""MEASurement<*>:AMPTime:DELay<*>:SLOPe \n
		Snippet: value: enums.PulseSlope = driver.measurement.ampTime.delay.slope.get(measIndex = repcap.MeasIndex.Default, delay = repcap.Delay.Default) \n
		Sets the edge of each source, between which the delay is measured. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:param delay: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Delay')
			:return: slope: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		delay_cmd_val = self._cmd_group.get_repcap_cmd_value(delay, repcap.Delay)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:AMPTime:DELay{delay_cmd_val}:SLOPe?')
		return Conversions.str_to_scalar_enum(response, enums.PulseSlope)
