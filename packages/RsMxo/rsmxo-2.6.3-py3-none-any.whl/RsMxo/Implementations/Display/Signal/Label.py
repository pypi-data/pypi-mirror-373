from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Types import DataType
from ....Internal.Utilities import trim_str_response
from ....Internal.ArgSingleList import ArgSingleList
from ....Internal.ArgSingle import ArgSingle
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LabelCls:
	"""Label commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("label", core, parent)

	def set(self, analog_channels: enums.AnalogChannels, name: str) -> None:
		"""DISPlay:SIGNal:LABel \n
		Snippet: driver.display.signal.label.set(analog_channels = enums.AnalogChannels.C1, name = 'abc') \n
		Defines and assigns a label to the specified channel waveform. \n
			:param analog_channels: No help available
			:param name: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('analog_channels', analog_channels, DataType.Enum, enums.AnalogChannels), ArgSingle('name', name, DataType.String))
		self._core.io.write(f'DISPlay:SIGNal:LABel {param}'.rstrip())

	def get(self, analog_channels: enums.AnalogChannels) -> str:
		"""DISPlay:SIGNal:LABel \n
		Snippet: value: str = driver.display.signal.label.get(analog_channels = enums.AnalogChannels.C1) \n
		Defines and assigns a label to the specified channel waveform. \n
			:param analog_channels: No help available
			:return: name: No help available"""
		param = Conversions.enum_scalar_to_str(analog_channels, enums.AnalogChannels)
		response = self._core.io.query_str(f'DISPlay:SIGNal:LABel? {param}')
		return trim_str_response(response)
