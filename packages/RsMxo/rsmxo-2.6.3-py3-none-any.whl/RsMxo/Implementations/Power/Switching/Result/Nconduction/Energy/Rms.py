from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RmsCls:
	"""Rms commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rms", core, parent)

	def get(self, power=repcap.Power.Default) -> float:
		"""POWer<*>:SWITching:RESult:NCONduction:ENERgy:RMS \n
		Snippet: value: float = driver.power.switching.result.nconduction.energy.rms.get(power = repcap.Power.Default) \n
		Return the RMS value of the selected measurement type if statistics are enabled. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: rms: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:SWITching:RESult:NCONduction:ENERgy:RMS?')
		return Conversions.str_to_float(response)
