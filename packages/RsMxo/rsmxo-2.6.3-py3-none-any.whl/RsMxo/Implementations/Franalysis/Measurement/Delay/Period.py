from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PeriodCls:
	"""Period commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("period", core, parent)

	def get_number(self) -> float:
		"""FRANalysis:MEASurement:DELay:PERiod[:NUMBer] \n
		Snippet: value: float = driver.franalysis.measurement.delay.period.get_number() \n
		No command help available \n
			:return: meas_delay_period: No help available
		"""
		response = self._core.io.query_str('FRANalysis:MEASurement:DELay:PERiod:NUMBer?')
		return Conversions.str_to_float(response)

	def set_number(self, meas_delay_period: float) -> None:
		"""FRANalysis:MEASurement:DELay:PERiod[:NUMBer] \n
		Snippet: driver.franalysis.measurement.delay.period.set_number(meas_delay_period = 1.0) \n
		No command help available \n
			:param meas_delay_period: No help available
		"""
		param = Conversions.decimal_value_to_str(meas_delay_period)
		self._core.io.write(f'FRANalysis:MEASurement:DELay:PERiod:NUMBer {param}')
