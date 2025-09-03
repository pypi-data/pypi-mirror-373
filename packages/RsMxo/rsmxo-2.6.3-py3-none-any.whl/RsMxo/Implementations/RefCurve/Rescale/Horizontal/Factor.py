from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FactorCls:
	"""Factor commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("factor", core, parent)

	def set(self, scale_factor: float, refCurve=repcap.RefCurve.Default) -> None:
		"""REFCurve<*>:RESCale:HORizontal:FACTor \n
		Snippet: driver.refCurve.rescale.horizontal.factor.set(scale_factor = 1.0, refCurve = repcap.RefCurve.Default) \n
		Sets the horizontal scale factor. A factor greater than 1 stretches the waveform horizontally, a factor lower than 1
		compresses the curve. \n
			:param scale_factor: No help available
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
		"""
		param = Conversions.decimal_value_to_str(scale_factor)
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		self._core.io.write(f'REFCurve{refCurve_cmd_val}:RESCale:HORizontal:FACTor {param}')

	def get(self, refCurve=repcap.RefCurve.Default) -> float:
		"""REFCurve<*>:RESCale:HORizontal:FACTor \n
		Snippet: value: float = driver.refCurve.rescale.horizontal.factor.get(refCurve = repcap.RefCurve.Default) \n
		Sets the horizontal scale factor. A factor greater than 1 stretches the waveform horizontally, a factor lower than 1
		compresses the curve. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
			:return: scale_factor: No help available"""
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		response = self._core.io.query_str(f'REFCurve{refCurve_cmd_val}:RESCale:HORizontal:FACTor?')
		return Conversions.str_to_float(response)
