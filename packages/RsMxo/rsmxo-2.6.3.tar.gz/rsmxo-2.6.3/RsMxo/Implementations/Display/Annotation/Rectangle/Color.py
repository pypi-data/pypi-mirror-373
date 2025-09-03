from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ColorCls:
	"""Color commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("color", core, parent)

	def set(self, type_py: enums.Color, annotation=repcap.Annotation.Default) -> None:
		"""DISPlay:ANNotation:RECTangle<*>:COLor \n
		Snippet: driver.display.annotation.rectangle.color.set(type_py = enums.Color.BLUE, annotation = repcap.Annotation.Default) \n
		Sets the color of the indicated rectangle annotation. \n
			:param type_py: See Table 'Color catalog for annotations'.
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.Color)
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		self._core.io.write(f'DISPlay:ANNotation:RECTangle{annotation_cmd_val}:COLor {param}')

	# noinspection PyTypeChecker
	def get(self, annotation=repcap.Annotation.Default) -> enums.Color:
		"""DISPlay:ANNotation:RECTangle<*>:COLor \n
		Snippet: value: enums.Color = driver.display.annotation.rectangle.color.get(annotation = repcap.Annotation.Default) \n
		Sets the color of the indicated rectangle annotation. \n
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
			:return: type_py: See Table 'Color catalog for annotations'."""
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		response = self._core.io.query_str(f'DISPlay:ANNotation:RECTangle{annotation_cmd_val}:COLor?')
		return Conversions.str_to_scalar_enum(response, enums.Color)
