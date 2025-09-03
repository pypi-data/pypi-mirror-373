from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.Types import DataType
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ExtendCls:
	"""Extend commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("extend", core, parent)

	def set(self, x: float = None, y: float = None, annotation=repcap.Annotation.Default) -> None:
		"""DISPlay:ANNotation:PLINe<*>:EXTend \n
		Snippet: driver.display.annotation.pline.extend.set(x = 1.0, y = 1.0, annotation = repcap.Annotation.Default) \n
		Expands the draw item with a segment. The x and y position of the existing end point is the start point of the new
		segment. The segments are always a straight lines. \n
			:param x: Horizontal position of the end point of the new segment
			:param y: Vertical position of the end point of the new segment
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('x', x, DataType.Float, None, is_optional=True), ArgSingle('y', y, DataType.Float, None, is_optional=True))
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		self._core.io.write(f'DISPlay:ANNotation:PLINe{annotation_cmd_val}:EXTend {param}'.rstrip())
