from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PositionCls:
	"""Position commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("position", core, parent)

	def set(self, horizontal_pos: float, annotation=repcap.Annotation.Default) -> None:
		"""DISPlay:ANNotation:RECTangle<*>:HORizontal:POSition \n
		Snippet: driver.display.annotation.rectangle.horizontal.position.set(horizontal_pos = 1.0, annotation = repcap.Annotation.Default) \n
		Sets the horizontal position of the left edge of the rectangle annotation. See also 'Defining the position of the
		annotation'. \n
			:param horizontal_pos: In % of the screen
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
		"""
		param = Conversions.decimal_value_to_str(horizontal_pos)
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		self._core.io.write(f'DISPlay:ANNotation:RECTangle{annotation_cmd_val}:HORizontal:POSition {param}')

	def get(self, annotation=repcap.Annotation.Default) -> float:
		"""DISPlay:ANNotation:RECTangle<*>:HORizontal:POSition \n
		Snippet: value: float = driver.display.annotation.rectangle.horizontal.position.get(annotation = repcap.Annotation.Default) \n
		Sets the horizontal position of the left edge of the rectangle annotation. See also 'Defining the position of the
		annotation'. \n
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
			:return: horizontal_pos: In % of the screen"""
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		response = self._core.io.query_str(f'DISPlay:ANNotation:RECTangle{annotation_cmd_val}:HORizontal:POSition?')
		return Conversions.str_to_float(response)
