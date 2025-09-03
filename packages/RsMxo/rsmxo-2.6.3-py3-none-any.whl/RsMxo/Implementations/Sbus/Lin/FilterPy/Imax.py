from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Types import DataType
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ImaxCls:
	"""Imax commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("imax", core, parent)

	def set(self, frame: str, field: str, data: int, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:LIN:FILTer:IMAX \n
		Snippet: driver.sbus.lin.filterPy.imax.set(frame = 'abc', field = 'abc', data = 1, serialBus = repcap.SerialBus.Default) \n
		Sets the end value of an index range if the operator is set to INRange. \n
			:param frame: No help available
			:param field: No help available
			:param data: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('frame', frame, DataType.String), ArgSingle('field', field, DataType.String), ArgSingle('data', data, DataType.Integer))
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:LIN:FILTer:IMAX {param}'.rstrip())

	def get(self, serialBus=repcap.SerialBus.Default) -> int:
		"""SBUS<*>:LIN:FILTer:IMAX \n
		Snippet: value: int = driver.sbus.lin.filterPy.imax.get(serialBus = repcap.SerialBus.Default) \n
		Sets the end value of an index range if the operator is set to INRange. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: data: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:LIN:FILTer:IMAX?')
		return Conversions.str_to_int(response)
