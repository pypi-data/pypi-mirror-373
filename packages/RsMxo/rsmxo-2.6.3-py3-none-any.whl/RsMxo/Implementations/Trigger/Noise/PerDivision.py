from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PerDivisionCls:
	"""PerDivision commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("perDivision", core, parent)

	def set(self, in_division: float, noise=repcap.Noise.Default) -> None:
		"""TRIGger:NOISe<*>:PERDivision \n
		Snippet: driver.trigger.noise.perDivision.set(in_division = 1.0, noise = repcap.Noise.Default) \n
		Defines a range in divisions around the trigger level in division units. If the signal oscillates inside this range and
		crosses the trigger level thereby, no trigger event occurs. \n
			:param in_division: No help available
			:param noise: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Noise')
		"""
		param = Conversions.decimal_value_to_str(in_division)
		noise_cmd_val = self._cmd_group.get_repcap_cmd_value(noise, repcap.Noise)
		self._core.io.write(f'TRIGger:NOISe{noise_cmd_val}:PERDivision {param}')

	def get(self, noise=repcap.Noise.Default) -> float:
		"""TRIGger:NOISe<*>:PERDivision \n
		Snippet: value: float = driver.trigger.noise.perDivision.get(noise = repcap.Noise.Default) \n
		Defines a range in divisions around the trigger level in division units. If the signal oscillates inside this range and
		crosses the trigger level thereby, no trigger event occurs. \n
			:param noise: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Noise')
			:return: in_division: No help available"""
		noise_cmd_val = self._cmd_group.get_repcap_cmd_value(noise, repcap.Noise)
		response = self._core.io.query_str(f'TRIGger:NOISe{noise_cmd_val}:PERDivision?')
		return Conversions.str_to_float(response)
