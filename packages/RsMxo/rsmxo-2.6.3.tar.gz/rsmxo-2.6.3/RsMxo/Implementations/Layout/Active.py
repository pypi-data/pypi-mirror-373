from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ActiveCls:
	"""Active commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("active", core, parent)

	def set(self, active_key: int, layout=repcap.Layout.Default) -> None:
		"""LAYout<*>:ACTive \n
		Snippet: driver.layout.active.set(active_key = 1, layout = repcap.Layout.Default) \n
		Sets the active SmartGrid configuration. The query returns the index of the active layout. \n
			:param active_key: Index of the active layout
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
		"""
		param = Conversions.decimal_value_to_str(active_key)
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		self._core.io.write(f'LAYout{layout_cmd_val}:ACTive {param}')

	def get(self, layout=repcap.Layout.Default) -> int:
		"""LAYout<*>:ACTive \n
		Snippet: value: int = driver.layout.active.get(layout = repcap.Layout.Default) \n
		Sets the active SmartGrid configuration. The query returns the index of the active layout. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:return: active_key: Index of the active layout"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:ACTive?')
		return Conversions.str_to_int(response)
