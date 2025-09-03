from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RangeCls:
	"""Range commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("range", core, parent)

	def set(self, timeout_mode: enums.HiLowMode, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:TIMeout:RANGe \n
		Snippet: driver.trigger.event.timeout.range.set(timeout_mode = enums.HiLowMode.EITHer, evnt = repcap.Evnt.Default) \n
		Sets the relation of the signal level to the trigger level for the timeout trigger. \n
			:param timeout_mode: HIGH = stays high, the signal level stays above the trigger level. LOW = stays low, the signal level stays below the trigger level. EITHer = stays high or low.
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.enum_scalar_to_str(timeout_mode, enums.HiLowMode)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:TIMeout:RANGe {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.HiLowMode:
		"""TRIGger:EVENt<*>:TIMeout:RANGe \n
		Snippet: value: enums.HiLowMode = driver.trigger.event.timeout.range.get(evnt = repcap.Evnt.Default) \n
		Sets the relation of the signal level to the trigger level for the timeout trigger. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: timeout_mode: HIGH = stays high, the signal level stays above the trigger level. LOW = stays low, the signal level stays below the trigger level. EITHer = stays high or low."""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:TIMeout:RANGe?')
		return Conversions.str_to_scalar_enum(response, enums.HiLowMode)
