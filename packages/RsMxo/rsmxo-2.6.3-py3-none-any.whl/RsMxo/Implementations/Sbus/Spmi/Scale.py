from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ScaleCls:
	"""Scale commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("scale", core, parent)

	def set(self, spmi_scale: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SPMI:SCALe \n
		Snippet: driver.sbus.spmi.scale.set(spmi_scale = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets the vertical position of the SPMI signal. \n
			:param spmi_scale: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(spmi_scale)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SPMI:SCALe {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:SPMI:SCALe \n
		Snippet: value: float = driver.sbus.spmi.scale.get(serialBus = repcap.SerialBus.Default) \n
		Sets the vertical position of the SPMI signal. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: spmi_scale: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SPMI:SCALe?')
		return Conversions.str_to_float(response)
