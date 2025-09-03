from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EdgeCls:
	"""Edge commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("edge", core, parent)

	def set(self, edge: enums.PulseSlope, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:EDGE \n
		Snippet: driver.treference.edge.set(edge = enums.PulseSlope.EITHer, timingReference = repcap.TimingReference.Default) \n
		Sets the clock edges that are used for measurements if method RsMxo.Treference.TypePy.set is set for the indicated
		measurement. Sets the data edges for clock data recovery if method RsMxo.Treference.TypePy.set is set for the indicated
		measurement. \n
			:param edge:
				- POSitive: The positive clock slope can be used, for example, for single data rate (SDR) signals with bit start at the positive clock edge.
				- NEGative: The negative clock slope can be used, for example, for SDR signals with bit start at the negative clock edge.
				- EITHer: Can be used for double data rate (DDR) signals and clock edges. For data edges, it is the most common setting.
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface
			'Treference')"""
		param = Conversions.enum_scalar_to_str(edge, enums.PulseSlope)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:EDGE {param}')

	# noinspection PyTypeChecker
	def get(self, timingReference=repcap.TimingReference.Default) -> enums.PulseSlope:
		"""TREFerence<*>:EDGE \n
		Snippet: value: enums.PulseSlope = driver.treference.edge.get(timingReference = repcap.TimingReference.Default) \n
		Sets the clock edges that are used for measurements if method RsMxo.Treference.TypePy.set is set for the indicated
		measurement. Sets the data edges for clock data recovery if method RsMxo.Treference.TypePy.set is set for the indicated
		measurement. \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: edge:
				- POSitive: The positive clock slope can be used, for example, for single data rate (SDR) signals with bit start at the positive clock edge.
				- NEGative: The negative clock slope can be used, for example, for SDR signals with bit start at the negative clock edge.
				- EITHer: Can be used for double data rate (DDR) signals and clock edges. For data edges, it is the most common setting."""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:EDGE?')
		return Conversions.str_to_scalar_enum(response, enums.PulseSlope)
