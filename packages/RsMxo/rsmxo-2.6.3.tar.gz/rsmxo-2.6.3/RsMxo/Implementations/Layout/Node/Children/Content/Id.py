from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class IdCls:
	"""Id commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("id", core, parent)

	def set(self, idn: int, layout=repcap.Layout.Default, nodeIx=repcap.NodeIx.Default, children=repcap.Children.Default) -> None:
		"""LAYout<*>:NODE<*>:CHILdren<*>:CONTent:ID \n
		Snippet: driver.layout.node.children.content.id.set(idn = 1, layout = repcap.Layout.Default, nodeIx = repcap.NodeIx.Default, children = repcap.Children.Default) \n
		Sets the content ID, the number of the specified content type. For example, the 'Diagram5' has Type=DIAGRAM and ID=5. \n
			:param idn: Numeric value
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param nodeIx: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Node')
			:param children: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Children')
		"""
		param = Conversions.decimal_value_to_str(idn)
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		nodeIx_cmd_val = self._cmd_group.get_repcap_cmd_value(nodeIx, repcap.NodeIx)
		children_cmd_val = self._cmd_group.get_repcap_cmd_value(children, repcap.Children)
		self._core.io.write(f'LAYout{layout_cmd_val}:NODE{nodeIx_cmd_val}:CHILdren{children_cmd_val}:CONTent:ID {param}')

	def get(self, layout=repcap.Layout.Default, nodeIx=repcap.NodeIx.Default, children=repcap.Children.Default) -> int:
		"""LAYout<*>:NODE<*>:CHILdren<*>:CONTent:ID \n
		Snippet: value: int = driver.layout.node.children.content.id.get(layout = repcap.Layout.Default, nodeIx = repcap.NodeIx.Default, children = repcap.Children.Default) \n
		Sets the content ID, the number of the specified content type. For example, the 'Diagram5' has Type=DIAGRAM and ID=5. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param nodeIx: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Node')
			:param children: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Children')
			:return: idn: Numeric value"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		nodeIx_cmd_val = self._cmd_group.get_repcap_cmd_value(nodeIx, repcap.NodeIx)
		children_cmd_val = self._cmd_group.get_repcap_cmd_value(children, repcap.Children)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:NODE{nodeIx_cmd_val}:CHILdren{children_cmd_val}:CONTent:ID?')
		return Conversions.str_to_int(response)
