from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FilDesignCls:
	"""FilDesign commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("filDesign", core, parent)

	def set(self, filter_design_typ: enums.FilterDesignType, channel=repcap.Channel.Default) -> None:
		"""CHANnel<*>:FILDesign \n
		Snippet: driver.channel.filDesign.set(filter_design_typ = enums.FilterDesignType.BETHomson, channel = repcap.Channel.Default) \n
		No command help available \n
			:param filter_design_typ: No help available
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
		"""
		param = Conversions.enum_scalar_to_str(filter_design_typ, enums.FilterDesignType)
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		self._core.io.write(f'CHANnel{channel_cmd_val}:FILDesign {param}')

	# noinspection PyTypeChecker
	def get(self, channel=repcap.Channel.Default) -> enums.FilterDesignType:
		"""CHANnel<*>:FILDesign \n
		Snippet: value: enums.FilterDesignType = driver.channel.filDesign.get(channel = repcap.Channel.Default) \n
		No command help available \n
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
			:return: filter_design_typ: No help available"""
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		response = self._core.io.query_str(f'CHANnel{channel_cmd_val}:FILDesign?')
		return Conversions.str_to_scalar_enum(response, enums.FilterDesignType)
