from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LowerCls:
	"""Lower commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("lower", core, parent)

	def set(self, level: float, evnt=repcap.Evnt.Default, lvl=repcap.Lvl.Default) -> None:
		"""TRIGger:EVENt<*>:LEVel<*>:SLEW:LOWer \n
		Snippet: driver.trigger.event.level.slew.lower.set(level = 1.0, evnt = repcap.Evnt.Default, lvl = repcap.Lvl.Default) \n
		Sets the lower voltage threshold. When the signal crosses this level, the slew rate measurement starts or stops depending
		on the selected slope. \n
			:param level: No help available
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:param lvl: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Level')
		"""
		param = Conversions.decimal_value_to_str(level)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		lvl_cmd_val = self._cmd_group.get_repcap_cmd_value(lvl, repcap.Lvl)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:LEVel{lvl_cmd_val}:SLEW:LOWer {param}')

	def get(self, evnt=repcap.Evnt.Default, lvl=repcap.Lvl.Default) -> float:
		"""TRIGger:EVENt<*>:LEVel<*>:SLEW:LOWer \n
		Snippet: value: float = driver.trigger.event.level.slew.lower.get(evnt = repcap.Evnt.Default, lvl = repcap.Lvl.Default) \n
		Sets the lower voltage threshold. When the signal crosses this level, the slew rate measurement starts or stops depending
		on the selected slope. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:param lvl: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Level')
			:return: level: No help available"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		lvl_cmd_val = self._cmd_group.get_repcap_cmd_value(lvl, repcap.Lvl)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:LEVel{lvl_cmd_val}:SLEW:LOWer?')
		return Conversions.str_to_float(response)
