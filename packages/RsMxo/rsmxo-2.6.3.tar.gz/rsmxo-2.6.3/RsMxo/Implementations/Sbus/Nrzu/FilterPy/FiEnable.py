from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Types import DataType
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FiEnableCls:
	"""FiEnable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fiEnable", core, parent)

	def set(self, frame: str, field: str, enabler: bool, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:NRZU:FILTer:FIENable \n
		Snippet: driver.sbus.nrzu.filterPy.fiEnable.set(frame = 'abc', field = 'abc', enabler = False, serialBus = repcap.SerialBus.Default) \n
		Enables or disables the checking condition for the selected field of the selected frame. \n
			:param frame: No help available
			:param field: No help available
			:param enabler: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('frame', frame, DataType.String), ArgSingle('field', field, DataType.String), ArgSingle('enabler', enabler, DataType.Boolean))
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:NRZU:FILTer:FIENable {param}'.rstrip())

	def get(self, serialBus=repcap.SerialBus.Default) -> bool:
		"""SBUS<*>:NRZU:FILTer:FIENable \n
		Snippet: value: bool = driver.sbus.nrzu.filterPy.fiEnable.get(serialBus = repcap.SerialBus.Default) \n
		Enables or disables the checking condition for the selected field of the selected frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: enabler: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:NRZU:FILTer:FIENable?')
		return Conversions.str_to_bool(response)
