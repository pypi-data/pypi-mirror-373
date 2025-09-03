from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StandardCls:
	"""Standard commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("standard", core, parent)

	def set(self, standard: enums.SBusLinStandard, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:LIN:STANdard \n
		Snippet: driver.sbus.lin.standard.set(standard = enums.SBusLinStandard.AUTO, serialBus = repcap.SerialBus.Default) \n
		Selects the version of the LIN standard. \n
			:param standard: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(standard, enums.SBusLinStandard)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:LIN:STANdard {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SBusLinStandard:
		"""SBUS<*>:LIN:STANdard \n
		Snippet: value: enums.SBusLinStandard = driver.sbus.lin.standard.get(serialBus = repcap.SerialBus.Default) \n
		Selects the version of the LIN standard. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: standard: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:LIN:STANdard?')
		return Conversions.str_to_scalar_enum(response, enums.SBusLinStandard)
