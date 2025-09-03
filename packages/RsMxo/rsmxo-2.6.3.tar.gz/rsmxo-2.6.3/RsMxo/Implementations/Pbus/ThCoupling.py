from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ThCouplingCls:
	"""ThCoupling commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("thCoupling", core, parent)

	def set(self, level_coupling: bool, pwrBus=repcap.PwrBus.Default) -> None:
		"""PBUS<*>:THCoupling \n
		Snippet: driver.pbus.thCoupling.set(level_coupling = False, pwrBus = repcap.PwrBus.Default) \n
		Sets the threshold and the hysteresis for all digital channels and all buses to the same value. For Logic 1, the command
		method RsMxo.Digital.ThCoupling.set has the same effect. \n
			:param level_coupling: No help available
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
		"""
		param = Conversions.bool_to_str(level_coupling)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:THCoupling {param}')

	def get(self, pwrBus=repcap.PwrBus.Default) -> bool:
		"""PBUS<*>:THCoupling \n
		Snippet: value: bool = driver.pbus.thCoupling.get(pwrBus = repcap.PwrBus.Default) \n
		Sets the threshold and the hysteresis for all digital channels and all buses to the same value. For Logic 1, the command
		method RsMxo.Digital.ThCoupling.set has the same effect. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: level_coupling: No help available"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:THCoupling?')
		return Conversions.str_to_bool(response)
