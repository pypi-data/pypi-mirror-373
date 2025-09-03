from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ActualCls:
	"""Actual commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("actual", core, parent)

	def get(self, power=repcap.Power.Default, result=repcap.Result.Default) -> float:
		"""POWer<*>:ONOFf:RESult<*>:TIME[:ACTual] \n
		Snippet: value: float = driver.power.onOff.result.time.actual.get(power = repcap.Power.Default, result = repcap.Result.Default) \n
		Returns the measured turn-on time or turn-off time of the specified input-output pair. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param result: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Result')
			:return: delay_meas_result: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		result_cmd_val = self._cmd_group.get_repcap_cmd_value(result, repcap.Result)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:ONOFf:RESult{result_cmd_val}:TIME:ACTual?')
		return Conversions.str_to_float(response)
