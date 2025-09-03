from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PhaseCls:
	"""Phase commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("phase", core, parent)

	def get_frequency(self) -> float:
		"""FRANalysis:MARGin:PHASe:FREQuency \n
		Snippet: value: float = driver.franalysis.margin.phase.get_frequency() \n
		Returns the frequency of the phase margin. \n
			:return: frequency: No help available
		"""
		response = self._core.io.query_str('FRANalysis:MARGin:PHASe:FREQuency?')
		return Conversions.str_to_float(response)

	def get_value(self) -> float:
		"""FRANalysis:MARGin:PHASe:VALue \n
		Snippet: value: float = driver.franalysis.margin.phase.get_value() \n
		Returns the value of the phase margin. \n
			:return: phase: No help available
		"""
		response = self._core.io.query_str('FRANalysis:MARGin:PHASe:VALue?')
		return Conversions.str_to_float(response)
