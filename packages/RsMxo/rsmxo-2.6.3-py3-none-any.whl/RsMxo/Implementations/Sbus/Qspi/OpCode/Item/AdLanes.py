from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AdLanesCls:
	"""AdLanes commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("adLanes", core, parent)

	def set(self, address_lanes: enums.SbusQspiInstruction, serialBus=repcap.SerialBus.Default, item=repcap.Item.Default) -> None:
		"""SBUS<*>:QSPI:OPCode:ITEM<*>:ADLanes \n
		Snippet: driver.sbus.qspi.opCode.item.adLanes.set(address_lanes = enums.SbusQspiInstruction.DUAL, serialBus = repcap.SerialBus.Default, item = repcap.Item.Default) \n
		Selects how many lines or lanes are used to send the address bytes to the flash memory. \n
			:param address_lanes: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param item: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Item')
		"""
		param = Conversions.enum_scalar_to_str(address_lanes, enums.SbusQspiInstruction)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		item_cmd_val = self._cmd_group.get_repcap_cmd_value(item, repcap.Item)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:QSPI:OPCode:ITEM{item_cmd_val}:ADLanes {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, item=repcap.Item.Default) -> enums.SbusQspiInstruction:
		"""SBUS<*>:QSPI:OPCode:ITEM<*>:ADLanes \n
		Snippet: value: enums.SbusQspiInstruction = driver.sbus.qspi.opCode.item.adLanes.get(serialBus = repcap.SerialBus.Default, item = repcap.Item.Default) \n
		Selects how many lines or lanes are used to send the address bytes to the flash memory. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param item: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Item')
			:return: address_lanes: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		item_cmd_val = self._cmd_group.get_repcap_cmd_value(item, repcap.Item)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:QSPI:OPCode:ITEM{item_cmd_val}:ADLanes?')
		return Conversions.str_to_scalar_enum(response, enums.SbusQspiInstruction)
