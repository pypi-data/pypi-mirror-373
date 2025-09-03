from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StdDevCls:
	"""StdDev commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("stdDev", core, parent)

	def get(self, power=repcap.Power.Default) -> float:
		"""POWer<*>:QUALity:RESult:VOLTage:PEAK:STDDev \n
		Snippet: value: float = driver.power.quality.result.voltage.peak.stdDev.get(power = repcap.Power.Default) \n
		Returns the voltage peak value, the highest measured magnitude value for the power quality analysis. For details on the
		statistics, see 'Overview of statistic commands'. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: std_dev: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:QUALity:RESult:VOLTage:PEAK:STDDev?')
		return Conversions.str_to_float(response)
