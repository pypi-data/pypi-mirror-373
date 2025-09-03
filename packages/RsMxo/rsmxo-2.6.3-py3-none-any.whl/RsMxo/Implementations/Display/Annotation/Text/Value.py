from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValueCls:
	"""Value commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("value", core, parent)

	def set(self, text: str = None, annotation=repcap.Annotation.Default) -> None:
		"""DISPlay:ANNotation:TEXT<*>[:VALue] \n
		Snippet: driver.display.annotation.text.value.set(text = 'abc', annotation = repcap.Annotation.Default) \n
		Adds a new text annotation or replaces the text value of an already existing text annotation. \n
			:param text: No help available
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
		"""
		param = ''
		if text:
			param = Conversions.value_to_quoted_str(text)
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		self._core.io.write(f'DISPlay:ANNotation:TEXT{annotation_cmd_val}:VALue {param}'.strip())

	def get(self, annotation=repcap.Annotation.Default) -> str:
		"""DISPlay:ANNotation:TEXT<*>[:VALue] \n
		Snippet: value: str = driver.display.annotation.text.value.get(annotation = repcap.Annotation.Default) \n
		Adds a new text annotation or replaces the text value of an already existing text annotation. \n
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
			:return: text: No help available"""
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		response = self._core.io.query_str(f'DISPlay:ANNotation:TEXT{annotation_cmd_val}:VALue?')
		return trim_str_response(response)
