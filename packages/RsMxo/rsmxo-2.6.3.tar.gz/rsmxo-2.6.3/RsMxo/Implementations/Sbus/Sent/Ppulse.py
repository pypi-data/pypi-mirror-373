from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PpulseCls:
	"""Ppulse commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ppulse", core, parent)

	def set(self, pause_pulse: enums.SbusSentPausePulse, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SENT:PPULse \n
		Snippet: driver.sbus.sent.ppulse.set(pause_pulse = enums.SbusSentPausePulse.NPP, serialBus = repcap.SerialBus.Default) \n
		Determines whether a pause pulse is transmitted after the checksum nibble. \n
			:param pause_pulse: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(pause_pulse, enums.SbusSentPausePulse)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SENT:PPULse {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SbusSentPausePulse:
		"""SBUS<*>:SENT:PPULse \n
		Snippet: value: enums.SbusSentPausePulse = driver.sbus.sent.ppulse.get(serialBus = repcap.SerialBus.Default) \n
		Determines whether a pause pulse is transmitted after the checksum nibble. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: pause_pulse: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SENT:PPULse?')
		return Conversions.str_to_scalar_enum(response, enums.SbusSentPausePulse)
