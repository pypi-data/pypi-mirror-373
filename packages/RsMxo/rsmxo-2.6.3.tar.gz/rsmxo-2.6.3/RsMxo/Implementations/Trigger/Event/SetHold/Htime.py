from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HtimeCls:
	"""Htime commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("htime", core, parent)

	def set(self, hold_time: float, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:SETHold:HTIMe \n
		Snippet: driver.trigger.event.setHold.htime.set(hold_time = 1.0, evnt = repcap.Evnt.Default) \n
		Sets the minimum time after the clock edge while the data signal must stay steady above or below the data level. \n
			:param hold_time: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.decimal_value_to_str(hold_time)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:SETHold:HTIMe {param}')

	def get(self, evnt=repcap.Evnt.Default) -> float:
		"""TRIGger:EVENt<*>:SETHold:HTIMe \n
		Snippet: value: float = driver.trigger.event.setHold.htime.get(evnt = repcap.Evnt.Default) \n
		Sets the minimum time after the clock edge while the data signal must stay steady above or below the data level. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: hold_time: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:SETHold:HTIMe?')
		return Conversions.str_to_float(response)
