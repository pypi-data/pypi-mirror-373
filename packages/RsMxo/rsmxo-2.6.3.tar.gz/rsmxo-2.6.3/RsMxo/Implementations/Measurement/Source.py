from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.Types import DataType
from ...Internal.ArgSingleList import ArgSingleList
from ...Internal.ArgSingle import ArgSingle
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SourceCls:
	"""Source commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("source", core, parent)

	def set(self, signal_source: enums.SignalSource, signal_source_2: enums.SignalSource = None, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<mg>:SOURce \n
		Snippet: driver.measurement.source.set(signal_source = enums.SignalSource.C1, signal_source_2 = enums.SignalSource.C1, measIndex = repcap.MeasIndex.Default) \n
		Sets the source of the measurement. \n
			:param signal_source: No help available
			:param signal_source_2: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('signal_source', signal_source, DataType.Enum, enums.SignalSource), ArgSingle('signal_source_2', signal_source_2, DataType.Enum, enums.SignalSource, is_optional=True))
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:SOURce {param}'.rstrip())
