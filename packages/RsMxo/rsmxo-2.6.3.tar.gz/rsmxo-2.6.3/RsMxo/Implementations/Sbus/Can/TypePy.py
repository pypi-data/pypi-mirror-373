from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TypePyCls:
	"""TypePy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("typePy", core, parent)

	def set(self, signal_type: enums.SbusCanSignalType, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:CAN:TYPE \n
		Snippet: driver.sbus.can.typePy.set(signal_type = enums.SbusCanSignalType.CANH, serialBus = repcap.SerialBus.Default) \n
		Selects the CAN-High or CAN-Low line. Both lines are required for differential signal transmission used by CAN. \n
			:param signal_type: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(signal_type, enums.SbusCanSignalType)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:CAN:TYPE {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SbusCanSignalType:
		"""SBUS<*>:CAN:TYPE \n
		Snippet: value: enums.SbusCanSignalType = driver.sbus.can.typePy.get(serialBus = repcap.SerialBus.Default) \n
		Selects the CAN-High or CAN-Low line. Both lines are required for differential signal transmission used by CAN. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: signal_type: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:CAN:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.SbusCanSignalType)
