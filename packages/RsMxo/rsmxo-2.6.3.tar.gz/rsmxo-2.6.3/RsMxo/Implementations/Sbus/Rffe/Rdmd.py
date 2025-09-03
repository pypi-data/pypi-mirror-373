from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RdmdCls:
	"""Rdmd commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rdmd", core, parent)

	def set(self, read_mode: enums.SbusRffeReadMode, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:RFFE:RDMD \n
		Snippet: driver.sbus.rffe.rdmd.set(read_mode = enums.SbusRffeReadMode.SREAD, serialBus = repcap.SerialBus.Default) \n
		Selects, if the standard or synchronous read mode is used. \n
			:param read_mode: STRD: standard SREAD: synchronous read
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(read_mode, enums.SbusRffeReadMode)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:RFFE:RDMD {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SbusRffeReadMode:
		"""SBUS<*>:RFFE:RDMD \n
		Snippet: value: enums.SbusRffeReadMode = driver.sbus.rffe.rdmd.get(serialBus = repcap.SerialBus.Default) \n
		Selects, if the standard or synchronous read mode is used. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: read_mode: STRD: standard SREAD: synchronous read"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:RFFE:RDMD?')
		return Conversions.str_to_scalar_enum(response, enums.SbusRffeReadMode)
