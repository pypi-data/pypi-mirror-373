from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.Types import DataType
from .....Internal.Utilities import trim_str_response
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DminCls:
	"""Dmin commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dmin", core, parent)

	def set(self, frame: str, field: str, data: str, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:ARINc:FILTer:DMIN \n
		Snippet: driver.sbus.arinc.filterPy.dmin.set(frame = 'abc', field = 'abc', data = 'abc', serialBus = repcap.SerialBus.Default) \n
		Specifies the data pattern, or sets the start value of a data pattern range. \n
			:param frame: No help available
			:param field: No help available
			:param data: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('frame', frame, DataType.String), ArgSingle('field', field, DataType.String), ArgSingle('data', data, DataType.String))
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:ARINc:FILTer:DMIN {param}'.rstrip())

	def get(self, serialBus=repcap.SerialBus.Default) -> str:
		"""SBUS<*>:ARINc:FILTer:DMIN \n
		Snippet: value: str = driver.sbus.arinc.filterPy.dmin.get(serialBus = repcap.SerialBus.Default) \n
		Specifies the data pattern, or sets the start value of a data pattern range. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: data: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:ARINc:FILTer:DMIN?')
		return trim_str_response(response)
