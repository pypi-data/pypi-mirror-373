from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ......Internal.Utilities import trim_str_response
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NameCls:
	"""Name commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("name", core, parent)

	def set(self, name: str, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> None:
		"""SBUS<*>:NRZU:FORMat:FRAMe<*>:NAME \n
		Snippet: driver.sbus.nrzu.formatPy.frame.name.set(name = 'abc', serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Specifies the name for the frame description of the selected frame. \n
			:param name: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
		"""
		param = Conversions.value_to_quoted_str(name)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:NRZU:FORMat:FRAMe{frame_cmd_val}:NAME {param}')

	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> str:
		"""SBUS<*>:NRZU:FORMat:FRAMe<*>:NAME \n
		Snippet: value: str = driver.sbus.nrzu.formatPy.frame.name.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Specifies the name for the frame description of the selected frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: name: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:NRZU:FORMat:FRAMe{frame_cmd_val}:NAME?')
		return trim_str_response(response)
