from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class GainCls:
	"""Gain commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("gain", core, parent)

	def get_frequency(self) -> float:
		"""FRANalysis:MARGin:GAIN:FREQuency \n
		Snippet: value: float = driver.franalysis.margin.gain.get_frequency() \n
		Returns the frequency of the gain margin. \n
			:return: frequency: No help available
		"""
		response = self._core.io.query_str('FRANalysis:MARGin:GAIN:FREQuency?')
		return Conversions.str_to_float(response)

	def get_value(self) -> float:
		"""FRANalysis:MARGin:GAIN:VALue \n
		Snippet: value: float = driver.franalysis.margin.gain.get_value() \n
		Returns the value of the gain margin. \n
			:return: phase: No help available
		"""
		response = self._core.io.query_str('FRANalysis:MARGin:GAIN:VALue?')
		return Conversions.str_to_float(response)
