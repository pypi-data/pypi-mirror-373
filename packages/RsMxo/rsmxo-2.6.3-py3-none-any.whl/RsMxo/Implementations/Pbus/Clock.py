from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ClockCls:
	"""Clock commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("clock", core, parent)

	def set(self, clock_source: enums.ClockSource, pwrBus=repcap.PwrBus.Default) -> None:
		"""PBUS<*>:CLOCk \n
		Snippet: driver.pbus.clock.set(clock_source = enums.ClockSource.D0, pwrBus = repcap.PwrBus.Default) \n
		Selects the digital channel used as clock. \n
			:param clock_source: Clock channel
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
		"""
		param = Conversions.enum_scalar_to_str(clock_source, enums.ClockSource)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:CLOCk {param}')

	# noinspection PyTypeChecker
	def get(self, pwrBus=repcap.PwrBus.Default) -> enums.ClockSource:
		"""PBUS<*>:CLOCk \n
		Snippet: value: enums.ClockSource = driver.pbus.clock.get(pwrBus = repcap.PwrBus.Default) \n
		Selects the digital channel used as clock. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: clock_source: Clock channel"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:CLOCk?')
		return Conversions.str_to_scalar_enum(response, enums.ClockSource)
