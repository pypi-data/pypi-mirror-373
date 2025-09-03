from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CrcVersionCls:
	"""CrcVersion commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("crcVersion", core, parent)

	def set(self, crc_version: enums.CrcVersion, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SENT:CRCVersion \n
		Snippet: driver.sbus.sent.crcVersion.set(crc_version = enums.CrcVersion.LEGA, serialBus = repcap.SerialBus.Default) \n
		Selects the version the CRC check is based on. \n
			:param crc_version: LEGA: Legacy V2010: v2010/v2016
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(crc_version, enums.CrcVersion)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SENT:CRCVersion {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.CrcVersion:
		"""SBUS<*>:SENT:CRCVersion \n
		Snippet: value: enums.CrcVersion = driver.sbus.sent.crcVersion.get(serialBus = repcap.SerialBus.Default) \n
		Selects the version the CRC check is based on. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: crc_version: LEGA: Legacy V2010: v2010/v2016"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SENT:CRCVersion?')
		return Conversions.str_to_scalar_enum(response, enums.CrcVersion)
