from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SymbolRateCls:
	"""SymbolRate commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("symbolRate", core, parent)

	def get_value(self) -> float:
		"""ACQuire:SRATe[:VALue] \n
		Snippet: value: float = driver.acquire.symbolRate.get_value() \n
		Sets the number of waveform points per second if method RsMxo.Acquire.SymbolRate.mode is set to MANual. \n
			:return: sample_rate: No help available
		"""
		response = self._core.io.query_str('ACQuire:SRATe:VALue?')
		return Conversions.str_to_float(response)

	def set_value(self, sample_rate: float) -> None:
		"""ACQuire:SRATe[:VALue] \n
		Snippet: driver.acquire.symbolRate.set_value(sample_rate = 1.0) \n
		Sets the number of waveform points per second if method RsMxo.Acquire.SymbolRate.mode is set to MANual. \n
			:param sample_rate: No help available
		"""
		param = Conversions.decimal_value_to_str(sample_rate)
		self._core.io.write(f'ACQuire:SRATe:VALue {param}')

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.AutoManualMode:
		"""ACQuire:SRATe:MODE \n
		Snippet: value: enums.AutoManualMode = driver.acquire.symbolRate.get_mode() \n
		Defines how the sample rate is set. The sample rate considers the samples of the ADC, and the processing of the captured
		samples including interpolation. \n
			:return: sample_rate_mode:
				- AUTO: Sample rate is determined automatically and changes due to instrument internal adjustments. You can set a minimum sample rate with ACQuire:SRATe:MINimum.
				- MANual: The sample rate is defined with ACQuire:SRATe[:VALue]."""
		response = self._core.io.query_str('ACQuire:SRATe:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.AutoManualMode)

	def set_mode(self, sample_rate_mode: enums.AutoManualMode) -> None:
		"""ACQuire:SRATe:MODE \n
		Snippet: driver.acquire.symbolRate.set_mode(sample_rate_mode = enums.AutoManualMode.AUTO) \n
		Defines how the sample rate is set. The sample rate considers the samples of the ADC, and the processing of the captured
		samples including interpolation. \n
			:param sample_rate_mode:
				- AUTO: Sample rate is determined automatically and changes due to instrument internal adjustments. You can set a minimum sample rate with ACQuire:SRATe:MINimum.
				- MANual: The sample rate is defined with ACQuire:SRATe[:VALue]."""
		param = Conversions.enum_scalar_to_str(sample_rate_mode, enums.AutoManualMode)
		self._core.io.write(f'ACQuire:SRATe:MODE {param}')

	def get_minimum(self) -> float:
		"""ACQuire:SRATe:MINimum \n
		Snippet: value: float = driver.acquire.symbolRate.get_minimum() \n
		Sets the minimum sample rate if method RsMxo.Acquire.SymbolRate.mode is set to AUTO. \n
			:return: smp_rate_usr_min: No help available
		"""
		response = self._core.io.query_str('ACQuire:SRATe:MINimum?')
		return Conversions.str_to_float(response)

	def set_minimum(self, smp_rate_usr_min: float) -> None:
		"""ACQuire:SRATe:MINimum \n
		Snippet: driver.acquire.symbolRate.set_minimum(smp_rate_usr_min = 1.0) \n
		Sets the minimum sample rate if method RsMxo.Acquire.SymbolRate.mode is set to AUTO. \n
			:param smp_rate_usr_min: No help available
		"""
		param = Conversions.decimal_value_to_str(smp_rate_usr_min)
		self._core.io.write(f'ACQuire:SRATe:MINimum {param}')
