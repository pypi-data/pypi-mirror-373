from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TypePyCls:
	"""TypePy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("typePy", core, parent)

	def set(self, type_py: enums.ContentType, layout=repcap.Layout.Default, nodeIx=repcap.NodeIx.Default, children=repcap.Children.Default) -> None:
		"""LAYout<*>:NODE<*>:CHILdren<*>:CONTent:TYPE \n
		Snippet: driver.layout.node.children.content.typePy.set(type_py = enums.ContentType.DIAG, layout = repcap.Layout.Default, nodeIx = repcap.NodeIx.Default, children = repcap.Children.Default) \n
		Sets the content type for a specified child in a specified node: diagram, result table, another node, or empty.
		For example, the 'Diagram5' has Type=DIAGRAM and ID=5. \n
			:param type_py: DIAG = DIAGRAM, RES = RESULT
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param nodeIx: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Node')
			:param children: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Children')
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.ContentType)
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		nodeIx_cmd_val = self._cmd_group.get_repcap_cmd_value(nodeIx, repcap.NodeIx)
		children_cmd_val = self._cmd_group.get_repcap_cmd_value(children, repcap.Children)
		self._core.io.write(f'LAYout{layout_cmd_val}:NODE{nodeIx_cmd_val}:CHILdren{children_cmd_val}:CONTent:TYPE {param}')

	# noinspection PyTypeChecker
	def get(self, layout=repcap.Layout.Default, nodeIx=repcap.NodeIx.Default, children=repcap.Children.Default) -> enums.ContentType:
		"""LAYout<*>:NODE<*>:CHILdren<*>:CONTent:TYPE \n
		Snippet: value: enums.ContentType = driver.layout.node.children.content.typePy.get(layout = repcap.Layout.Default, nodeIx = repcap.NodeIx.Default, children = repcap.Children.Default) \n
		Sets the content type for a specified child in a specified node: diagram, result table, another node, or empty.
		For example, the 'Diagram5' has Type=DIAGRAM and ID=5. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param nodeIx: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Node')
			:param children: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Children')
			:return: type_py: DIAG = DIAGRAM, RES = RESULT"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		nodeIx_cmd_val = self._cmd_group.get_repcap_cmd_value(nodeIx, repcap.NodeIx)
		children_cmd_val = self._cmd_group.get_repcap_cmd_value(children, repcap.Children)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:NODE{nodeIx_cmd_val}:CHILdren{children_cmd_val}:CONTent:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.ContentType)
