from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, mode: enums.AutoManualMode, noise=repcap.Noise.Default) -> None:
		"""TRIGger:NOISe<*>[:STATe] \n
		Snippet: driver.trigger.noise.state.set(mode = enums.AutoManualMode.AUTO, noise = repcap.Noise.Default) \n
		Selects how the hysteresis is set. \n
			:param mode:
				- AUTO: Automatic mode is the recommended mode. The hysteresis is set by the instrument to reject the internal noise of the instrument.
				- MANual: The hysteresis is defined with TRIGger:NOISem:ABSolute or TRIGger:NOISem:RELative.
			:param noise: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Noise')"""
		param = Conversions.enum_scalar_to_str(mode, enums.AutoManualMode)
		noise_cmd_val = self._cmd_group.get_repcap_cmd_value(noise, repcap.Noise)
		self._core.io.write(f'TRIGger:NOISe{noise_cmd_val}:STATe {param}')

	# noinspection PyTypeChecker
	def get(self, noise=repcap.Noise.Default) -> enums.AutoManualMode:
		"""TRIGger:NOISe<*>[:STATe] \n
		Snippet: value: enums.AutoManualMode = driver.trigger.noise.state.get(noise = repcap.Noise.Default) \n
		Selects how the hysteresis is set. \n
			:param noise: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Noise')
			:return: mode:
				- AUTO: Automatic mode is the recommended mode. The hysteresis is set by the instrument to reject the internal noise of the instrument.
				- MANual: The hysteresis is defined with TRIGger:NOISem:ABSolute or TRIGger:NOISem:RELative."""
		noise_cmd_val = self._cmd_group.get_repcap_cmd_value(noise, repcap.Noise)
		response = self._core.io.query_str(f'TRIGger:NOISe{noise_cmd_val}:STATe?')
		return Conversions.str_to_scalar_enum(response, enums.AutoManualMode)
