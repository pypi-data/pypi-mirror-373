from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LabelCls:
	"""Label commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("label", core, parent)

	def set(self, label: str, layout=repcap.Layout.Default, diagram=repcap.Diagram.Default) -> None:
		"""LAYout<*>:DIAGram<*>:LABel \n
		Snippet: driver.layout.diagram.label.set(label = 'abc', layout = repcap.Layout.Default, diagram = repcap.Diagram.Default) \n
		Defines a name for the specified diagram in a specified layout. \n
			:param label: String with the diagram name
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param diagram: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Diagram')
		"""
		param = Conversions.value_to_quoted_str(label)
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		diagram_cmd_val = self._cmd_group.get_repcap_cmd_value(diagram, repcap.Diagram)
		self._core.io.write(f'LAYout{layout_cmd_val}:DIAGram{diagram_cmd_val}:LABel {param}')

	def get(self, layout=repcap.Layout.Default, diagram=repcap.Diagram.Default) -> str:
		"""LAYout<*>:DIAGram<*>:LABel \n
		Snippet: value: str = driver.layout.diagram.label.get(layout = repcap.Layout.Default, diagram = repcap.Diagram.Default) \n
		Defines a name for the specified diagram in a specified layout. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param diagram: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Diagram')
			:return: label: String with the diagram name"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		diagram_cmd_val = self._cmd_group.get_repcap_cmd_value(diagram, repcap.Diagram)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:DIAGram{diagram_cmd_val}:LABel?')
		return trim_str_response(response)
