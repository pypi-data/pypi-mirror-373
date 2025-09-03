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

	def set(self, label: str, pwrBus=repcap.PwrBus.Default, bit=repcap.Bit.Default) -> None:
		"""PBUS<*>:BIT<*>:LABel \n
		Snippet: driver.pbus.bit.label.set(label = 'abc', pwrBus = repcap.PwrBus.Default, bit = repcap.Bit.Default) \n
		Sets a name for the indicated digital channel. The name is displayed in the diagram. \n
			:param label: String containing the channel name
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:param bit: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Bit')
		"""
		param = Conversions.value_to_quoted_str(label)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		bit_cmd_val = self._cmd_group.get_repcap_cmd_value(bit, repcap.Bit)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:BIT{bit_cmd_val}:LABel {param}')

	def get(self, pwrBus=repcap.PwrBus.Default, bit=repcap.Bit.Default) -> str:
		"""PBUS<*>:BIT<*>:LABel \n
		Snippet: value: str = driver.pbus.bit.label.get(pwrBus = repcap.PwrBus.Default, bit = repcap.Bit.Default) \n
		Sets a name for the indicated digital channel. The name is displayed in the diagram. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:param bit: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Bit')
			:return: label: String containing the channel name"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		bit_cmd_val = self._cmd_group.get_repcap_cmd_value(bit, repcap.Bit)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:BIT{bit_cmd_val}:LABel?')
		return trim_str_response(response)
