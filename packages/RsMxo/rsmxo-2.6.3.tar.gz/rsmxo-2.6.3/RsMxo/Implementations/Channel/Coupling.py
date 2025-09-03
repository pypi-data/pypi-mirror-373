from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CouplingCls:
	"""Coupling commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("coupling", core, parent)

	def set(self, value: enums.Coupling, channel=repcap.Channel.Default) -> None:
		"""CHANnel<*>:COUPling \n
		Snippet: driver.channel.coupling.set(value = enums.Coupling.AC, channel = repcap.Channel.Default) \n
		Sets the connection of the channel signal, i.e. the input impedance (termination) and a filter (coupling) . The command
		determines what part of the signal is used for waveform analysis and triggering. \n
			:param value:
				- DC: Connection with 50 Ω termination, passes both DC and AC components of the signal.
				- DCLimit: Connection with 1 MΩ termination, passes both DC and AC components of the signal.
				- AC: Connection with 1 MΩ termination through DC capacitor, removes DC and very low-frequency components. The waveform is centered on zero volts.
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')"""
		param = Conversions.enum_scalar_to_str(value, enums.Coupling)
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		self._core.io.write(f'CHANnel{channel_cmd_val}:COUPling {param}')

	# noinspection PyTypeChecker
	def get(self, channel=repcap.Channel.Default) -> enums.Coupling:
		"""CHANnel<*>:COUPling \n
		Snippet: value: enums.Coupling = driver.channel.coupling.get(channel = repcap.Channel.Default) \n
		Sets the connection of the channel signal, i.e. the input impedance (termination) and a filter (coupling) . The command
		determines what part of the signal is used for waveform analysis and triggering. \n
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
			:return: value:
				- DC: Connection with 50 Ω termination, passes both DC and AC components of the signal.
				- DCLimit: Connection with 1 MΩ termination, passes both DC and AC components of the signal.
				- AC: Connection with 1 MΩ termination through DC capacitor, removes DC and very low-frequency components. The waveform is centered on zero volts."""
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		response = self._core.io.query_str(f'CHANnel{channel_cmd_val}:COUPling?')
		return Conversions.str_to_scalar_enum(response, enums.Coupling)
