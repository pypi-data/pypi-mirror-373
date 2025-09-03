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

	def set(self, dig_sign_height_rel: float, pwrBus=repcap.PwrBus.Default) -> None:
		"""PBUS<*>:DIGSignals:SCALe \n
		Snippet: driver.pbus.digSignals.scale.set(dig_sign_height_rel = 1.0, pwrBus = repcap.PwrBus.Default) \n
		Sets the size of the display that is used by each active digital signal. \n
			:param dig_sign_height_rel: No help available
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
		"""
		param = Conversions.decimal_value_to_str(dig_sign_height_rel)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:DIGSignals:SCALe {param}')

	def get(self, pwrBus=repcap.PwrBus.Default) -> float:
		"""PBUS<*>:DIGSignals:SCALe \n
		Snippet: value: float = driver.pbus.digSignals.scale.get(pwrBus = repcap.PwrBus.Default) \n
		Sets the size of the display that is used by each active digital signal. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: dig_sign_height_rel: No help available"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:DIGSignals:SCALe?')
		return Conversions.str_to_float(response)
