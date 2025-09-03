from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SactiveCls:
	"""Sactive commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sactive", core, parent)

	def set(self, layout=repcap.Layout.Default) -> None:
		"""LAYout<*>:SACTive \n
		Snippet: driver.layout.sactive.set(layout = repcap.Layout.Default) \n
		Activates the specified SmartGrid configuration. The command has the same effect as method RsMxo.Layout.Active.set but it
		has no query, and the active layout is specified by the suffix. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
		"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		self._core.io.write(f'LAYout{layout_cmd_val}:SACTive')

	def set_and_wait(self, layout=repcap.Layout.Default, opc_timeout_ms: int = -1) -> None:
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		"""LAYout<*>:SACTive \n
		Snippet: driver.layout.sactive.set_and_wait(layout = repcap.Layout.Default) \n
		Activates the specified SmartGrid configuration. The command has the same effect as method RsMxo.Layout.Active.set but it
		has no query, and the active layout is specified by the suffix. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'LAYout{layout_cmd_val}:SACTive', opc_timeout_ms)
