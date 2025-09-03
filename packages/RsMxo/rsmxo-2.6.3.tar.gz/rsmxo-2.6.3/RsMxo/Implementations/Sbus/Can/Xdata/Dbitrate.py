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

	def set(self, xl_bitrate: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:CAN:XDATa:DBITrate \n
		Snippet: driver.sbus.can.xdata.dbitrate.set(xl_bitrate = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets the bit rate of the data phase for the CAN XL frame. \n
			:param xl_bitrate: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(xl_bitrate)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:CAN:XDATa:DBITrate {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:CAN:XDATa:DBITrate \n
		Snippet: value: float = driver.sbus.can.xdata.dbitrate.get(serialBus = repcap.SerialBus.Default) \n
		Sets the bit rate of the data phase for the CAN XL frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: xl_bitrate: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:CAN:XDATa:DBITrate?')
		return Conversions.str_to_float(response)
