from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PositionCls:
	"""Position commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("position", core, parent)

	def set(self, vert_posi: float, refCurve=repcap.RefCurve.Default) -> None:
		"""REFCurve<*>:POSition \n
		Snippet: driver.refCurve.position.set(vert_posi = 1.0, refCurve = repcap.RefCurve.Default) \n
		Available, if method RsMxo.RefCurve.Vmode.set is set to INDependent. Moves the reference waveform up or down in the
		diagram. \n
			:param vert_posi: No help available
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
		"""
		param = Conversions.decimal_value_to_str(vert_posi)
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		self._core.io.write(f'REFCurve{refCurve_cmd_val}:POSition {param}')

	def get(self, refCurve=repcap.RefCurve.Default) -> float:
		"""REFCurve<*>:POSition \n
		Snippet: value: float = driver.refCurve.position.get(refCurve = repcap.RefCurve.Default) \n
		Available, if method RsMxo.RefCurve.Vmode.set is set to INDependent. Moves the reference waveform up or down in the
		diagram. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
			:return: vert_posi: No help available"""
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		response = self._core.io.query_str(f'REFCurve{refCurve_cmd_val}:POSition?')
		return Conversions.str_to_float(response)
