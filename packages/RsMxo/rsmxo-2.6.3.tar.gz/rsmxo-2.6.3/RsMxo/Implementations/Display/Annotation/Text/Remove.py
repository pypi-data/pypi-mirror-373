from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RemoveCls:
	"""Remove commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("remove", core, parent)

	def set(self, annotation=repcap.Annotation.Default) -> None:
		"""DISPlay:ANNotation:TEXT<*>:REMove \n
		Snippet: driver.display.annotation.text.remove.set(annotation = repcap.Annotation.Default) \n
		Removes the specified text annotation from the screen. \n
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
		"""
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		self._core.io.write(f'DISPlay:ANNotation:TEXT{annotation_cmd_val}:REMove')

	def set_and_wait(self, annotation=repcap.Annotation.Default, opc_timeout_ms: int = -1) -> None:
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		"""DISPlay:ANNotation:TEXT<*>:REMove \n
		Snippet: driver.display.annotation.text.remove.set_and_wait(annotation = repcap.Annotation.Default) \n
		Removes the specified text annotation from the screen. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'DISPlay:ANNotation:TEXT{annotation_cmd_val}:REMove', opc_timeout_ms)
