from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ClonCls:
	"""Clon commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("clon", core, parent)

	def set(self, clocked: bool, pwrBus=repcap.PwrBus.Default) -> None:
		"""PBUS<*>:CLON \n
		Snippet: driver.pbus.clon.set(clocked = False, pwrBus = repcap.PwrBus.Default) \n
		Defines if the bus is a clocked bus - one of the digital channels serves as the clock of the bus. \n
			:param clocked: No help available
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
		"""
		param = Conversions.bool_to_str(clocked)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:CLON {param}')

	def get(self, pwrBus=repcap.PwrBus.Default) -> bool:
		"""PBUS<*>:CLON \n
		Snippet: value: bool = driver.pbus.clon.get(pwrBus = repcap.PwrBus.Default) \n
		Defines if the bus is a clocked bus - one of the digital channels serves as the clock of the bus. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: clocked: No help available"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:CLON?')
		return Conversions.str_to_bool(response)
