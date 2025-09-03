from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RpositionCls:
	"""Rposition commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rposition", core, parent)

	def set(self, result_position: enums.WindowPosition, layout=repcap.Layout.Default) -> None:
		"""LAYout<*>:RPOSition \n
		Snippet: driver.layout.rposition.set(result_position = enums.WindowPosition.BOTT, layout = repcap.Layout.Default) \n
		Defines the position of the result container inside the layout. \n
			:param result_position: No help available
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
		"""
		param = Conversions.enum_scalar_to_str(result_position, enums.WindowPosition)
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		self._core.io.write(f'LAYout{layout_cmd_val}:RPOSition {param}')

	# noinspection PyTypeChecker
	def get(self, layout=repcap.Layout.Default) -> enums.WindowPosition:
		"""LAYout<*>:RPOSition \n
		Snippet: value: enums.WindowPosition = driver.layout.rposition.get(layout = repcap.Layout.Default) \n
		Defines the position of the result container inside the layout. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:return: result_position: No help available"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:RPOSition?')
		return Conversions.str_to_scalar_enum(response, enums.WindowPosition)
