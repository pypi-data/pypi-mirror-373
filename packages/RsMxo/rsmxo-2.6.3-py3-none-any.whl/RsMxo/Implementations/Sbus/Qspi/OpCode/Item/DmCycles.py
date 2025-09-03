from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DmCyclesCls:
	"""DmCycles commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dmCycles", core, parent)

	def set(self, dummy_cycles: int, serialBus=repcap.SerialBus.Default, item=repcap.Item.Default) -> None:
		"""SBUS<*>:QSPI:OPCode:ITEM<*>:DMCYcles \n
		Snippet: driver.sbus.qspi.opCode.item.dmCycles.set(dummy_cycles = 1, serialBus = repcap.SerialBus.Default, item = repcap.Item.Default) \n
		Sets the number of dummy cycles. Dummy cycles are clock cycles inserted after the address or other command sequences but
		before data transfer begins. These cycles allow the flash memory device additional time to perform internal operations or
		latch onto the correct data to ensure accurate read or write operations. \n
			:param dummy_cycles: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param item: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Item')
		"""
		param = Conversions.decimal_value_to_str(dummy_cycles)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		item_cmd_val = self._cmd_group.get_repcap_cmd_value(item, repcap.Item)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:QSPI:OPCode:ITEM{item_cmd_val}:DMCYcles {param}')

	def get(self, serialBus=repcap.SerialBus.Default, item=repcap.Item.Default) -> int:
		"""SBUS<*>:QSPI:OPCode:ITEM<*>:DMCYcles \n
		Snippet: value: int = driver.sbus.qspi.opCode.item.dmCycles.get(serialBus = repcap.SerialBus.Default, item = repcap.Item.Default) \n
		Sets the number of dummy cycles. Dummy cycles are clock cycles inserted after the address or other command sequences but
		before data transfer begins. These cycles allow the flash memory device additional time to perform internal operations or
		latch onto the correct data to ensure accurate read or write operations. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param item: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Item')
			:return: dummy_cycles: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		item_cmd_val = self._cmd_group.get_repcap_cmd_value(item, repcap.Item)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:QSPI:OPCode:ITEM{item_cmd_val}:DMCYcles?')
		return Conversions.str_to_int(response)
