from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class GateCls:
	"""Gate commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("gate", core, parent)

	def set(self, gate: int, power=repcap.Power.Default) -> None:
		"""POWer<*>:QUALity:GATE \n
		Snippet: driver.power.quality.gate.set(gate = 1, power = repcap.Power.Default) \n
		Selects the gate that is used for limiting the range of the power quality measurement. Enable the gate before you assign
		a measurement to it (method RsMxo.Gate.Enable.set =ON) . \n
			:param gate: Number of the gate to be used
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.decimal_value_to_str(gate)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:QUALity:GATE {param}')

	def get(self, power=repcap.Power.Default) -> int:
		"""POWer<*>:QUALity:GATE \n
		Snippet: value: int = driver.power.quality.gate.get(power = repcap.Power.Default) \n
		Selects the gate that is used for limiting the range of the power quality measurement. Enable the gate before you assign
		a measurement to it (method RsMxo.Gate.Enable.set =ON) . \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: gate: Number of the gate to be used"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:QUALity:GATE?')
		return Conversions.str_to_int(response)
