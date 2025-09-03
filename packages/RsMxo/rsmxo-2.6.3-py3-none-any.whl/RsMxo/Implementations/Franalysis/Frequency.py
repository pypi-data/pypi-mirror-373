from typing import List

from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrequencyCls:
	"""Frequency commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("frequency", core, parent)

	def get_data(self) -> List[float]:
		"""FRANalysis:FREQuency:DATA \n
		Snippet: value: List[float] = driver.franalysis.frequency.get_data() \n
		Returns the data of the frequency points for which gain and phase have been calculated as a list of comma-separated
		values in Hz. \n
			:return: data: Comma-separated list of values
		"""
		response = self._core.io.query_bin_or_ascii_float_list('FRANalysis:FREQuency:DATA?')
		return response

	def get_start(self) -> float:
		"""FRANalysis:FREQuency:STARt \n
		Snippet: value: float = driver.franalysis.frequency.get_start() \n
		Sets the start frequency of the sweep. \n
			:return: start_frequency: No help available
		"""
		response = self._core.io.query_str('FRANalysis:FREQuency:STARt?')
		return Conversions.str_to_float(response)

	def set_start(self, start_frequency: float) -> None:
		"""FRANalysis:FREQuency:STARt \n
		Snippet: driver.franalysis.frequency.set_start(start_frequency = 1.0) \n
		Sets the start frequency of the sweep. \n
			:param start_frequency: No help available
		"""
		param = Conversions.decimal_value_to_str(start_frequency)
		self._core.io.write(f'FRANalysis:FREQuency:STARt {param}')

	def get_stop(self) -> float:
		"""FRANalysis:FREQuency:STOP \n
		Snippet: value: float = driver.franalysis.frequency.get_stop() \n
		Sets the stop frequency of the sweep. \n
			:return: stop_frequency: No help available
		"""
		response = self._core.io.query_str('FRANalysis:FREQuency:STOP?')
		return Conversions.str_to_float(response)

	def set_stop(self, stop_frequency: float) -> None:
		"""FRANalysis:FREQuency:STOP \n
		Snippet: driver.franalysis.frequency.set_stop(stop_frequency = 1.0) \n
		Sets the stop frequency of the sweep. \n
			:param stop_frequency: No help available
		"""
		param = Conversions.decimal_value_to_str(stop_frequency)
		self._core.io.write(f'FRANalysis:FREQuency:STOP {param}')
