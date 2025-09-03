from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PointsCls:
	"""Points commands group definition. 5 total commands, 0 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("points", core, parent)

	def get_arate(self) -> float:
		"""ACQuire:POINts:ARATe \n
		Snippet: value: float = driver.acquire.points.get_arate() \n
		Returns the sample rate of the ADC, before waveform processing. The result is the interleaved sample rate or the
		non-interleaved one, depending on the channel usage. \n
			:return: adc_sample_rate: No help available
		"""
		response = self._core.io.query_str('ACQuire:POINts:ARATe?')
		return Conversions.str_to_float(response)

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.AutoManualMode:
		"""ACQuire:POINts:MODE \n
		Snippet: value: enums.AutoManualMode = driver.acquire.points.get_mode() \n
		Selects the mode of the waveform record length adjustment. The record length is the number of waveform samples that are
		stored in one waveform record after processing, including interpolation. It determines the length of the displayed
		waveform. \n
			:return: record_len_mode: No help available
		"""
		response = self._core.io.query_str('ACQuire:POINts:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.AutoManualMode)

	def set_mode(self, record_len_mode: enums.AutoManualMode) -> None:
		"""ACQuire:POINts:MODE \n
		Snippet: driver.acquire.points.set_mode(record_len_mode = enums.AutoManualMode.AUTO) \n
		Selects the mode of the waveform record length adjustment. The record length is the number of waveform samples that are
		stored in one waveform record after processing, including interpolation. It determines the length of the displayed
		waveform. \n
			:param record_len_mode:
				- AUTO: Record length is determined automatically and changes due to instrument internal adjustments.
				- MANual: The waveform record length is defined with ACQuire:POINts[:VALue]."""
		param = Conversions.enum_scalar_to_str(record_len_mode, enums.AutoManualMode)
		self._core.io.write(f'ACQuire:POINts:MODE {param}')

	def get_value(self) -> int:
		"""ACQuire:POINts[:VALue] \n
		Snippet: value: int = driver.acquire.points.get_value() \n
		Sets the record length, if method RsMxo.Acquire.Points.mode is set to MANual. \n
			:return: record_length: No help available
		"""
		response = self._core.io.query_str('ACQuire:POINts:VALue?')
		return Conversions.str_to_int(response)

	def set_value(self, record_length: int) -> None:
		"""ACQuire:POINts[:VALue] \n
		Snippet: driver.acquire.points.set_value(record_length = 1) \n
		Sets the record length, if method RsMxo.Acquire.Points.mode is set to MANual. \n
			:param record_length: No help available
		"""
		param = Conversions.decimal_value_to_str(record_length)
		self._core.io.write(f'ACQuire:POINts:VALue {param}')

	def get_dvalue(self) -> int:
		"""ACQuire:POINts:DVALue \n
		Snippet: value: int = driver.acquire.points.get_dvalue() \n
		Returns the current digital record length used by each digital channel. \n
			:return: dig_rec_len: No help available
		"""
		response = self._core.io.query_str('ACQuire:POINts:DVALue?')
		return Conversions.str_to_int(response)

	def get_maximum(self) -> int:
		"""ACQuire:POINts:MAXimum \n
		Snippet: value: int = driver.acquire.points.get_maximum() \n
		Sets the maximum record length, if method RsMxo.Acquire.Points.mode is set to AUTO. \n
			:return: record_len_user_limit: No help available
		"""
		response = self._core.io.query_str('ACQuire:POINts:MAXimum?')
		return Conversions.str_to_int(response)

	def set_maximum(self, record_len_user_limit: int) -> None:
		"""ACQuire:POINts:MAXimum \n
		Snippet: driver.acquire.points.set_maximum(record_len_user_limit = 1) \n
		Sets the maximum record length, if method RsMxo.Acquire.Points.mode is set to AUTO. \n
			:param record_len_user_limit: No help available
		"""
		param = Conversions.decimal_value_to_str(record_len_user_limit)
		self._core.io.write(f'ACQuire:POINts:MAXimum {param}')
