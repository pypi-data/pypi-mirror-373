from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class XmodeCls:
	"""Xmode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("xmode", core, parent)

	def set(self, xaxis_mode: enums.AxisMode, refCurve=repcap.RefCurve.Default) -> None:
		"""REFCurve<*>:AXIS[:XMODe] \n
		Snippet: driver.refCurve.axis.xmode.set(xaxis_mode = enums.AxisMode.LIN, refCurve = repcap.RefCurve.Default) \n
		Defines the scaling method for the frequency (x-axis) of the reference curve. \n
			:param xaxis_mode: LIN: Linear scaling LOG: Logarithmic scaling
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
		"""
		param = Conversions.enum_scalar_to_str(xaxis_mode, enums.AxisMode)
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		self._core.io.write(f'REFCurve{refCurve_cmd_val}:AXIS:XMODe {param}')

	# noinspection PyTypeChecker
	def get(self, refCurve=repcap.RefCurve.Default) -> enums.AxisMode:
		"""REFCurve<*>:AXIS[:XMODe] \n
		Snippet: value: enums.AxisMode = driver.refCurve.axis.xmode.get(refCurve = repcap.RefCurve.Default) \n
		Defines the scaling method for the frequency (x-axis) of the reference curve. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
			:return: xaxis_mode: LIN: Linear scaling LOG: Logarithmic scaling"""
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		response = self._core.io.query_str(f'REFCurve{refCurve_cmd_val}:AXIS:XMODe?')
		return Conversions.str_to_scalar_enum(response, enums.AxisMode)
