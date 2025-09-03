from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class UsrLevelCls:
	"""UsrLevel commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("usrLevel", core, parent)

	def set(self, user_level: enums.UserLevel, refLevel=repcap.RefLevel.Default) -> None:
		"""REFLevel<*>:USRLevel \n
		Snippet: driver.refLevel.usrLevel.set(user_level = enums.UserLevel.UREF, refLevel = repcap.RefLevel.Default) \n
		No command help available \n
			:param user_level: No help available
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
		"""
		param = Conversions.enum_scalar_to_str(user_level, enums.UserLevel)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		self._core.io.write(f'REFLevel{refLevel_cmd_val}:USRLevel {param}')

	# noinspection PyTypeChecker
	def get(self, refLevel=repcap.RefLevel.Default) -> enums.UserLevel:
		"""REFLevel<*>:USRLevel \n
		Snippet: value: enums.UserLevel = driver.refLevel.usrLevel.get(refLevel = repcap.RefLevel.Default) \n
		No command help available \n
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: user_level: No help available"""
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'REFLevel{refLevel_cmd_val}:USRLevel?')
		return Conversions.str_to_scalar_enum(response, enums.UserLevel)
