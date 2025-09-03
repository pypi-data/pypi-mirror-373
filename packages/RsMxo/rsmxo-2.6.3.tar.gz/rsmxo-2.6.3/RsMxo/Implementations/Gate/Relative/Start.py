from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StartCls:
	"""Start commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("start", core, parent)

	def set(self, relative_start: float, gate=repcap.Gate.Default) -> None:
		"""GATE<*>:RELative:STARt \n
		Snippet: driver.gate.relative.start.set(relative_start = 1.0, gate = repcap.Gate.Default) \n
		Define the relative start and end values for the gate, respectively. Available, if method RsMxo.Gate.Gcoupling.
		set = MANUal and method RsMxo.Gate.Mode.set =REL. \n
			:param relative_start: No help available
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')
		"""
		param = Conversions.decimal_value_to_str(relative_start)
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		self._core.io.write(f'GATE{gate_cmd_val}:RELative:STARt {param}')

	def get(self, gate=repcap.Gate.Default) -> float:
		"""GATE<*>:RELative:STARt \n
		Snippet: value: float = driver.gate.relative.start.get(gate = repcap.Gate.Default) \n
		Define the relative start and end values for the gate, respectively. Available, if method RsMxo.Gate.Gcoupling.
		set = MANUal and method RsMxo.Gate.Mode.set =REL. \n
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')
			:return: relative_start: No help available"""
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		response = self._core.io.query_str(f'GATE{gate_cmd_val}:RELative:STARt?')
		return Conversions.str_to_float(response)
