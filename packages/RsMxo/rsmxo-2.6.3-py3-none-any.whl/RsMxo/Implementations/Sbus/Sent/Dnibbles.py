from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DnibblesCls:
	"""Dnibbles commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dnibbles", core, parent)

	def set(self, data_nibbles: int, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SENT:DNIBbles \n
		Snippet: driver.sbus.sent.dnibbles.set(data_nibbles = 1, serialBus = repcap.SerialBus.Default) \n
		Sets the number of data units in a single transmission sequence. \n
			:param data_nibbles: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(data_nibbles)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SENT:DNIBbles {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> int:
		"""SBUS<*>:SENT:DNIBbles \n
		Snippet: value: int = driver.sbus.sent.dnibbles.get(serialBus = repcap.SerialBus.Default) \n
		Sets the number of data units in a single transmission sequence. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: data_nibbles: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SENT:DNIBbles?')
		return Conversions.str_to_int(response)
