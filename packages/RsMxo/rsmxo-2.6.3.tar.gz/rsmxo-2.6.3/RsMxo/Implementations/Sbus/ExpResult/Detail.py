from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DetailCls:
	"""Detail commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("detail", core, parent)

	def set(self, include_details: bool, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:EXPResult:DETail \n
		Snippet: driver.sbus.expResult.detail.set(include_details = False, serialBus = repcap.SerialBus.Default) \n
		If enabled, includes the detailed results for all frames in the export result file. \n
			:param include_details: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.bool_to_str(include_details)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:EXPResult:DETail {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> bool:
		"""SBUS<*>:EXPResult:DETail \n
		Snippet: value: bool = driver.sbus.expResult.detail.get(serialBus = repcap.SerialBus.Default) \n
		If enabled, includes the detailed results for all frames in the export result file. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: include_details: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:EXPResult:DETail?')
		return Conversions.str_to_bool(response)
