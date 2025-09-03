from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DbitrateCls:
	"""Dbitrate commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dbitrate", core, parent)

	def set(self, fd_bitrate: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:CAN:FDATa:DBITrate \n
		Snippet: driver.sbus.can.fdata.dbitrate.set(fd_bitrate = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets the bit rate of the data phase. \n
			:param fd_bitrate: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(fd_bitrate)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:CAN:FDATa:DBITrate {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:CAN:FDATa:DBITrate \n
		Snippet: value: float = driver.sbus.can.fdata.dbitrate.get(serialBus = repcap.SerialBus.Default) \n
		Sets the bit rate of the data phase. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: fd_bitrate: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:CAN:FDATa:DBITrate?')
		return Conversions.str_to_float(response)
