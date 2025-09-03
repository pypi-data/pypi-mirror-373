from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CountCls:
	"""Count commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("count", core, parent)

	def get(self, layout=repcap.Layout.Default) -> int:
		"""LAYout<*>:COUNt \n
		Snippet: value: int = driver.layout.count.get(layout = repcap.Layout.Default) \n
		Returns the number of available layouts, i.e. SmartGrid configurations. By default, they named Diagram Set on the display. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:return: count: Number of SmartGrid configurations"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:COUNt?')
		return Conversions.str_to_int(response)
