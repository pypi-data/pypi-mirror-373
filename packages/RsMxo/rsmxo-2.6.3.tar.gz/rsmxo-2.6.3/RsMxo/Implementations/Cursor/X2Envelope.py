from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class X2EnvelopeCls:
	"""X2Envelope commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("x2Envelope", core, parent)

	def set(self, envlp_curve_sel_source_2: enums.EnvelopeCurve, cursor=repcap.Cursor.Default) -> None:
		"""CURSor<*>:X2ENvelope \n
		Snippet: driver.cursor.x2Envelope.set(envlp_curve_sel_source_2 = enums.EnvelopeCurve.BOTH, cursor = repcap.Cursor.Default) \n
		Define which horizontal cursor is positioned to the maximum and which to the minimum envelope values. Prerequisites:
			INTRO_CMD_HELP: Sets the acquisition and average count, which has a double effect: \n
			- method RsMxo.Acquire.typePy is set to ENVElope.
			- method RsMxo.Cursor.Tracking.State.set is set to ON.
			- method RsMxo.Cursor.Function.set is set to PAIRed.  \n
			:param envlp_curve_sel_source_2:
				- MIN: The horizontal cursor is set to the crossing point of the vertical cursor with the minimum waveform envelope.
				- MAX: The horizontal cursor is set to the crossing point of the vertical cursor with the maximum waveform envelope.
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')"""
		param = Conversions.enum_scalar_to_str(envlp_curve_sel_source_2, enums.EnvelopeCurve)
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		self._core.io.write(f'CURSor{cursor_cmd_val}:X2ENvelope {param}')

	# noinspection PyTypeChecker
	def get(self, cursor=repcap.Cursor.Default) -> enums.EnvelopeCurve:
		"""CURSor<*>:X2ENvelope \n
		Snippet: value: enums.EnvelopeCurve = driver.cursor.x2Envelope.get(cursor = repcap.Cursor.Default) \n
		Define which horizontal cursor is positioned to the maximum and which to the minimum envelope values. Prerequisites:
			INTRO_CMD_HELP: Sets the acquisition and average count, which has a double effect: \n
			- method RsMxo.Acquire.typePy is set to ENVElope.
			- method RsMxo.Cursor.Tracking.State.set is set to ON.
			- method RsMxo.Cursor.Function.set is set to PAIRed.  \n
			:param cursor: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cursor')
			:return: envlp_curve_sel_source_2: No help available"""
		cursor_cmd_val = self._cmd_group.get_repcap_cmd_value(cursor, repcap.Cursor)
		response = self._core.io.query_str(f'CURSor{cursor_cmd_val}:X2ENvelope?')
		return Conversions.str_to_scalar_enum(response, enums.EnvelopeCurve)
