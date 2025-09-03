from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Types import DataType
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ErEnableCls:
	"""ErEnable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("erEnable", core, parent)

	def set(self, error_name: str, enabler: bool, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:RFFE:FILTer:ERENable \n
		Snippet: driver.sbus.rffe.filterPy.erEnable.set(error_name = 'abc', enabler = False, serialBus = repcap.SerialBus.Default) \n
		Defines the error type to be filtered on. \n
			:param error_name: No help available
			:param enabler: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('error_name', error_name, DataType.String), ArgSingle('enabler', enabler, DataType.Boolean))
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:RFFE:FILTer:ERENable {param}'.rstrip())

	def get(self, serialBus=repcap.SerialBus.Default) -> bool:
		"""SBUS<*>:RFFE:FILTer:ERENable \n
		Snippet: value: bool = driver.sbus.rffe.filterPy.erEnable.get(serialBus = repcap.SerialBus.Default) \n
		Defines the error type to be filtered on. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: enabler: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:RFFE:FILTer:ERENable?')
		return Conversions.str_to_bool(response)
