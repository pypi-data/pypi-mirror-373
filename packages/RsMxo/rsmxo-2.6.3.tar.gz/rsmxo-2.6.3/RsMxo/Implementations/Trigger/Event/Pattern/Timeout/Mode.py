from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ModeCls:
	"""Mode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mode", core, parent)

	def set(self, timeout_mode: enums.HiLowMode, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:PATTern:TIMeout:MODE \n
		Snippet: driver.trigger.event.pattern.timeout.mode.set(timeout_mode = enums.HiLowMode.EITHer, evnt = repcap.Evnt.Default) \n
		No command help available \n
			:param timeout_mode: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.enum_scalar_to_str(timeout_mode, enums.HiLowMode)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:PATTern:TIMeout:MODE {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.HiLowMode:
		"""TRIGger:EVENt<*>:PATTern:TIMeout:MODE \n
		Snippet: value: enums.HiLowMode = driver.trigger.event.pattern.timeout.mode.get(evnt = repcap.Evnt.Default) \n
		No command help available \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: timeout_mode: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:PATTern:TIMeout:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.HiLowMode)
