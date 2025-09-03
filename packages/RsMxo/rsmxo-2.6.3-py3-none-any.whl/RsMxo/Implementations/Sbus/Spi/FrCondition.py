from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrConditionCls:
	"""FrCondition commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("frCondition", core, parent)

	def set(self, frame_condition: enums.SbusFrameCondition, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SPI:FRCondition \n
		Snippet: driver.sbus.spi.frCondition.set(frame_condition = enums.SbusFrameCondition.CLKTimeout, serialBus = repcap.SerialBus.Default) \n
		No command help available \n
			:param frame_condition: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(frame_condition, enums.SbusFrameCondition)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SPI:FRCondition {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SbusFrameCondition:
		"""SBUS<*>:SPI:FRCondition \n
		Snippet: value: enums.SbusFrameCondition = driver.sbus.spi.frCondition.get(serialBus = repcap.SerialBus.Default) \n
		No command help available \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: frame_condition: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SPI:FRCondition?')
		return Conversions.str_to_scalar_enum(response, enums.SbusFrameCondition)
