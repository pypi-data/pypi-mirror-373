from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ActualCls:
	"""Actual commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("actual", core, parent)

	def get(self, power=repcap.Power.Default) -> float:
		"""POWer<*>:SWITching:RESult:TOTal:POWer[:ACTual] \n
		Snippet: value: float = driver.power.switching.result.total.power.actual.get(power = repcap.Power.Default) \n
		Return the current result value of the selected measurement type. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: actual: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:SWITching:RESult:TOTal:POWer:ACTual?')
		return Conversions.str_to_float(response)
