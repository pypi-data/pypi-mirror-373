from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HeightCls:
	"""Height commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("height", core, parent)

	def set(self, height: float, annotation=repcap.Annotation.Default) -> None:
		"""DISPlay:ANNotation:RECTangle<*>:HEIGht \n
		Snippet: driver.display.annotation.rectangle.height.set(height = 1.0, annotation = repcap.Annotation.Default) \n
		Sets the height (vertical size) of the rectangle annotation. \n
			:param height: In % of the screen.
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
		"""
		param = Conversions.decimal_value_to_str(height)
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		self._core.io.write(f'DISPlay:ANNotation:RECTangle{annotation_cmd_val}:HEIGht {param}')

	def get(self, annotation=repcap.Annotation.Default) -> float:
		"""DISPlay:ANNotation:RECTangle<*>:HEIGht \n
		Snippet: value: float = driver.display.annotation.rectangle.height.get(annotation = repcap.Annotation.Default) \n
		Sets the height (vertical size) of the rectangle annotation. \n
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
			:return: height: In % of the screen."""
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		response = self._core.io.query_str(f'DISPlay:ANNotation:RECTangle{annotation_cmd_val}:HEIGht?')
		return Conversions.str_to_float(response)
