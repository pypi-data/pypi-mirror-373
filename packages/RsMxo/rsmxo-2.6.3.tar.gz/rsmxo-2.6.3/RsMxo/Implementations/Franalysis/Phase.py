from typing import List

from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PhaseCls:
	"""Phase commands group definition. 5 total commands, 0 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("phase", core, parent)

	def get_data(self) -> List[float]:
		"""FRANalysis:PHASe:DATA \n
		Snippet: value: List[float] = driver.franalysis.phase.get_data() \n
		Returns the data of the phase as a list of comma-separated values in degree. \n
			:return: data: Comma-separated list of values
		"""
		response = self._core.io.query_bin_or_ascii_float_list('FRANalysis:PHASe:DATA?')
		return response

	def get_enable(self) -> bool:
		"""FRANalysis:PHASe:ENABle \n
		Snippet: value: bool = driver.franalysis.phase.get_enable() \n
		Enables the phase waveform for the frequency response analysis. \n
			:return: state: No help available
		"""
		response = self._core.io.query_str('FRANalysis:PHASe:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, state: bool) -> None:
		"""FRANalysis:PHASe:ENABle \n
		Snippet: driver.franalysis.phase.set_enable(state = False) \n
		Enables the phase waveform for the frequency response analysis. \n
			:param state: No help available
		"""
		param = Conversions.bool_to_str(state)
		self._core.io.write(f'FRANalysis:PHASe:ENABle {param}')

	def get_maximum(self) -> float:
		"""FRANalysis:PHASe:MAXimum \n
		Snippet: value: float = driver.franalysis.phase.get_maximum() \n
		Sets the upper boundary of the vertical phase window. The lower boundary is given by Maximum phase - 360°. By default,
		the Maximum phase is set to 180° for a phase window ranging from -180° to 180° accordingly. \n
			:return: max_phase: No help available
		"""
		response = self._core.io.query_str('FRANalysis:PHASe:MAXimum?')
		return Conversions.str_to_float(response)

	def set_maximum(self, max_phase: float) -> None:
		"""FRANalysis:PHASe:MAXimum \n
		Snippet: driver.franalysis.phase.set_maximum(max_phase = 1.0) \n
		Sets the upper boundary of the vertical phase window. The lower boundary is given by Maximum phase - 360°. By default,
		the Maximum phase is set to 180° for a phase window ranging from -180° to 180° accordingly. \n
			:param max_phase: No help available
		"""
		param = Conversions.decimal_value_to_str(max_phase)
		self._core.io.write(f'FRANalysis:PHASe:MAXimum {param}')

	def get_offset(self) -> float:
		"""FRANalysis:PHASe:OFFSet \n
		Snippet: value: float = driver.franalysis.phase.get_offset() \n
		Sets a vertical offset of the phase waveform. \n
			:return: vertical_offset: No help available
		"""
		response = self._core.io.query_str('FRANalysis:PHASe:OFFSet?')
		return Conversions.str_to_float(response)

	def set_offset(self, vertical_offset: float) -> None:
		"""FRANalysis:PHASe:OFFSet \n
		Snippet: driver.franalysis.phase.set_offset(vertical_offset = 1.0) \n
		Sets a vertical offset of the phase waveform. \n
			:param vertical_offset: No help available
		"""
		param = Conversions.decimal_value_to_str(vertical_offset)
		self._core.io.write(f'FRANalysis:PHASe:OFFSet {param}')

	def get_scale(self) -> float:
		"""FRANalysis:PHASe:SCALe \n
		Snippet: value: float = driver.franalysis.phase.get_scale() \n
		Sets the vertical scale for the phase waveform. \n
			:return: vertical_scale: No help available
		"""
		response = self._core.io.query_str('FRANalysis:PHASe:SCALe?')
		return Conversions.str_to_float(response)

	def set_scale(self, vertical_scale: float) -> None:
		"""FRANalysis:PHASe:SCALe \n
		Snippet: driver.franalysis.phase.set_scale(vertical_scale = 1.0) \n
		Sets the vertical scale for the phase waveform. \n
			:param vertical_scale: No help available
		"""
		param = Conversions.decimal_value_to_str(vertical_scale)
		self._core.io.write(f'FRANalysis:PHASe:SCALe {param}')
