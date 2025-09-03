from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ResultCls:
	"""Result commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("result", core, parent)

	# noinspection PyTypeChecker
	def get_state(self) -> enums.ResultState:
		"""GENerator:ALIGnment:DC:RESult[:STATe] \n
		Snippet: value: enums.ResultState = driver.generator.alignment.dc.result.get_state() \n
		No command help available \n
			:return: state: No help available
		"""
		response = self._core.io.query_str('GENerator:ALIGnment:DC:RESult:STATe?')
		return Conversions.str_to_scalar_enum(response, enums.ResultState)

	def get_date(self) -> str:
		"""GENerator:ALIGnment:DC:RESult:DATE \n
		Snippet: value: str = driver.generator.alignment.dc.result.get_date() \n
		No command help available \n
			:return: date: No help available
		"""
		response = self._core.io.query_str('GENerator:ALIGnment:DC:RESult:DATE?')
		return trim_str_response(response)

	def get_time(self) -> str:
		"""GENerator:ALIGnment:DC:RESult:TIME \n
		Snippet: value: str = driver.generator.alignment.dc.result.get_time() \n
		No command help available \n
			:return: time: No help available
		"""
		response = self._core.io.query_str('GENerator:ALIGnment:DC:RESult:TIME?')
		return trim_str_response(response)
