from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FormatPyCls:
	"""FormatPy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("formatPy", core, parent)

	def set(self, data_format: enums.SbusDataFormat, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:FORMat \n
		Snippet: driver.sbus.formatPy.set(data_format = enums.SbusDataFormat.ASCII, serialBus = repcap.SerialBus.Default) \n
		Sets the number format for decoded data values of the indicated serial bus. It defines the format in the decode table,
		and in the combs of the decoded signal on the screen. \n
			:param data_format: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(data_format, enums.SbusDataFormat)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:FORMat {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SbusDataFormat:
		"""SBUS<*>:FORMat \n
		Snippet: value: enums.SbusDataFormat = driver.sbus.formatPy.get(serialBus = repcap.SerialBus.Default) \n
		Sets the number format for decoded data values of the indicated serial bus. It defines the format in the decode table,
		and in the combs of the decoded signal on the screen. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: data_format: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:FORMat?')
		return Conversions.str_to_scalar_enum(response, enums.SbusDataFormat)
