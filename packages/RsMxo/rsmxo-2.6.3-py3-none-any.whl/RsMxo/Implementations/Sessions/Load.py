from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LoadCls:
	"""Load commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("load", core, parent)

	def set_execute(self, file_path: str) -> None:
		"""SESSion:LOAD[:EXECute] \n
		Snippet: driver.sessions.load.set_execute(file_path = 'abc') \n
		Loads a session file. To reload also user-specific display settings (if included in the session file) , set method RsMxo.
		Sessions.userPref. \n
			:param file_path: String parameter specifying path and filename of the session file.
		"""
		param = Conversions.value_to_quoted_str(file_path)
		self._core.io.write(f'SESSion:LOAD:EXECute {param}')
