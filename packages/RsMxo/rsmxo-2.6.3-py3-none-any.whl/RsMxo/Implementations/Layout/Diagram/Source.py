from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SourceCls:
	"""Source commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("source", core, parent)

	def set(self, signal_keys: str, layout=repcap.Layout.Default, diagram=repcap.Diagram.Default) -> None:
		"""LAYout<l>:DIAGram<da>:SOURce \n
		Snippet: driver.layout.diagram.source.set(signal_keys = 'abc', layout = repcap.Layout.Default, diagram = repcap.Diagram.Default) \n
		Assigns the waveforms to a diagram. \n
			:param signal_keys: String with a comma-separated list of waveforms, e.g. 'C1, C2, M1'
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param diagram: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Diagram')
		"""
		param = Conversions.value_to_quoted_str(signal_keys)
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		diagram_cmd_val = self._cmd_group.get_repcap_cmd_value(diagram, repcap.Diagram)
		self._core.io.write(f'LAYout{layout_cmd_val}:DIAGram{diagram_cmd_val}:SOURce {param}')
