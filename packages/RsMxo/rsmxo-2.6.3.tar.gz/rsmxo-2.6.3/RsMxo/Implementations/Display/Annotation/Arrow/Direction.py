from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DirectionCls:
	"""Direction commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("direction", core, parent)

	def set(self, type_py: enums.TypePy, annotation=repcap.Annotation.Default) -> None:
		"""DISPlay:ANNotation:ARRow<*>:DIRection \n
		Snippet: driver.display.annotation.arrow.direction.set(type_py = enums.TypePy.BLEFt, annotation = repcap.Annotation.Default) \n
		Sets the direction of the indicated arrow annotation from strating point to arrow tip. \n
			:param type_py: TLEFt: to top left TRIGht: to top right BLEFt: to bottom left BRIGht: to bottom right
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.TypePy)
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		self._core.io.write(f'DISPlay:ANNotation:ARRow{annotation_cmd_val}:DIRection {param}')

	# noinspection PyTypeChecker
	def get(self, annotation=repcap.Annotation.Default) -> enums.TypePy:
		"""DISPlay:ANNotation:ARRow<*>:DIRection \n
		Snippet: value: enums.TypePy = driver.display.annotation.arrow.direction.get(annotation = repcap.Annotation.Default) \n
		Sets the direction of the indicated arrow annotation from strating point to arrow tip. \n
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
			:return: type_py: TLEFt: to top left TRIGht: to top right BLEFt: to bottom left BRIGht: to bottom right"""
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		response = self._core.io.query_str(f'DISPlay:ANNotation:ARRow{annotation_cmd_val}:DIRection?')
		return Conversions.str_to_scalar_enum(response, enums.TypePy)
