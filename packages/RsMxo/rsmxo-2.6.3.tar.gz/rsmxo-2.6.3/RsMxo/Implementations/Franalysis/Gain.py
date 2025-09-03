from typing import List

from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class GainCls:
	"""Gain commands group definition. 4 total commands, 0 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("gain", core, parent)

	def get_data(self) -> List[float]:
		"""FRANalysis:GAIN:DATA \n
		Snippet: value: List[float] = driver.franalysis.gain.get_data() \n
		Returns the data of the gain as a list of comma-separated values in dB. \n
			:return: data: Comma-separated list of values
		"""
		response = self._core.io.query_bin_or_ascii_float_list('FRANalysis:GAIN:DATA?')
		return response

	def get_enable(self) -> bool:
		"""FRANalysis:GAIN:ENABle \n
		Snippet: value: bool = driver.franalysis.gain.get_enable() \n
		Enables the gain waveform for the frequency response analysis. \n
			:return: state: No help available
		"""
		response = self._core.io.query_str('FRANalysis:GAIN:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, state: bool) -> None:
		"""FRANalysis:GAIN:ENABle \n
		Snippet: driver.franalysis.gain.set_enable(state = False) \n
		Enables the gain waveform for the frequency response analysis. \n
			:param state: No help available
		"""
		param = Conversions.bool_to_str(state)
		self._core.io.write(f'FRANalysis:GAIN:ENABle {param}')

	def get_offset(self) -> float:
		"""FRANalysis:GAIN:OFFSet \n
		Snippet: value: float = driver.franalysis.gain.get_offset() \n
		Sets a vertical offset of the gain waveform. \n
			:return: vertical_offset: No help available
		"""
		response = self._core.io.query_str('FRANalysis:GAIN:OFFSet?')
		return Conversions.str_to_float(response)

	def set_offset(self, vertical_offset: float) -> None:
		"""FRANalysis:GAIN:OFFSet \n
		Snippet: driver.franalysis.gain.set_offset(vertical_offset = 1.0) \n
		Sets a vertical offset of the gain waveform. \n
			:param vertical_offset: No help available
		"""
		param = Conversions.decimal_value_to_str(vertical_offset)
		self._core.io.write(f'FRANalysis:GAIN:OFFSet {param}')

	def get_scale(self) -> float:
		"""FRANalysis:GAIN:SCALe \n
		Snippet: value: float = driver.franalysis.gain.get_scale() \n
		Sets the vertical scale for the gain waveform. \n
			:return: vertical_scale: No help available
		"""
		response = self._core.io.query_str('FRANalysis:GAIN:SCALe?')
		return Conversions.str_to_float(response)

	def set_scale(self, vertical_scale: float) -> None:
		"""FRANalysis:GAIN:SCALe \n
		Snippet: driver.franalysis.gain.set_scale(vertical_scale = 1.0) \n
		Sets the vertical scale for the gain waveform. \n
			:param vertical_scale: No help available
		"""
		param = Conversions.decimal_value_to_str(vertical_scale)
		self._core.io.write(f'FRANalysis:GAIN:SCALe {param}')
