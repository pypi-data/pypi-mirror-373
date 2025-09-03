from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FnameCls:
	"""Fname commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fname", core, parent)

	def set(self, frame_name: str, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:PROTocol:FNAMe \n
		Snippet: driver.measurement.protocol.fname.set(frame_name = 'abc', measIndex = repcap.MeasIndex.Default) \n
		Sets or queries the name of the frame or the frame type, at which the oscilloscope executes or starts the measurement. \n
			:param frame_name: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.value_to_quoted_str(frame_name)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:PROTocol:FNAMe {param}')

	def get(self, measIndex=repcap.MeasIndex.Default) -> str:
		"""MEASurement<*>:PROTocol:FNAMe \n
		Snippet: value: str = driver.measurement.protocol.fname.get(measIndex = repcap.MeasIndex.Default) \n
		Sets or queries the name of the frame or the frame type, at which the oscilloscope executes or starts the measurement. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: frame_name: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:PROTocol:FNAMe?')
		return trim_str_response(response)
