from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class GfilterCls:
	"""Gfilter commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("gfilter", core, parent)

	def set(self, glitch_filter: bool, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:RFFE:GFILter \n
		Snippet: driver.sbus.rffe.gfilter.set(glitch_filter = False, serialBus = repcap.SerialBus.Default) \n
		Enables the glitch filter on the SCLK and SDATA lines to improve decode accuracy. \n
			:param glitch_filter: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.bool_to_str(glitch_filter)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:RFFE:GFILter {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> bool:
		"""SBUS<*>:RFFE:GFILter \n
		Snippet: value: bool = driver.sbus.rffe.gfilter.get(serialBus = repcap.SerialBus.Default) \n
		Enables the glitch filter on the SCLK and SDATA lines to improve decode accuracy. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: glitch_filter: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:RFFE:GFILter?')
		return Conversions.str_to_bool(response)
