from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PositionCls:
	"""Position commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("position", core, parent)

	def set(self, honeycomb_posi: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SWIRe:POSition \n
		Snippet: driver.sbus.swire.position.set(honeycomb_posi = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets the vertical position of the SpaceWire signal. \n
			:param honeycomb_posi: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(honeycomb_posi)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SWIRe:POSition {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:SWIRe:POSition \n
		Snippet: value: float = driver.sbus.swire.position.get(serialBus = repcap.SerialBus.Default) \n
		Sets the vertical position of the SpaceWire signal. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: honeycomb_posi: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SWIRe:POSition?')
		return Conversions.str_to_float(response)
