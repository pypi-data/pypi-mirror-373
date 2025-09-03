from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RatioCls:
	"""Ratio commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ratio", core, parent)

	def set(self, container_split_ratio_horiz: float, layout=repcap.Layout.Default, result=repcap.Result.Default) -> None:
		"""LAYout<*>:RESult<*>:HORizontal:RATio \n
		Snippet: driver.layout.result.horizontal.ratio.set(container_split_ratio_horiz = 1.0, layout = repcap.Layout.Default, result = repcap.Result.Default) \n
		Sets the horizontal ratio between the cursor result table and the measurement result table inside the result display
		container if the results are displayed at the bottom. \n
			:param container_split_ratio_horiz: No help available
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param result: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Result')
		"""
		param = Conversions.decimal_value_to_str(container_split_ratio_horiz)
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		result_cmd_val = self._cmd_group.get_repcap_cmd_value(result, repcap.Result)
		self._core.io.write(f'LAYout{layout_cmd_val}:RESult{result_cmd_val}:HORizontal:RATio {param}')

	def get(self, layout=repcap.Layout.Default, result=repcap.Result.Default) -> float:
		"""LAYout<*>:RESult<*>:HORizontal:RATio \n
		Snippet: value: float = driver.layout.result.horizontal.ratio.get(layout = repcap.Layout.Default, result = repcap.Result.Default) \n
		Sets the horizontal ratio between the cursor result table and the measurement result table inside the result display
		container if the results are displayed at the bottom. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param result: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Result')
			:return: container_split_ratio_horiz: No help available"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		result_cmd_val = self._cmd_group.get_repcap_cmd_value(result, repcap.Result)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:RESult{result_cmd_val}:HORizontal:RATio?')
		return Conversions.str_to_float(response)
