from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SessionsCls:
	"""Sessions commands group definition. 6 total commands, 2 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sessions", core, parent)

	@property
	def save(self):
		"""save commands group. 0 Sub-classes, 4 commands."""
		if not hasattr(self, '_save'):
			from .Save import SaveCls
			self._save = SaveCls(self._core, self._cmd_group)
		return self._save

	@property
	def load(self):
		"""load commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_load'):
			from .Load import LoadCls
			self._load = LoadCls(self._core, self._cmd_group)
		return self._load

	def get_user_pref(self) -> bool:
		"""SESSion:USERpref \n
		Snippet: value: bool = driver.sessions.get_user_pref() \n
		If ON, the user-specific display settings for the toolbar, waveform colors and diagram presentation are included in the
		session file. The setting affects the saving and the recall actions. \n
			:return: recall_include_user_setting: No help available
		"""
		response = self._core.io.query_str('SESSion:USERpref?')
		return Conversions.str_to_bool(response)

	def set_user_pref(self, recall_include_user_setting: bool) -> None:
		"""SESSion:USERpref \n
		Snippet: driver.sessions.set_user_pref(recall_include_user_setting = False) \n
		If ON, the user-specific display settings for the toolbar, waveform colors and diagram presentation are included in the
		session file. The setting affects the saving and the recall actions. \n
			:param recall_include_user_setting: No help available
		"""
		param = Conversions.bool_to_str(recall_include_user_setting)
		self._core.io.write(f'SESSion:USERpref {param}')

	def clone(self) -> 'SessionsCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SessionsCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
