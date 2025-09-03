from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PositionCls:
	"""Position commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("position", core, parent)

	def set(self, yposition: float, pwrBus=repcap.PwrBus.Default) -> None:
		"""PBUS<*>:POSition \n
		Snippet: driver.pbus.position.set(yposition = 1.0, pwrBus = repcap.PwrBus.Default) \n
		Sets the position of the indicated logic group waveform. \n
			:param yposition: No help available
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
		"""
		param = Conversions.decimal_value_to_str(yposition)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:POSition {param}')

	def get(self, pwrBus=repcap.PwrBus.Default) -> float:
		"""PBUS<*>:POSition \n
		Snippet: value: float = driver.pbus.position.get(pwrBus = repcap.PwrBus.Default) \n
		Sets the position of the indicated logic group waveform. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: yposition: No help available"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:POSition?')
		return Conversions.str_to_float(response)
