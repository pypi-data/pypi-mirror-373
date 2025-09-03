from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LabelCls:
	"""Label commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("label", core, parent)

	def set(self, label: str, digital=repcap.Digital.Default) -> None:
		"""DIGital<*>:LABel \n
		Snippet: driver.digital.label.set(label = 'abc', digital = repcap.Digital.Default) \n
		Sets a name for the indicated digital channel. The name is displayed in the diagram. The setting affects only the
		settings of the first MSO bus (Logic1) . You can set the label for all buses with method RsMxo.Pbus.Bit.Label.set \n
			:param label: String containing the channel name
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')
		"""
		param = Conversions.value_to_quoted_str(label)
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		self._core.io.write(f'DIGital{digital_cmd_val}:LABel {param}')

	def get(self, digital=repcap.Digital.Default) -> str:
		"""DIGital<*>:LABel \n
		Snippet: value: str = driver.digital.label.get(digital = repcap.Digital.Default) \n
		Sets a name for the indicated digital channel. The name is displayed in the diagram. The setting affects only the
		settings of the first MSO bus (Logic1) . You can set the label for all buses with method RsMxo.Pbus.Bit.Label.set \n
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')
			:return: label: String containing the channel name"""
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		response = self._core.io.query_str(f'DIGital{digital_cmd_val}:LABel?')
		return trim_str_response(response)
