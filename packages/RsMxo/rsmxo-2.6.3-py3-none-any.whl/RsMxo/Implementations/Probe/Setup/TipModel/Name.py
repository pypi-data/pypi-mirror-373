from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NameCls:
	"""Name commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("name", core, parent)

	# noinspection PyTypeChecker
	def get(self, probe=repcap.Probe.Default) -> enums.ProbeTipModel:
		"""PROBe<*>:SETup:TIPModel:NAME \n
		Snippet: value: enums.ProbeTipModel = driver.probe.setup.tipModel.name.get(probe = repcap.Probe.Default) \n
		Returns the name of the tip module that is connected to the R&S RT-ZISO probe at the specified channel. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: probe_tip_model: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:TIPModel:NAME?')
		return Conversions.str_to_scalar_enum(response, enums.ProbeTipModel)
