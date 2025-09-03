from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RatioCls:
	"""Ratio commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ratio", core, parent)

	def set(self, split_ratio: float, layout=repcap.Layout.Default, nodeIx=repcap.NodeIx.Default) -> None:
		"""LAYout<*>:NODE<*>:RATio \n
		Snippet: driver.layout.node.ratio.set(split_ratio = 1.0, layout = repcap.Layout.Default, nodeIx = repcap.NodeIx.Default) \n
		Sets the size ratio of the two children in the specified node. \n
			:param split_ratio: Size ratio of the children. 0.5 assigns 50% of the node size to each child. 0.3 assigns 30% to child 1% and 70% to child 2.
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param nodeIx: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Node')
		"""
		param = Conversions.decimal_value_to_str(split_ratio)
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		nodeIx_cmd_val = self._cmd_group.get_repcap_cmd_value(nodeIx, repcap.NodeIx)
		self._core.io.write(f'LAYout{layout_cmd_val}:NODE{nodeIx_cmd_val}:RATio {param}')

	def get(self, layout=repcap.Layout.Default, nodeIx=repcap.NodeIx.Default) -> float:
		"""LAYout<*>:NODE<*>:RATio \n
		Snippet: value: float = driver.layout.node.ratio.get(layout = repcap.Layout.Default, nodeIx = repcap.NodeIx.Default) \n
		Sets the size ratio of the two children in the specified node. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param nodeIx: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Node')
			:return: split_ratio: Size ratio of the children. 0.5 assigns 50% of the node size to each child. 0.3 assigns 30% to child 1% and 70% to child 2."""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		nodeIx_cmd_val = self._cmd_group.get_repcap_cmd_value(nodeIx, repcap.NodeIx)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:NODE{nodeIx_cmd_val}:RATio?')
		return Conversions.str_to_float(response)
