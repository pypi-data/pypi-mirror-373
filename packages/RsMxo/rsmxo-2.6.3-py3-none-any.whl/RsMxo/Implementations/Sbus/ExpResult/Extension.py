from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ExtensionCls:
	"""Extension commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("extension", core, parent)

	def set(self, file_type: enums.ResultFileType, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:EXPResult:EXTension \n
		Snippet: driver.sbus.expResult.extension.set(file_type = enums.ResultFileType.CSV, serialBus = repcap.SerialBus.Default) \n
		Selects the file format. \n
			:param file_type: PY: Python
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(file_type, enums.ResultFileType)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:EXPResult:EXTension {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.ResultFileType:
		"""SBUS<*>:EXPResult:EXTension \n
		Snippet: value: enums.ResultFileType = driver.sbus.expResult.extension.get(serialBus = repcap.SerialBus.Default) \n
		Selects the file format. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: file_type: PY: Python"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:EXPResult:EXTension?')
		return Conversions.str_to_scalar_enum(response, enums.ResultFileType)
