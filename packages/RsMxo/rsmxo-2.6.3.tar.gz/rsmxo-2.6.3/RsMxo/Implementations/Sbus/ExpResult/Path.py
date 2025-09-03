from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PathCls:
	"""Path commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("path", core, parent)

	def set(self, path: str, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:EXPResult:PATH \n
		Snippet: driver.sbus.expResult.path.set(path = 'abc', serialBus = repcap.SerialBus.Default) \n
		Sets the path where the protocol export files are stored.
		On the instrument, the default path is /home/storage/userData/Protocol. You can create subfolders in this folder. \n
			:param path: String parameter
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.value_to_quoted_str(path)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:EXPResult:PATH {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> str:
		"""SBUS<*>:EXPResult:PATH \n
		Snippet: value: str = driver.sbus.expResult.path.get(serialBus = repcap.SerialBus.Default) \n
		Sets the path where the protocol export files are stored.
		On the instrument, the default path is /home/storage/userData/Protocol. You can create subfolders in this folder. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: path: String parameter"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:EXPResult:PATH?')
		return trim_str_response(response)
