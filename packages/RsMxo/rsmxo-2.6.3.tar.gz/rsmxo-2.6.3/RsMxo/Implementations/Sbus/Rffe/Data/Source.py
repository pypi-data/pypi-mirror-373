from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SourceCls:
	"""Source commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("source", core, parent)

	def set(self, source_data: enums.Source, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:RFFE:DATA:SOURce \n
		Snippet: driver.sbus.rffe.data.source.set(source_data = enums.Source.C1, serialBus = repcap.SerialBus.Default) \n
		Sets the source of the data line. \n
			:param source_data: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(source_data, enums.Source)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:RFFE:DATA:SOURce {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.Source:
		"""SBUS<*>:RFFE:DATA:SOURce \n
		Snippet: value: enums.Source = driver.sbus.rffe.data.source.get(serialBus = repcap.SerialBus.Default) \n
		Sets the source of the data line. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: source_data: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:RFFE:DATA:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.Source)
