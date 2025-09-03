from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnvSelectCls:
	"""EnvSelect commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("envSelect", core, parent)

	def set(self, envelope_curve: enums.EnvelopeCurve, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:ENVSelect \n
		Snippet: driver.measurement.envSelect.set(envelope_curve = enums.EnvelopeCurve.BOTH, measIndex = repcap.MeasIndex.Default) \n
		Relevant only for measurements on envelope waveforms. It selects the envelope to be used for measurement. Prerequisites:
			- method RsMxo.Acquire.typePy is set to ENVElope.  \n
			:param envelope_curve:
				- MIN: Measures on the lower envelope.
				- MAX: Measures on the upper envelope.
				- BOTH: The envelope is ignored, and the waveform is measured as usual.
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')"""
		param = Conversions.enum_scalar_to_str(envelope_curve, enums.EnvelopeCurve)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:ENVSelect {param}')

	# noinspection PyTypeChecker
	def get(self, measIndex=repcap.MeasIndex.Default) -> enums.EnvelopeCurve:
		"""MEASurement<*>:ENVSelect \n
		Snippet: value: enums.EnvelopeCurve = driver.measurement.envSelect.get(measIndex = repcap.MeasIndex.Default) \n
		Relevant only for measurements on envelope waveforms. It selects the envelope to be used for measurement. Prerequisites:
			- method RsMxo.Acquire.typePy is set to ENVElope.  \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: envelope_curve:
				- MIN: Measures on the lower envelope.
				- MAX: Measures on the upper envelope.
				- BOTH: The envelope is ignored, and the waveform is measured as usual."""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:ENVSelect?')
		return Conversions.str_to_scalar_enum(response, enums.EnvelopeCurve)
