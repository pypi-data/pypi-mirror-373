from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AltCls:
	"""Alt commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("alt", core, parent)

	def set(self, alt: bool, serialBus=repcap.SerialBus.Default, item=repcap.Item.Default) -> None:
		"""SBUS<*>:QSPI:OPCode:ITEM<*>:ALT \n
		Snippet: driver.sbus.qspi.opCode.item.alt.set(alt = False, serialBus = repcap.SerialBus.Default, item = repcap.Item.Default) \n
		Enable, if an alternative field is available. \n
			:param alt: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param item: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Item')
		"""
		param = Conversions.bool_to_str(alt)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		item_cmd_val = self._cmd_group.get_repcap_cmd_value(item, repcap.Item)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:QSPI:OPCode:ITEM{item_cmd_val}:ALT {param}')

	def get(self, serialBus=repcap.SerialBus.Default, item=repcap.Item.Default) -> bool:
		"""SBUS<*>:QSPI:OPCode:ITEM<*>:ALT \n
		Snippet: value: bool = driver.sbus.qspi.opCode.item.alt.get(serialBus = repcap.SerialBus.Default, item = repcap.Item.Default) \n
		Enable, if an alternative field is available. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param item: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Item')
			:return: alt: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		item_cmd_val = self._cmd_group.get_repcap_cmd_value(item, repcap.Item)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:QSPI:OPCode:ITEM{item_cmd_val}:ALT?')
		return Conversions.str_to_bool(response)
