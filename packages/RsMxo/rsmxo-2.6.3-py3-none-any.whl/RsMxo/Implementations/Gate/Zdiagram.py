from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.Types import DataType
from ...Internal.StructBase import StructBase
from ...Internal.ArgStruct import ArgStruct
from ...Internal.ArgSingleList import ArgSingleList
from ...Internal.ArgSingle import ArgSingle
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ZdiagramCls:
	"""Zdiagram commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("zdiagram", core, parent)

	def set(self, signal_source: int, signal_source_2: int = None, gate=repcap.Gate.Default) -> None:
		"""GATE<*>:ZDIagram \n
		Snippet: driver.gate.zdiagram.set(signal_source = 1, signal_source_2 = 1, gate = repcap.Gate.Default) \n
		Available for method RsMxo.Gate.Gcoupling.set = ZOOM. The gate area is defined identically to the zoom area for the
		selected zoom diagram. \n
			:param signal_source: No help available
			:param signal_source_2: No help available
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('signal_source', signal_source, DataType.Integer), ArgSingle('signal_source_2', signal_source_2, DataType.Integer, None, is_optional=True))
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		self._core.io.write(f'GATE{gate_cmd_val}:ZDIagram {param}'.rstrip())

	# noinspection PyTypeChecker
	class ZdiagramStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Signal_Source: int: No parameter help available
			- 2 Signal_Source_2: int: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_int('Signal_Source'),
			ArgStruct.scalar_int('Signal_Source_2')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Signal_Source: int = None
			self.Signal_Source_2: int = None

	def get(self, gate=repcap.Gate.Default) -> ZdiagramStruct:
		"""GATE<*>:ZDIagram \n
		Snippet: value: ZdiagramStruct = driver.gate.zdiagram.get(gate = repcap.Gate.Default) \n
		Available for method RsMxo.Gate.Gcoupling.set = ZOOM. The gate area is defined identically to the zoom area for the
		selected zoom diagram. \n
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')
			:return: structure: for return value, see the help for ZdiagramStruct structure arguments."""
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		return self._core.io.query_struct(f'GATE{gate_cmd_val}:ZDIagram?', self.__class__.ZdiagramStruct())
