from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CrcMethodCls:
	"""CrcMethod commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("crcMethod", core, parent)

	def set(self, crc_calculation: enums.CrcCalculation, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SENT:CRCMethod \n
		Snippet: driver.sbus.sent.crcMethod.set(crc_calculation = enums.CrcCalculation.SAEJ, serialBus = repcap.SerialBus.Default) \n
		Selects the method for CRC calculation. \n
			:param crc_calculation: SAEJ: SAE_J2716 TLE: TLE_4998X
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(crc_calculation, enums.CrcCalculation)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SENT:CRCMethod {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.CrcCalculation:
		"""SBUS<*>:SENT:CRCMethod \n
		Snippet: value: enums.CrcCalculation = driver.sbus.sent.crcMethod.get(serialBus = repcap.SerialBus.Default) \n
		Selects the method for CRC calculation. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: crc_calculation: SAEJ: SAE_J2716 TLE: TLE_4998X"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SENT:CRCMethod?')
		return Conversions.str_to_scalar_enum(response, enums.CrcCalculation)
