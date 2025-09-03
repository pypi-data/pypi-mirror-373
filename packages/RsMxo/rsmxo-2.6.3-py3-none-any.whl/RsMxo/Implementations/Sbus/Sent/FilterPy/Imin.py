from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Types import DataType
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class IminCls:
	"""Imin commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("imin", core, parent)

	def set(self, frame: str, field: str, data: int, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SENT:FILTer:IMIN \n
		Snippet: driver.sbus.sent.filterPy.imin.set(frame = 'abc', field = 'abc', data = 1, serialBus = repcap.SerialBus.Default) \n
		Specifies the index, or sets the start value of an index range. \n
			:param frame: No help available
			:param field: No help available
			:param data: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('frame', frame, DataType.String), ArgSingle('field', field, DataType.String), ArgSingle('data', data, DataType.Integer))
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SENT:FILTer:IMIN {param}'.rstrip())

	def get(self, serialBus=repcap.SerialBus.Default) -> int:
		"""SBUS<*>:SENT:FILTer:IMIN \n
		Snippet: value: int = driver.sbus.sent.filterPy.imin.get(serialBus = repcap.SerialBus.Default) \n
		Specifies the index, or sets the start value of an index range. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: data: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SENT:FILTer:IMIN?')
		return Conversions.str_to_int(response)
