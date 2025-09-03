from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SformatCls:
	"""Sformat commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sformat", core, parent)

	def set(self, serial_messages: enums.SbusSentSerialMessages, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SENT:SFORmat \n
		Snippet: driver.sbus.sent.sformat.set(serial_messages = enums.SbusSentSerialMessages.DISabled, serialBus = repcap.SerialBus.Default) \n
		Selects if serial messages are enabled or disabled. \n
			:param serial_messages: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(serial_messages, enums.SbusSentSerialMessages)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SENT:SFORmat {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SbusSentSerialMessages:
		"""SBUS<*>:SENT:SFORmat \n
		Snippet: value: enums.SbusSentSerialMessages = driver.sbus.sent.sformat.get(serialBus = repcap.SerialBus.Default) \n
		Selects if serial messages are enabled or disabled. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: serial_messages: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SENT:SFORmat?')
		return Conversions.str_to_scalar_enum(response, enums.SbusSentSerialMessages)
