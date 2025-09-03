from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SkewCls:
	"""Skew commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("skew", core, parent)

	def set(self, skew_offset: float, pwrBus=repcap.PwrBus.Default) -> None:
		"""PBUS<*>:SKEW \n
		Snippet: driver.pbus.skew.set(skew_offset = 1.0, pwrBus = repcap.PwrBus.Default) \n
		Sets a general delay for all digital channels. \n
			:param skew_offset: No help available
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
		"""
		param = Conversions.decimal_value_to_str(skew_offset)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:SKEW {param}')

	def get(self, pwrBus=repcap.PwrBus.Default) -> float:
		"""PBUS<*>:SKEW \n
		Snippet: value: float = driver.pbus.skew.get(pwrBus = repcap.PwrBus.Default) \n
		Sets a general delay for all digital channels. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: skew_offset: No help available"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:SKEW?')
		return Conversions.str_to_float(response)
