from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AlgorithmCls:
	"""Algorithm commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("algorithm", core, parent)

	def set(self, algorithm: enums.Algorithm, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:CDR:SOFTware:ALGorithm \n
		Snippet: driver.treference.cdr.software.algorithm.set(algorithm = enums.Algorithm.CFRequency, timingReference = repcap.TimingReference.Default) \n
		Sets the software algorithm that is used for software clock data recovery. \n
			:param algorithm: CFRequency: constant frequency PLL: phase-locked loop control system FF: feed forward PLLRlock: PLL which is locked at the acquisition start. FFSTart: feed forward algorithm locked at the acquisition start.
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
		"""
		param = Conversions.enum_scalar_to_str(algorithm, enums.Algorithm)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:CDR:SOFTware:ALGorithm {param}')

	# noinspection PyTypeChecker
	def get(self, timingReference=repcap.TimingReference.Default) -> enums.Algorithm:
		"""TREFerence<*>:CDR:SOFTware:ALGorithm \n
		Snippet: value: enums.Algorithm = driver.treference.cdr.software.algorithm.get(timingReference = repcap.TimingReference.Default) \n
		Sets the software algorithm that is used for software clock data recovery. \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: algorithm: CFRequency: constant frequency PLL: phase-locked loop control system FF: feed forward PLLRlock: PLL which is locked at the acquisition start. FFSTart: feed forward algorithm locked at the acquisition start."""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:CDR:SOFTware:ALGorithm?')
		return Conversions.str_to_scalar_enum(response, enums.Algorithm)
