from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EattenuationCls:
	"""Eattenuation commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("eattenuation", core, parent)

	def set(self, ext_att: float, channel=repcap.Channel.Default) -> None:
		"""CHANnel<*>:EATTenuation \n
		Snippet: driver.channel.eattenuation.set(ext_att = 1.0, channel = repcap.Channel.Default) \n
		Consider a voltage divider that is part of the DUT before the measuring point. The external attenuation is included in
		the measurement, and the instrument shows the results that would be measured before the divider. External attenuation can
		be used with all probes. \n
			:param ext_att: Values depend on the selected scale (method RsMxo.Channel.EatScale.set) and the unit of the waveform. See 'External Attenuation: Scale, Attenuation'. Limits below are for linear scale.
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
		"""
		param = Conversions.decimal_value_to_str(ext_att)
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		self._core.io.write(f'CHANnel{channel_cmd_val}:EATTenuation {param}')

	def get(self, channel=repcap.Channel.Default) -> float:
		"""CHANnel<*>:EATTenuation \n
		Snippet: value: float = driver.channel.eattenuation.get(channel = repcap.Channel.Default) \n
		Consider a voltage divider that is part of the DUT before the measuring point. The external attenuation is included in
		the measurement, and the instrument shows the results that would be measured before the divider. External attenuation can
		be used with all probes. \n
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
			:return: ext_att: Values depend on the selected scale (method RsMxo.Channel.EatScale.set) and the unit of the waveform. See 'External Attenuation: Scale, Attenuation'. Limits below are for linear scale."""
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		response = self._core.io.query_str(f'CHANnel{channel_cmd_val}:EATTenuation?')
		return Conversions.str_to_float(response)
