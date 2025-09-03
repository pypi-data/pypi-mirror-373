from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MtpDurationCls:
	"""MtpDuration commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mtpDuration", core, parent)

	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> float:
		"""SBUS<*>:SENT:FRAMe<*>:MTPDuration \n
		Snippet: value: float = driver.sbus.sent.frame.mtpDuration.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns the duration of the main trigger pulse (MTP) , which is an additional pulse added to the frame when running in
		'Short PWM Code' (SPC) mode. Withpulse width modulationn (PWM) , you can connect multiple sensors to the bus.
		The duration of the MTP defines, which sensor starts the transmission. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: mtp_duration: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SENT:FRAMe{frame_cmd_val}:MTPDuration?')
		return Conversions.str_to_float(response)
