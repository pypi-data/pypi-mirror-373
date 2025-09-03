from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ModeCls:
	"""Mode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mode", core, parent)

	def set(self, mode: enums.SbusHbtoMode, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:HBTO:MODE \n
		Snippet: driver.sbus.hbto.mode.set(mode = enums.SbusHbtoMode.AUTO, serialBus = repcap.SerialBus.Default) \n
		Selects the operation mode. \n
			:param mode: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.SbusHbtoMode)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:HBTO:MODE {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SbusHbtoMode:
		"""SBUS<*>:HBTO:MODE \n
		Snippet: value: enums.SbusHbtoMode = driver.sbus.hbto.mode.get(serialBus = repcap.SerialBus.Default) \n
		Selects the operation mode. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: mode: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:HBTO:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.SbusHbtoMode)
