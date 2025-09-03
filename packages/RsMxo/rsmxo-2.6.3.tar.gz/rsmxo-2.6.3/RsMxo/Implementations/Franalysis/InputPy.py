from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class InputPyCls:
	"""InputPy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("inputPy", core, parent)

	# noinspection PyTypeChecker
	def get_source(self) -> enums.AnalogChannels:
		"""FRANalysis:INPut[:SOURce] \n
		Snippet: value: enums.AnalogChannels = driver.franalysis.inputPy.get_source() \n
		Sets the channel for the input signal of the DUT. \n
			:return: input_channel: No help available
		"""
		response = self._core.io.query_str('FRANalysis:INPut:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.AnalogChannels)

	def set_source(self, input_channel: enums.AnalogChannels) -> None:
		"""FRANalysis:INPut[:SOURce] \n
		Snippet: driver.franalysis.inputPy.set_source(input_channel = enums.AnalogChannels.C1) \n
		Sets the channel for the input signal of the DUT. \n
			:param input_channel: No help available
		"""
		param = Conversions.enum_scalar_to_str(input_channel, enums.AnalogChannels)
		self._core.io.write(f'FRANalysis:INPut:SOURce {param}')
