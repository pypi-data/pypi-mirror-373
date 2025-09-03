from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ViolationCls:
	"""Violation commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("violation", core, parent)

	def get(self, power=repcap.Power.Default, result=repcap.Result.Default) -> int:
		"""POWer<*>:HARMonics:RESult<*>:VIOLation \n
		Snippet: value: int = driver.power.harmonics.result.violation.get(power = repcap.Power.Default, result = repcap.Result.Default) \n
		Queries if the value of n-th harmonic is within the defined limit for the current measurement. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param result: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Result')
			:return: harmonic: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		result_cmd_val = self._cmd_group.get_repcap_cmd_value(result, repcap.Result)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:HARMonics:RESult{result_cmd_val}:VIOLation?')
		return Conversions.str_to_int(response)
