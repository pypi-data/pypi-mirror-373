from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class WidthCls:
	"""Width commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("width", core, parent)

	def set(self, width: float, annotation=repcap.Annotation.Default) -> None:
		"""DISPlay:ANNotation:RECTangle<*>:WIDTh \n
		Snippet: driver.display.annotation.rectangle.width.set(width = 1.0, annotation = repcap.Annotation.Default) \n
		Sets the width (horizontal size) of the rectangle annotation. \n
			:param width: In % of the screen
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
		"""
		param = Conversions.decimal_value_to_str(width)
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		self._core.io.write(f'DISPlay:ANNotation:RECTangle{annotation_cmd_val}:WIDTh {param}')

	def get(self, annotation=repcap.Annotation.Default) -> float:
		"""DISPlay:ANNotation:RECTangle<*>:WIDTh \n
		Snippet: value: float = driver.display.annotation.rectangle.width.get(annotation = repcap.Annotation.Default) \n
		Sets the width (horizontal size) of the rectangle annotation. \n
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
			:return: width: In % of the screen"""
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		response = self._core.io.query_str(f'DISPlay:ANNotation:RECTangle{annotation_cmd_val}:WIDTh?')
		return Conversions.str_to_float(response)
