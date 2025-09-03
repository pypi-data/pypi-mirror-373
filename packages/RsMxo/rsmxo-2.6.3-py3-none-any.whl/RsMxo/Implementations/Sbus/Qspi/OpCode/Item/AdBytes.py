from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AdBytesCls:
	"""AdBytes commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("adBytes", core, parent)

	def set(self, address_bytes: int, serialBus=repcap.SerialBus.Default, item=repcap.Item.Default) -> None:
		"""SBUS<*>:QSPI:OPCode:ITEM<*>:ADBYtes \n
		Snippet: driver.sbus.qspi.opCode.item.adBytes.set(address_bytes = 1, serialBus = repcap.SerialBus.Default, item = repcap.Item.Default) \n
		Sets the address byte. It specifies the location in the flash memory where the operation (e.g., read, write) is performed. \n
			:param address_bytes: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param item: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Item')
		"""
		param = Conversions.decimal_value_to_str(address_bytes)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		item_cmd_val = self._cmd_group.get_repcap_cmd_value(item, repcap.Item)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:QSPI:OPCode:ITEM{item_cmd_val}:ADBYtes {param}')

	def get(self, serialBus=repcap.SerialBus.Default, item=repcap.Item.Default) -> int:
		"""SBUS<*>:QSPI:OPCode:ITEM<*>:ADBYtes \n
		Snippet: value: int = driver.sbus.qspi.opCode.item.adBytes.get(serialBus = repcap.SerialBus.Default, item = repcap.Item.Default) \n
		Sets the address byte. It specifies the location in the flash memory where the operation (e.g., read, write) is performed. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param item: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Item')
			:return: address_bytes: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		item_cmd_val = self._cmd_group.get_repcap_cmd_value(item, repcap.Item)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:QSPI:OPCode:ITEM{item_cmd_val}:ADBYtes?')
		return Conversions.str_to_int(response)
