from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DdrCls:
	"""Ddr commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ddr", core, parent)

	def set(self, ddr: bool, serialBus=repcap.SerialBus.Default, item=repcap.Item.Default) -> None:
		"""SBUS<*>:QSPI:OPCode:ITEM<*>:DDR \n
		Snippet: driver.sbus.qspi.opCode.item.ddr.set(ddr = False, serialBus = repcap.SerialBus.Default, item = repcap.Item.Default) \n
		If enabled, the data is transferred on both the rising and falling edges of the clock signal. This setting effectively
		doubles the data transfer rate compared to a single data rate (SDR) , which transfers data only on one clock edge. \n
			:param ddr: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param item: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Item')
		"""
		param = Conversions.bool_to_str(ddr)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		item_cmd_val = self._cmd_group.get_repcap_cmd_value(item, repcap.Item)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:QSPI:OPCode:ITEM{item_cmd_val}:DDR {param}')

	def get(self, serialBus=repcap.SerialBus.Default, item=repcap.Item.Default) -> bool:
		"""SBUS<*>:QSPI:OPCode:ITEM<*>:DDR \n
		Snippet: value: bool = driver.sbus.qspi.opCode.item.ddr.get(serialBus = repcap.SerialBus.Default, item = repcap.Item.Default) \n
		If enabled, the data is transferred on both the rising and falling edges of the clock signal. This setting effectively
		doubles the data transfer rate compared to a single data rate (SDR) , which transfers data only on one clock edge. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param item: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Item')
			:return: ddr: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		item_cmd_val = self._cmd_group.get_repcap_cmd_value(item, repcap.Item)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:QSPI:OPCode:ITEM{item_cmd_val}:DDR?')
		return Conversions.str_to_bool(response)
