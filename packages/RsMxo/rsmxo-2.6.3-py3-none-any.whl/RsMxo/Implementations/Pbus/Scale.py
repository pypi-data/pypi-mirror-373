from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ScaleCls:
	"""Scale commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("scale", core, parent)

	def set(self, relative_height: float, pwrBus=repcap.PwrBus.Default) -> None:
		"""PBUS<*>:SCALe \n
		Snippet: driver.pbus.scale.set(relative_height = 1.0, pwrBus = repcap.PwrBus.Default) \n
		Sets the size of the display that is used by the indicated logic group waveform. \n
			:param relative_height: No help available
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
		"""
		param = Conversions.decimal_value_to_str(relative_height)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:SCALe {param}')

	def get(self, pwrBus=repcap.PwrBus.Default) -> float:
		"""PBUS<*>:SCALe \n
		Snippet: value: float = driver.pbus.scale.get(pwrBus = repcap.PwrBus.Default) \n
		Sets the size of the display that is used by the indicated logic group waveform. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: relative_height: No help available"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:SCALe?')
		return Conversions.str_to_float(response)
