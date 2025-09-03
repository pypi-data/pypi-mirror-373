from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.Types import DataType
from .....Internal.StructBase import StructBase
from .....Internal.ArgStruct import ArgStruct
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValueCls:
	"""Value commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("value", core, parent)

	def set(self, horizontal_pos: float = None, vertical_pos: float = None, width: float = None, height: float = None, annotation=repcap.Annotation.Default) -> None:
		"""DISPlay:ANNotation:RECTangle<*>[:VALue] \n
		Snippet: driver.display.annotation.rectangle.value.set(horizontal_pos = 1.0, vertical_pos = 1.0, width = 1.0, height = 1.0, annotation = repcap.Annotation.Default) \n
		Adds a new rectangle annotation, or replaces the annotation if it already exists. If no parameters are defined, the
		default values are used. All parameters are given in % of the screen. \n
			:param horizontal_pos: No help available
			:param vertical_pos: No help available
			:param width: No help available
			:param height: No help available
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('horizontal_pos', horizontal_pos, DataType.Float, None, is_optional=True), ArgSingle('vertical_pos', vertical_pos, DataType.Float, None, is_optional=True), ArgSingle('width', width, DataType.Float, None, is_optional=True), ArgSingle('height', height, DataType.Float, None, is_optional=True))
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		self._core.io.write(f'DISPlay:ANNotation:RECTangle{annotation_cmd_val}:VALue {param}'.rstrip())

	# noinspection PyTypeChecker
	class ValueStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Horizontal_Pos: float: No parameter help available
			- 2 Vertical_Pos: float: No parameter help available
			- 3 Width: float: No parameter help available
			- 4 Height: float: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_float('Horizontal_Pos'),
			ArgStruct.scalar_float('Vertical_Pos'),
			ArgStruct.scalar_float('Width'),
			ArgStruct.scalar_float('Height')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Horizontal_Pos: float = None
			self.Vertical_Pos: float = None
			self.Width: float = None
			self.Height: float = None

	def get(self, annotation=repcap.Annotation.Default) -> ValueStruct:
		"""DISPlay:ANNotation:RECTangle<*>[:VALue] \n
		Snippet: value: ValueStruct = driver.display.annotation.rectangle.value.get(annotation = repcap.Annotation.Default) \n
		Adds a new rectangle annotation, or replaces the annotation if it already exists. If no parameters are defined, the
		default values are used. All parameters are given in % of the screen. \n
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
			:return: structure: for return value, see the help for ValueStruct structure arguments."""
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		return self._core.io.query_struct(f'DISPlay:ANNotation:RECTangle{annotation_cmd_val}:VALue?', self.__class__.ValueStruct())
