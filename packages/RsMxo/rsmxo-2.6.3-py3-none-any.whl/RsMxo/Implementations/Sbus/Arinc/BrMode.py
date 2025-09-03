from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BrModeCls:
	"""BrMode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("brMode", core, parent)

	def set(self, bitrate_mode: enums.LowHigh, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:ARINc:BRMode \n
		Snippet: driver.sbus.arinc.brMode.set(bitrate_mode = enums.LowHigh.HIGH, serialBus = repcap.SerialBus.Default) \n
		Sets the bit rate mode to high or low speed. You can set an exact bitrate value with method RsMxo.Sbus.Arinc.BrValue.set. \n
			:param bitrate_mode: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(bitrate_mode, enums.LowHigh)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:ARINc:BRMode {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.LowHigh:
		"""SBUS<*>:ARINc:BRMode \n
		Snippet: value: enums.LowHigh = driver.sbus.arinc.brMode.get(serialBus = repcap.SerialBus.Default) \n
		Sets the bit rate mode to high or low speed. You can set an exact bitrate value with method RsMxo.Sbus.Arinc.BrValue.set. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: bitrate_mode: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:ARINc:BRMode?')
		return Conversions.str_to_scalar_enum(response, enums.LowHigh)
