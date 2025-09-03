from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ExpressionCls:
	"""Expression commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("expression", core, parent)

	def get_define(self) -> str:
		"""TRIGger:ZONE:EXPRession[:DEFine] \n
		Snippet: value: str = driver.trigger.zone.expression.get_define() \n
		Defines the zone trigger. The available operators for the combination between the zones are AND | NOT | OR | XOR. \n
			:return: zn_trig_logi_expr: No help available
		"""
		response = self._core.io.query_str('TRIGger:ZONE:EXPRession:DEFine?')
		return trim_str_response(response)

	def set_define(self, zn_trig_logi_expr: str) -> None:
		"""TRIGger:ZONE:EXPRession[:DEFine] \n
		Snippet: driver.trigger.zone.expression.set_define(zn_trig_logi_expr = 'abc') \n
		Defines the zone trigger. The available operators for the combination between the zones are AND | NOT | OR | XOR. \n
			:param zn_trig_logi_expr: String with the logical expression
		"""
		param = Conversions.value_to_quoted_str(zn_trig_logi_expr)
		self._core.io.write(f'TRIGger:ZONE:EXPRession:DEFine {param}')
