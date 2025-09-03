from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HmodeCls:
	"""Hmode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("hmode", core, parent)

	def set(self, horizontal_mode: enums.HorizontalMode, refCurve=repcap.RefCurve.Default) -> None:
		"""REFCurve<*>:HMODe \n
		Snippet: driver.refCurve.hmode.set(horizontal_mode = enums.HorizontalMode.COUPled, refCurve = repcap.RefCurve.Default) \n
		Selects the coupling of horizontal settings. \n
			:param horizontal_mode:
				- ORIGinal: Horizontal scaling and reference point of the source waveform are used.
				- COUPled: The current horizontal settings of the diagram are used.
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')"""
		param = Conversions.enum_scalar_to_str(horizontal_mode, enums.HorizontalMode)
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		self._core.io.write(f'REFCurve{refCurve_cmd_val}:HMODe {param}')

	# noinspection PyTypeChecker
	def get(self, refCurve=repcap.RefCurve.Default) -> enums.HorizontalMode:
		"""REFCurve<*>:HMODe \n
		Snippet: value: enums.HorizontalMode = driver.refCurve.hmode.get(refCurve = repcap.RefCurve.Default) \n
		Selects the coupling of horizontal settings. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
			:return: horizontal_mode:
				- ORIGinal: Horizontal scaling and reference point of the source waveform are used.
				- COUPled: The current horizontal settings of the diagram are used."""
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		response = self._core.io.query_str(f'REFCurve{refCurve_cmd_val}:HMODe?')
		return Conversions.str_to_scalar_enum(response, enums.HorizontalMode)
