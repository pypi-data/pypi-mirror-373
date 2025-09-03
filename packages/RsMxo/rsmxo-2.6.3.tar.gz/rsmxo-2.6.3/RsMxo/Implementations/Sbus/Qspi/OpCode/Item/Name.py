from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ......Internal.Utilities import trim_str_response
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NameCls:
	"""Name commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("name", core, parent)

	def set(self, name: str, serialBus=repcap.SerialBus.Default, item=repcap.Item.Default) -> None:
		"""SBUS<*>:QSPI:OPCode:ITEM<*>:NAME \n
		Snippet: driver.sbus.qspi.opCode.item.name.set(name = 'abc', serialBus = repcap.SerialBus.Default, item = repcap.Item.Default) \n
		Sets the name for the Opcode. \n
			:param name: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param item: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Item')
		"""
		param = Conversions.value_to_quoted_str(name)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		item_cmd_val = self._cmd_group.get_repcap_cmd_value(item, repcap.Item)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:QSPI:OPCode:ITEM{item_cmd_val}:NAME {param}')

	def get(self, serialBus=repcap.SerialBus.Default, item=repcap.Item.Default) -> str:
		"""SBUS<*>:QSPI:OPCode:ITEM<*>:NAME \n
		Snippet: value: str = driver.sbus.qspi.opCode.item.name.get(serialBus = repcap.SerialBus.Default, item = repcap.Item.Default) \n
		Sets the name for the Opcode. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param item: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Item')
			:return: name: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		item_cmd_val = self._cmd_group.get_repcap_cmd_value(item, repcap.Item)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:QSPI:OPCode:ITEM{item_cmd_val}:NAME?')
		return trim_str_response(response)
