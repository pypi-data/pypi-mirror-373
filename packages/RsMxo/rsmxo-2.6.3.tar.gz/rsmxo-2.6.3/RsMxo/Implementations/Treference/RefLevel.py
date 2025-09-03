from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RefLevelCls:
	"""RefLevel commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("refLevel", core, parent)

	def set(self, reference_level: enums.ReferenceLevel, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:REFLevel \n
		Snippet: driver.treference.refLevel.set(reference_level = enums.ReferenceLevel.LOWer, timingReference = repcap.TimingReference.Default) \n
		Selects the reference level that is used for the timing reference if the indicated timing reference uses an explicit
		click signal. \n
			:param reference_level: No help available
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
		"""
		param = Conversions.enum_scalar_to_str(reference_level, enums.ReferenceLevel)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:REFLevel {param}')

	# noinspection PyTypeChecker
	def get(self, timingReference=repcap.TimingReference.Default) -> enums.ReferenceLevel:
		"""TREFerence<*>:REFLevel \n
		Snippet: value: enums.ReferenceLevel = driver.treference.refLevel.get(timingReference = repcap.TimingReference.Default) \n
		Selects the reference level that is used for the timing reference if the indicated timing reference uses an explicit
		click signal. \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: reference_level: No help available"""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:REFLevel?')
		return Conversions.str_to_scalar_enum(response, enums.ReferenceLevel)
