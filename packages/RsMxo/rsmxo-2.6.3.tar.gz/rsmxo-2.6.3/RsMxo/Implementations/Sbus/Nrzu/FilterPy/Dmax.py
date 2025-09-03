from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.Types import DataType
from .....Internal.Utilities import trim_str_response
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DmaxCls:
	"""Dmax commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dmax", core, parent)

	def set(self, frame: str, field: str, data: str, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:NRZU:FILTer:DMAX \n
		Snippet: driver.sbus.nrzu.filterPy.dmax.set(frame = 'abc', field = 'abc', data = 'abc', serialBus = repcap.SerialBus.Default) \n
		Sets the end value of a data pattern range if the operator is set to INRange or OORANGe. You can set the operator with
		method RsMxo.Sbus.Nrzu.FilterPy.Frame.Fld.Doperator.set. \n
			:param frame: No help available
			:param field: No help available
			:param data: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('frame', frame, DataType.String), ArgSingle('field', field, DataType.String), ArgSingle('data', data, DataType.String))
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:NRZU:FILTer:DMAX {param}'.rstrip())

	def get(self, serialBus=repcap.SerialBus.Default) -> str:
		"""SBUS<*>:NRZU:FILTer:DMAX \n
		Snippet: value: str = driver.sbus.nrzu.filterPy.dmax.get(serialBus = repcap.SerialBus.Default) \n
		Sets the end value of a data pattern range if the operator is set to INRange or OORANGe. You can set the operator with
		method RsMxo.Sbus.Nrzu.FilterPy.Frame.Fld.Doperator.set. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: data: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:NRZU:FILTer:DMAX?')
		return trim_str_response(response)
