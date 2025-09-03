from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ModeCls:
	"""Mode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mode", core, parent)

	def set(self, mode: enums.AbsRel, noise=repcap.Noise.Default) -> None:
		"""TRIGger:NOISe<*>:MODE \n
		Snippet: driver.trigger.noise.mode.set(mode = enums.AbsRel.ABS, noise = repcap.Noise.Default) \n
		Selects whether the hysteresis is defined in absolute or relative values. The setting is available only in manual
		hysteresis mode. \n
			:param mode: No help available
			:param noise: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Noise')
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.AbsRel)
		noise_cmd_val = self._cmd_group.get_repcap_cmd_value(noise, repcap.Noise)
		self._core.io.write(f'TRIGger:NOISe{noise_cmd_val}:MODE {param}')

	# noinspection PyTypeChecker
	def get(self, noise=repcap.Noise.Default) -> enums.AbsRel:
		"""TRIGger:NOISe<*>:MODE \n
		Snippet: value: enums.AbsRel = driver.trigger.noise.mode.get(noise = repcap.Noise.Default) \n
		Selects whether the hysteresis is defined in absolute or relative values. The setting is available only in manual
		hysteresis mode. \n
			:param noise: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Noise')
			:return: mode: No help available"""
		noise_cmd_val = self._cmd_group.get_repcap_cmd_value(noise, repcap.Noise)
		response = self._core.io.query_str(f'TRIGger:NOISe{noise_cmd_val}:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.AbsRel)
