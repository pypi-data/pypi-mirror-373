from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DtLanesCls:
	"""DtLanes commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dtLanes", core, parent)

	def set(self, data_lanes: enums.SbusQspiInstruction, serialBus=repcap.SerialBus.Default, item=repcap.Item.Default) -> None:
		"""SBUS<*>:QSPI:OPCode:ITEM<*>:DTLanes \n
		Snippet: driver.sbus.qspi.opCode.item.dtLanes.set(data_lanes = enums.SbusQspiInstruction.DUAL, serialBus = repcap.SerialBus.Default, item = repcap.Item.Default) \n
		Selects how many lanes are used for the data transfer. The data lanes refer to the physical connections through which
		data is transmitted between the main (typically a microcontroller) and the sub (typically a flash memory device) .
		QUADSPI can utilize multiple data lines to increase the speed and efficiency of data transfer. \n
			:param data_lanes: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param item: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Item')
		"""
		param = Conversions.enum_scalar_to_str(data_lanes, enums.SbusQspiInstruction)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		item_cmd_val = self._cmd_group.get_repcap_cmd_value(item, repcap.Item)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:QSPI:OPCode:ITEM{item_cmd_val}:DTLanes {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default, item=repcap.Item.Default) -> enums.SbusQspiInstruction:
		"""SBUS<*>:QSPI:OPCode:ITEM<*>:DTLanes \n
		Snippet: value: enums.SbusQspiInstruction = driver.sbus.qspi.opCode.item.dtLanes.get(serialBus = repcap.SerialBus.Default, item = repcap.Item.Default) \n
		Selects how many lanes are used for the data transfer. The data lanes refer to the physical connections through which
		data is transmitted between the main (typically a microcontroller) and the sub (typically a flash memory device) .
		QUADSPI can utilize multiple data lines to increase the speed and efficiency of data transfer. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param item: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Item')
			:return: data_lanes: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		item_cmd_val = self._cmd_group.get_repcap_cmd_value(item, repcap.Item)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:QSPI:OPCode:ITEM{item_cmd_val}:DTLanes?')
		return Conversions.str_to_scalar_enum(response, enums.SbusQspiInstruction)
