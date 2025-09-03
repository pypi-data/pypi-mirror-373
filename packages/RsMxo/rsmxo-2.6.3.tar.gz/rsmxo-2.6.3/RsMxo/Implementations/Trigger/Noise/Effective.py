from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EffectiveCls:
	"""Effective commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("effective", core, parent)

	def get(self, noise=repcap.Noise.Default) -> float:
		"""TRIGger:NOISe<*>:EFFective \n
		Snippet: value: float = driver.trigger.noise.effective.get(noise = repcap.Noise.Default) \n
		Returns the hysteresis that is set by the instrument in automatic hysteresis mode. \n
			:param noise: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Noise')
			:return: effective: No help available"""
		noise_cmd_val = self._cmd_group.get_repcap_cmd_value(noise, repcap.Noise)
		response = self._core.io.query_str(f'TRIGger:NOISe{noise_cmd_val}:EFFective?')
		return Conversions.str_to_float(response)
