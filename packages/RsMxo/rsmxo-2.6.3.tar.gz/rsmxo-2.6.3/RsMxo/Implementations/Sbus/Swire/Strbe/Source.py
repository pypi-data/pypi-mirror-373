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

	def set(self, strobe_source: enums.Source, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SWIRe:STRBe:SOURce \n
		Snippet: driver.sbus.swire.strbe.source.set(strobe_source = enums.Source.C1, serialBus = repcap.SerialBus.Default) \n
		Selects the source for the strobe signal. \n
			:param strobe_source: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(strobe_source, enums.Source)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SWIRe:STRBe:SOURce {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.Source:
		"""SBUS<*>:SWIRe:STRBe:SOURce \n
		Snippet: value: enums.Source = driver.sbus.swire.strbe.source.get(serialBus = repcap.SerialBus.Default) \n
		Selects the source for the strobe signal. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: strobe_source: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SWIRe:STRBe:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.Source)
