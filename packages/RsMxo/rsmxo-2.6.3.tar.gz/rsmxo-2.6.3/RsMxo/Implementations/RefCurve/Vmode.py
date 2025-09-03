from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class VmodeCls:
	"""Vmode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("vmode", core, parent)

	def set(self, vertical_mode: enums.VerticalMode, refCurve=repcap.RefCurve.Default) -> None:
		"""REFCurve<*>:VMODe \n
		Snippet: driver.refCurve.vmode.set(vertical_mode = enums.VerticalMode.COUPled, refCurve = repcap.RefCurve.Default) \n
		Selects the coupling of vertical settings. \n
			:param vertical_mode:
				- COUPled: Vertical position and scale of the source are used.
				- INDependent: Scaling and position can be set specific to the reference waveform.
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')"""
		param = Conversions.enum_scalar_to_str(vertical_mode, enums.VerticalMode)
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		self._core.io.write(f'REFCurve{refCurve_cmd_val}:VMODe {param}')

	# noinspection PyTypeChecker
	def get(self, refCurve=repcap.RefCurve.Default) -> enums.VerticalMode:
		"""REFCurve<*>:VMODe \n
		Snippet: value: enums.VerticalMode = driver.refCurve.vmode.get(refCurve = repcap.RefCurve.Default) \n
		Selects the coupling of vertical settings. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
			:return: vertical_mode:
				- COUPled: Vertical position and scale of the source are used.
				- INDependent: Scaling and position can be set specific to the reference waveform."""
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		response = self._core.io.query_str(f'REFCurve{refCurve_cmd_val}:VMODe?')
		return Conversions.str_to_scalar_enum(response, enums.VerticalMode)
