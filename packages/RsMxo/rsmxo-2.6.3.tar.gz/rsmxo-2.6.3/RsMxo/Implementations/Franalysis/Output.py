from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OutputCls:
	"""Output commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("output", core, parent)

	# noinspection PyTypeChecker
	def get_source(self) -> enums.AnalogChannels:
		"""FRANalysis:OUTPut[:SOURce] \n
		Snippet: value: enums.AnalogChannels = driver.franalysis.output.get_source() \n
		Sets the channel for the output signal of the DUT. \n
			:return: output_channel: No help available
		"""
		response = self._core.io.query_str('FRANalysis:OUTPut:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.AnalogChannels)

	def set_source(self, output_channel: enums.AnalogChannels) -> None:
		"""FRANalysis:OUTPut[:SOURce] \n
		Snippet: driver.franalysis.output.set_source(output_channel = enums.AnalogChannels.C1) \n
		Sets the channel for the output signal of the DUT. \n
			:param output_channel: No help available
		"""
		param = Conversions.enum_scalar_to_str(output_channel, enums.AnalogChannels)
		self._core.io.write(f'FRANalysis:OUTPut:SOURce {param}')
