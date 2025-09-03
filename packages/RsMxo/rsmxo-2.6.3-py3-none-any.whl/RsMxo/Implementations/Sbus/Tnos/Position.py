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

	def set(self, tenbto_position: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:TNOS:POSition \n
		Snippet: driver.sbus.tnos.position.set(tenbto_position = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets the vertical position of the 10BASE-T1S signal. \n
			:param tenbto_position: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(tenbto_position)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:TNOS:POSition {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:TNOS:POSition \n
		Snippet: value: float = driver.sbus.tnos.position.get(serialBus = repcap.SerialBus.Default) \n
		Sets the vertical position of the 10BASE-T1S signal. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: tenbto_position: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:TNOS:POSition?')
		return Conversions.str_to_float(response)
