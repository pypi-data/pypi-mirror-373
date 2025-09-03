from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LevelCls:
	"""Level commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("level", core, parent)

	def set(self, clock_level: float, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:SETHold:CSOurce:LEVel \n
		Snippet: driver.trigger.event.setHold.csource.level.set(clock_level = 1.0, evnt = repcap.Evnt.Default) \n
		Sets the voltage level for the clock signal. Both the clock level and the clock edge define the starting point for
		calculation of the setup and hold time. \n
			:param clock_level: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.decimal_value_to_str(clock_level)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:SETHold:CSOurce:LEVel {param}')

	def get(self, evnt=repcap.Evnt.Default) -> float:
		"""TRIGger:EVENt<*>:SETHold:CSOurce:LEVel \n
		Snippet: value: float = driver.trigger.event.setHold.csource.level.get(evnt = repcap.Evnt.Default) \n
		Sets the voltage level for the clock signal. Both the clock level and the clock edge define the starting point for
		calculation of the setup and hold time. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: clock_level: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:SETHold:CSOurce:LEVel?')
		return Conversions.str_to_float(response)
