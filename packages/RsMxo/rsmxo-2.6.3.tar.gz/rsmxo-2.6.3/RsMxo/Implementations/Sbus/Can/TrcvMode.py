from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TrcvModeCls:
	"""TrcvMode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("trcvMode", core, parent)

	def set(self, transceiver_md: enums.SbusCanTransceiverMode, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:CAN:TRCVmode \n
		Snippet: driver.sbus.can.trcvMode.set(transceiver_md = enums.SbusCanTransceiverMode.FAST, serialBus = repcap.SerialBus.Default) \n
		Selects the transceiver mode for the CAN decoding. \n
			:param transceiver_md: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(transceiver_md, enums.SbusCanTransceiverMode)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:CAN:TRCVmode {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SbusCanTransceiverMode:
		"""SBUS<*>:CAN:TRCVmode \n
		Snippet: value: enums.SbusCanTransceiverMode = driver.sbus.can.trcvMode.get(serialBus = repcap.SerialBus.Default) \n
		Selects the transceiver mode for the CAN decoding. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: transceiver_md: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:CAN:TRCVmode?')
		return Conversions.str_to_scalar_enum(response, enums.SbusCanTransceiverMode)
