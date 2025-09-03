from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AvailableCls:
	"""Available commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("available", core, parent)

	def get(self, power=repcap.Power.Default) -> int:
		"""POWer<*>:HARMonics:AVAilable \n
		Snippet: value: int = driver.power.harmonics.available.get(power = repcap.Power.Default) \n
		Returns the number of measured harmonics. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: count: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:HARMonics:AVAilable?')
		return Conversions.str_to_int(response)
