from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StypeCls:
	"""Stype commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("stype", core, parent)

	def set(self, split_type: enums.LayoutSplitType, layout=repcap.Layout.Default, nodeIx=repcap.NodeIx.Default) -> None:
		"""LAYout<*>:NODE<*>:STYPe \n
		Snippet: driver.layout.node.stype.set(split_type = enums.LayoutSplitType.BODE, layout = repcap.Layout.Default, nodeIx = repcap.NodeIx.Default) \n
		Creates a second child (e.g. diagram) in the node if only one child exists, and sets the splitting of the node. If two
		children exist, only the splitting is set. \n
			:param split_type: HOR = HORizontal, VERT = VERTical
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param nodeIx: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Node')
		"""
		param = Conversions.enum_scalar_to_str(split_type, enums.LayoutSplitType)
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		nodeIx_cmd_val = self._cmd_group.get_repcap_cmd_value(nodeIx, repcap.NodeIx)
		self._core.io.write(f'LAYout{layout_cmd_val}:NODE{nodeIx_cmd_val}:STYPe {param}')

	# noinspection PyTypeChecker
	def get(self, layout=repcap.Layout.Default, nodeIx=repcap.NodeIx.Default) -> enums.LayoutSplitType:
		"""LAYout<*>:NODE<*>:STYPe \n
		Snippet: value: enums.LayoutSplitType = driver.layout.node.stype.get(layout = repcap.Layout.Default, nodeIx = repcap.NodeIx.Default) \n
		Creates a second child (e.g. diagram) in the node if only one child exists, and sets the splitting of the node. If two
		children exist, only the splitting is set. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param nodeIx: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Node')
			:return: split_type: HOR = HORizontal, VERT = VERTical"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		nodeIx_cmd_val = self._cmd_group.get_repcap_cmd_value(nodeIx, repcap.NodeIx)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:NODE{nodeIx_cmd_val}:STYPe?')
		return Conversions.str_to_scalar_enum(response, enums.LayoutSplitType)
