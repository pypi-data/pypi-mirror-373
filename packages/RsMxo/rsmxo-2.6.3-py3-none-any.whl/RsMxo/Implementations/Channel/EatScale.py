from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EatScaleCls:
	"""EatScale commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("eatScale", core, parent)

	def set(self, ext_att_scl: enums.AxisMode, channel=repcap.Channel.Default) -> None:
		"""CHANnel<*>:EATScale \n
		Snippet: driver.channel.eatScale.set(ext_att_scl = enums.AxisMode.LIN, channel = repcap.Channel.Default) \n
		Sets the attenuation scale for an external divider: linear or logarithmic. \n
			:param ext_att_scl: No help available
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
		"""
		param = Conversions.enum_scalar_to_str(ext_att_scl, enums.AxisMode)
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		self._core.io.write(f'CHANnel{channel_cmd_val}:EATScale {param}')

	# noinspection PyTypeChecker
	def get(self, channel=repcap.Channel.Default) -> enums.AxisMode:
		"""CHANnel<*>:EATScale \n
		Snippet: value: enums.AxisMode = driver.channel.eatScale.get(channel = repcap.Channel.Default) \n
		Sets the attenuation scale for an external divider: linear or logarithmic. \n
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
			:return: ext_att_scl: No help available"""
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		response = self._core.io.query_str(f'CHANnel{channel_cmd_val}:EATScale?')
		return Conversions.str_to_scalar_enum(response, enums.AxisMode)
