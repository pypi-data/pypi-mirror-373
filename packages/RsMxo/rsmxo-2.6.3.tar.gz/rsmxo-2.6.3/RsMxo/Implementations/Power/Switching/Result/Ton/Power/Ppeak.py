from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PpeakCls:
	"""Ppeak commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ppeak", core, parent)

	def get(self, power=repcap.Power.Default) -> float:
		"""POWer<*>:SWITching:RESult:TON:POWer:PPEak \n
		Snippet: value: float = driver.power.switching.result.ton.power.ppeak.get(power = repcap.Power.Default) \n
		Return the positive peak value (maximum) of the selected measurement type if statistics are enabled. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: max_peak: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:SWITching:RESult:TON:POWer:PPEak?')
		return Conversions.str_to_float(response)
