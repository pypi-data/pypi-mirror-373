from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class F2NameCls:
	"""F2Name commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("f2Name", core, parent)

	def set(self, frame_2_name: str, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:PROTocol:F2Name \n
		Snippet: driver.measurement.protocol.f2Name.set(frame_2_name = 'abc', measIndex = repcap.MeasIndex.Default) \n
		Sets or queries the name of the frame or the frame type, at which the oscilloscope ends the measurement in a From - To
		condition. \n
			:param frame_2_name: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.value_to_quoted_str(frame_2_name)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:PROTocol:F2Name {param}')

	def get(self, measIndex=repcap.MeasIndex.Default) -> str:
		"""MEASurement<*>:PROTocol:F2Name \n
		Snippet: value: str = driver.measurement.protocol.f2Name.get(measIndex = repcap.MeasIndex.Default) \n
		Sets or queries the name of the frame or the frame type, at which the oscilloscope ends the measurement in a From - To
		condition. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: frame_2_name: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:PROTocol:F2Name?')
		return trim_str_response(response)
