from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Types import DataType
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BitCls:
	"""Bit commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("bit", core, parent)

	def set(self, frame: str, field: str, bit: enums.SbusBitState, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:RFFE:FILTer:BIT \n
		Snippet: driver.sbus.rffe.filterPy.bit.set(frame = 'abc', field = 'abc', bit = enums.SbusBitState.DC, serialBus = repcap.SerialBus.Default) \n
		Sets the operator for the data pattern in the selected field of the selected frame. \n
			:param frame: No help available
			:param field: No help available
			:param bit: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('frame', frame, DataType.String), ArgSingle('field', field, DataType.String), ArgSingle('bit', bit, DataType.Enum, enums.SbusBitState))
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:RFFE:FILTer:BIT {param}'.rstrip())

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SbusBitState:
		"""SBUS<*>:RFFE:FILTer:BIT \n
		Snippet: value: enums.SbusBitState = driver.sbus.rffe.filterPy.bit.get(serialBus = repcap.SerialBus.Default) \n
		Sets the operator for the data pattern in the selected field of the selected frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: bit: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:RFFE:FILTer:BIT?')
		return Conversions.str_to_scalar_enum(response, enums.SbusBitState)
