from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OutputCls:
	"""Output commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("output", core, parent)

	def get_enable(self) -> bool:
		"""SENSe[:ROSCillator]:OUTPut[:ENABle] \n
		Snippet: value: bool = driver.sense.roscillator.output.get_enable() \n
		Sends the internal reference clock signal to the Ref Out 10 MHz connector. \n
			:return: ref_output_enable: No help available
		"""
		response = self._core.io.query_str('SENSe:ROSCillator:OUTPut:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, ref_output_enable: bool) -> None:
		"""SENSe[:ROSCillator]:OUTPut[:ENABle] \n
		Snippet: driver.sense.roscillator.output.set_enable(ref_output_enable = False) \n
		Sends the internal reference clock signal to the Ref Out 10 MHz connector. \n
			:param ref_output_enable: No help available
		"""
		param = Conversions.bool_to_str(ref_output_enable)
		self._core.io.write(f'SENSe:ROSCillator:OUTPut:ENABle {param}')
