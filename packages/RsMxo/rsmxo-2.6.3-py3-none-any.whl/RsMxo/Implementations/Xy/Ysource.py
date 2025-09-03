from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class YsourceCls:
	"""Ysource commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ysource", core, parent)

	def set(self, ysource: enums.Source, xyAxis=repcap.XyAxis.Default) -> None:
		"""XY<*>:YSOurce \n
		Snippet: driver.xy.ysource.set(ysource = enums.Source.C1, xyAxis = repcap.XyAxis.Default) \n
		Defines the signal source that supplies the y-values of the XY-diagram. \n
			:param ysource: No help available
			:param xyAxis: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Xy')
		"""
		param = Conversions.enum_scalar_to_str(ysource, enums.Source)
		xyAxis_cmd_val = self._cmd_group.get_repcap_cmd_value(xyAxis, repcap.XyAxis)
		self._core.io.write(f'XY{xyAxis_cmd_val}:YSOurce {param}')

	# noinspection PyTypeChecker
	def get(self, xyAxis=repcap.XyAxis.Default) -> enums.Source:
		"""XY<*>:YSOurce \n
		Snippet: value: enums.Source = driver.xy.ysource.get(xyAxis = repcap.XyAxis.Default) \n
		Defines the signal source that supplies the y-values of the XY-diagram. \n
			:param xyAxis: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Xy')
			:return: ysource: No help available"""
		xyAxis_cmd_val = self._cmd_group.get_repcap_cmd_value(xyAxis, repcap.XyAxis)
		response = self._core.io.query_str(f'XY{xyAxis_cmd_val}:YSOurce?')
		return Conversions.str_to_scalar_enum(response, enums.Source)
