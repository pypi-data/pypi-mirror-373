from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NetCls:
	"""Net commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("net", core, parent)

	def get_hostname(self) -> str:
		"""SYSTem:COMMunicate:NET[:HOSTname] \n
		Snippet: value: str = driver.system.communicate.net.get_hostname() \n
		Sets the host name of the instrument, which is required when configuring a network. After changing the host name, you
		have to reboot the instrument. The query SYSTem:COMMunicate:NET:HOSTname? returns the currently defined host name. \n
			:return: hostname: String parameter
		"""
		response = self._core.io.query_str('SYSTem:COMMunicate:NET:HOSTname?')
		return trim_str_response(response)

	def set_hostname(self, hostname: str) -> None:
		"""SYSTem:COMMunicate:NET[:HOSTname] \n
		Snippet: driver.system.communicate.net.set_hostname(hostname = 'abc') \n
		Sets the host name of the instrument, which is required when configuring a network. After changing the host name, you
		have to reboot the instrument. The query SYSTem:COMMunicate:NET:HOSTname? returns the currently defined host name. \n
			:param hostname: String parameter
		"""
		param = Conversions.value_to_quoted_str(hostname)
		self._core.io.write(f'SYSTem:COMMunicate:NET:HOSTname {param}')
