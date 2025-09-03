from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AbsoluteCls:
	"""Absolute commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("absolute", core, parent)

	def set(self, absolute: float, noise=repcap.Noise.Default) -> None:
		"""TRIGger:NOISe<*>:ABSolute \n
		Snippet: driver.trigger.noise.absolute.set(absolute = 1.0, noise = repcap.Noise.Default) \n
		Defines a range in absolute values around the trigger level. If the signal oscillates inside this range and thus crosses
		the trigger level, no trigger event occurs. \n
			:param absolute: No help available
			:param noise: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Noise')
		"""
		param = Conversions.decimal_value_to_str(absolute)
		noise_cmd_val = self._cmd_group.get_repcap_cmd_value(noise, repcap.Noise)
		self._core.io.write(f'TRIGger:NOISe{noise_cmd_val}:ABSolute {param}')

	def get(self, noise=repcap.Noise.Default) -> float:
		"""TRIGger:NOISe<*>:ABSolute \n
		Snippet: value: float = driver.trigger.noise.absolute.get(noise = repcap.Noise.Default) \n
		Defines a range in absolute values around the trigger level. If the signal oscillates inside this range and thus crosses
		the trigger level, no trigger event occurs. \n
			:param noise: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Noise')
			:return: absolute: No help available"""
		noise_cmd_val = self._cmd_group.get_repcap_cmd_value(noise, repcap.Noise)
		response = self._core.io.query_str(f'TRIGger:NOISe{noise_cmd_val}:ABSolute?')
		return Conversions.str_to_float(response)
