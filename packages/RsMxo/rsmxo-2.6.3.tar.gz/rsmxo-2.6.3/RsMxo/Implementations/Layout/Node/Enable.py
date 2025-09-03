from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, state: bool, layout=repcap.Layout.Default, nodeIx=repcap.NodeIx.Default) -> None:
		"""LAYout<*>:NODE<*>[:ENABle] \n
		Snippet: driver.layout.node.enable.set(state = False, layout = repcap.Layout.Default, nodeIx = repcap.NodeIx.Default) \n
		Creates the specified node in the specified layout. OFF deletes the node and its children. The query returns whether the
		specified node exists (1) or not (0) . \n
			:param state: No help available
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param nodeIx: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Node')
		"""
		param = Conversions.bool_to_str(state)
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		nodeIx_cmd_val = self._cmd_group.get_repcap_cmd_value(nodeIx, repcap.NodeIx)
		self._core.io.write(f'LAYout{layout_cmd_val}:NODE{nodeIx_cmd_val}:ENABle {param}')

	def get(self, layout=repcap.Layout.Default, nodeIx=repcap.NodeIx.Default) -> bool:
		"""LAYout<*>:NODE<*>[:ENABle] \n
		Snippet: value: bool = driver.layout.node.enable.get(layout = repcap.Layout.Default, nodeIx = repcap.NodeIx.Default) \n
		Creates the specified node in the specified layout. OFF deletes the node and its children. The query returns whether the
		specified node exists (1) or not (0) . \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param nodeIx: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Node')
			:return: state: No help available"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		nodeIx_cmd_val = self._cmd_group.get_repcap_cmd_value(nodeIx, repcap.NodeIx)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:NODE{nodeIx_cmd_val}:ENABle?')
		return Conversions.str_to_bool(response)
