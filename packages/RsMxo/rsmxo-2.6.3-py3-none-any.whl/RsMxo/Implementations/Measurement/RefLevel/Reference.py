from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ReferenceCls:
	"""Reference commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("reference", core, parent)

	def set(self, ref_levs: float, measIndex=repcap.MeasIndex.Default, refLevel=repcap.RefLevel.Default) -> None:
		"""MEASurement<*>:REFLevel<*>:REFerence \n
		Snippet: driver.measurement.refLevel.reference.set(ref_levs = 1.0, measIndex = repcap.MeasIndex.Default, refLevel = repcap.RefLevel.Default) \n
		Selects the set of reference levels that is used for the measurement and for the indicated measurement source.
		Each source of the measurement can have its own reference level set. \n
			:param ref_levs: Number of the reference level set. Define the reference level set before you use it.
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
		"""
		param = Conversions.decimal_value_to_str(ref_levs)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:REFLevel{refLevel_cmd_val}:REFerence {param}')

	def get(self, measIndex=repcap.MeasIndex.Default, refLevel=repcap.RefLevel.Default) -> float:
		"""MEASurement<*>:REFLevel<*>:REFerence \n
		Snippet: value: float = driver.measurement.refLevel.reference.get(measIndex = repcap.MeasIndex.Default, refLevel = repcap.RefLevel.Default) \n
		Selects the set of reference levels that is used for the measurement and for the indicated measurement source.
		Each source of the measurement can have its own reference level set. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: ref_levs: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:REFLevel{refLevel_cmd_val}:REFerence?')
		return Conversions.str_to_float(response)
