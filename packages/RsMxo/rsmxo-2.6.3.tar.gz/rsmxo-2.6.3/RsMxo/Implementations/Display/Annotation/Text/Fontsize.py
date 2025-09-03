from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FontsizeCls:
	"""Fontsize commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fontsize", core, parent)

	def set(self, fontsize: int, annotation=repcap.Annotation.Default) -> None:
		"""DISPlay:ANNotation:TEXT<*>:FONTsize \n
		Snippet: driver.display.annotation.text.fontsize.set(fontsize = 1, annotation = repcap.Annotation.Default) \n
		Sets the font size of the text. \n
			:param fontsize: No help available
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
		"""
		param = Conversions.decimal_value_to_str(fontsize)
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		self._core.io.write(f'DISPlay:ANNotation:TEXT{annotation_cmd_val}:FONTsize {param}')

	def get(self, annotation=repcap.Annotation.Default) -> int:
		"""DISPlay:ANNotation:TEXT<*>:FONTsize \n
		Snippet: value: int = driver.display.annotation.text.fontsize.get(annotation = repcap.Annotation.Default) \n
		Sets the font size of the text. \n
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
			:return: fontsize: No help available"""
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		response = self._core.io.query_str(f'DISPlay:ANNotation:TEXT{annotation_cmd_val}:FONTsize?')
		return Conversions.str_to_int(response)
