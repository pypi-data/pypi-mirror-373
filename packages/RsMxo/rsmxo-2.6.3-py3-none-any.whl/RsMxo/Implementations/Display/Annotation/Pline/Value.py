from typing import List

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

	def set(self, x_1: float, y_1: float, x_2: float, y_2: float, xn: List[float] = None, annotation=repcap.Annotation.Default) -> None:
		"""DISPlay:ANNotation:PLINe<*>[:VALue] \n
		Snippet: driver.display.annotation.pline.value.set(x_1 = 1.0, y_1 = 1.0, x_2 = 1.0, y_2 = 1.0, xn = [1.1, 2.2, 3.3], annotation = repcap.Annotation.Default) \n
		Adds a new draw annotation, or replaces the annotation if it already exists. If no parameters are defined, the default
		values are used. All parameters are given in % of the screen. \n
			:param x_1: Horizontal position of the start point of the new line
			:param y_1: Vertical position of the start point of the new line
			:param x_2: Horizontal position of the endpoint of the new line
			:param y_2: Vertical position of the endpoint of the new line
			:param xn: No help available
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('x_1', x_1, DataType.Float), ArgSingle('y_1', y_1, DataType.Float), ArgSingle('x_2', x_2, DataType.Float), ArgSingle('y_2', y_2, DataType.Float), ArgSingle('xn', xn, DataType.FloatList, None, True, True, 1))
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		self._core.io.write(f'DISPlay:ANNotation:PLINe{annotation_cmd_val}:VALue {param}'.rstrip())

	# noinspection PyTypeChecker
	class ValueStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 X_1: float: Horizontal position of the start point of the new line
			- 2 Y_1: float: Vertical position of the start point of the new line
			- 3 X_2: float: Horizontal position of the endpoint of the new line
			- 4 Y_2: float: Vertical position of the endpoint of the new line
			- 5 Xn: List[float]: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_float('X_1'),
			ArgStruct.scalar_float('Y_1'),
			ArgStruct.scalar_float('X_2'),
			ArgStruct.scalar_float('Y_2'),
			ArgStruct('Xn', DataType.FloatList, None, False, True, 1)]

		def __init__(self):
			StructBase.__init__(self, self)
			self.X_1: float = None
			self.Y_1: float = None
			self.X_2: float = None
			self.Y_2: float = None
			self.Xn: List[float] = None

	def get(self, annotation=repcap.Annotation.Default) -> ValueStruct:
		"""DISPlay:ANNotation:PLINe<*>[:VALue] \n
		Snippet: value: ValueStruct = driver.display.annotation.pline.value.get(annotation = repcap.Annotation.Default) \n
		Adds a new draw annotation, or replaces the annotation if it already exists. If no parameters are defined, the default
		values are used. All parameters are given in % of the screen. \n
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
			:return: structure: for return value, see the help for ValueStruct structure arguments."""
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		return self._core.io.query_struct(f'DISPlay:ANNotation:PLINe{annotation_cmd_val}:VALue?', self.__class__.ValueStruct())
