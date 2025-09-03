from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EvtCountCls:
	"""EvtCount commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("evtCount", core, parent)

	def get(self, power=repcap.Power.Default) -> int:
		"""POWer<*>:QUALity:RESult:POWer:APParent:EVTCount \n
		Snippet: value: int = driver.power.quality.result.power.apparent.evtCount.get(power = repcap.Power.Default) \n
		Returns the apparent power for the power quality analysis. For details on the statistics, see 'Overview of statistic
		commands'. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: count: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:QUALity:RESult:POWer:APParent:EVTCount?')
		return Conversions.str_to_int(response)
