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

	def set(self, cs_source: enums.Source, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SPI:CSELect:SOURce \n
		Snippet: driver.sbus.spi.cselect.source.set(cs_source = enums.Source.C1, serialBus = repcap.SerialBus.Default) \n
		Sets the input channel of the CS line. \n
			:param cs_source: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(cs_source, enums.Source)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SPI:CSELect:SOURce {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.Source:
		"""SBUS<*>:SPI:CSELect:SOURce \n
		Snippet: value: enums.Source = driver.sbus.spi.cselect.source.get(serialBus = repcap.SerialBus.Default) \n
		Sets the input channel of the CS line. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: cs_source: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SPI:CSELect:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.Source)
