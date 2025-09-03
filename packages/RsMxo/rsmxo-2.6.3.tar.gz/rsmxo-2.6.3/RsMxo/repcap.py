from enum import Enum
# noinspection PyPep8Naming
from .Internal.RepeatedCapability import VALUE_DEFAULT as DefaultRepCap
# noinspection PyPep8Naming
from .Internal.RepeatedCapability import VALUE_EMPTY as EmptyRepCap
# noinspection PyPep8Naming,PyUnresolvedReferences
from .Internal.RepeatedCapability import VALUE_SKIP_HEADER as SkipHeaderRepCap


# noinspection SpellCheckingInspection
class Annotation(Enum):
	"""Repeated capability Annotation"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Ix1 = 1
	Ix2 = 2
	Ix3 = 3
	Ix4 = 4
	Ix5 = 5
	Ix6 = 6
	Ix7 = 7
	Ix8 = 8
	Ix9 = 9
	Ix10 = 10
	Ix11 = 11
	Ix12 = 12
	Ix13 = 13
	Ix14 = 14
	Ix15 = 15
	Ix16 = 16


# noinspection SpellCheckingInspection
class Area(Enum):
	"""Repeated capability Area"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8


# noinspection SpellCheckingInspection
class Bit(Enum):
	"""Repeated capability Bit"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr0 = 0
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12
	Nr13 = 13
	Nr14 = 14
	Nr15 = 15


# noinspection SpellCheckingInspection
class Channel(Enum):
	"""Repeated capability Channel"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Ch1 = 1
	Ch2 = 2
	Ch3 = 3
	Ch4 = 4
	Ch5 = 5
	Ch6 = 6
	Ch7 = 7
	Ch8 = 8


# noinspection SpellCheckingInspection
class ChannelDigital(Enum):
	"""Repeated capability ChannelDigital"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	DigCh1 = 1
	DigCh2 = 2
	DigCh3 = 3
	DigCh4 = 4
	DigCh5 = 5
	DigCh6 = 6
	DigCh7 = 7
	DigCh8 = 8
	DigCh9 = 9
	DigCh10 = 10
	DigCh11 = 11
	DigCh12 = 12
	DigCh13 = 13
	DigCh14 = 14
	DigCh15 = 15
	DigCh16 = 16


# noinspection SpellCheckingInspection
class Children(Enum):
	"""Repeated capability Children"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2


# noinspection SpellCheckingInspection
class Cursor(Enum):
	"""Repeated capability Cursor"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4


# noinspection SpellCheckingInspection
class Delay(Enum):
	"""Repeated capability Delay"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2


# noinspection SpellCheckingInspection
class Device(Enum):
	"""Repeated capability Device"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10


# noinspection SpellCheckingInspection
class Diagram(Enum):
	"""Repeated capability Diagram"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8


# noinspection SpellCheckingInspection
class Digital(Enum):
	"""Repeated capability Digital"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr0 = 0
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12
	Nr13 = 13
	Nr14 = 14
	Nr15 = 15


# noinspection SpellCheckingInspection
class DtoTrigger(Enum):
	"""Repeated capability DtoTrigger"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2


# noinspection SpellCheckingInspection
class Error(Enum):
	"""Repeated capability Error"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Ix1 = 1
	Ix2 = 2
	Ix3 = 3
	Ix4 = 4
	Ix5 = 5
	Ix6 = 6
	Ix7 = 7
	Ix8 = 8
	Ix9 = 9
	Ix10 = 10
	Ix11 = 11
	Ix12 = 12
	Ix13 = 13
	Ix14 = 14
	Ix15 = 15
	Ix16 = 16
	Ix17 = 17
	Ix18 = 18
	Ix19 = 19
	Ix20 = 20
	Ix21 = 21
	Ix22 = 22
	Ix23 = 23
	Ix24 = 24
	Ix25 = 25
	Ix26 = 26
	Ix27 = 27
	Ix28 = 28
	Ix29 = 29
	Ix30 = 30
	Ix31 = 31
	Ix32 = 32


# noinspection SpellCheckingInspection
class Evnt(Enum):
	"""Repeated capability Evnt"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3


# noinspection SpellCheckingInspection
class Field(Enum):
	"""Repeated capability Field"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Ix1 = 1
	Ix2 = 2
	Ix3 = 3
	Ix4 = 4
	Ix5 = 5
	Ix6 = 6
	Ix7 = 7
	Ix8 = 8
	Ix9 = 9
	Ix10 = 10
	Ix11 = 11
	Ix12 = 12
	Ix13 = 13
	Ix14 = 14
	Ix15 = 15
	Ix16 = 16
	Ix17 = 17
	Ix18 = 18
	Ix19 = 19
	Ix20 = 20
	Ix21 = 21
	Ix22 = 22
	Ix23 = 23
	Ix24 = 24
	Ix25 = 25
	Ix26 = 26
	Ix27 = 27
	Ix28 = 28
	Ix29 = 29
	Ix30 = 30
	Ix31 = 31
	Ix32 = 32


# noinspection SpellCheckingInspection
class FieldData(Enum):
	"""Repeated capability FieldData"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Ix1 = 1
	Ix2 = 2
	Ix3 = 3
	Ix4 = 4
	Ix5 = 5
	Ix6 = 6
	Ix7 = 7
	Ix8 = 8
	Ix9 = 9
	Ix10 = 10
	Ix11 = 11
	Ix12 = 12
	Ix13 = 13
	Ix14 = 14
	Ix15 = 15
	Ix16 = 16
	Ix17 = 17
	Ix18 = 18
	Ix19 = 19
	Ix20 = 20
	Ix21 = 21
	Ix22 = 22
	Ix23 = 23
	Ix24 = 24
	Ix25 = 25
	Ix26 = 26
	Ix27 = 27
	Ix28 = 28
	Ix29 = 29
	Ix30 = 30
	Ix31 = 31
	Ix32 = 32


# noinspection SpellCheckingInspection
class Frame(Enum):
	"""Repeated capability Frame"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Ix1 = 1
	Ix2 = 2
	Ix3 = 3
	Ix4 = 4
	Ix5 = 5
	Ix6 = 6
	Ix7 = 7
	Ix8 = 8
	Ix9 = 9
	Ix10 = 10
	Ix11 = 11
	Ix12 = 12
	Ix13 = 13
	Ix14 = 14
	Ix15 = 15
	Ix16 = 16
	Ix17 = 17
	Ix18 = 18
	Ix19 = 19
	Ix20 = 20
	Ix21 = 21
	Ix22 = 22
	Ix23 = 23
	Ix24 = 24
	Ix25 = 25
	Ix26 = 26
	Ix27 = 27
	Ix28 = 28
	Ix29 = 29
	Ix30 = 30
	Ix31 = 31
	Ix32 = 32


# noinspection SpellCheckingInspection
class Gate(Enum):
	"""Repeated capability Gate"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8


# noinspection SpellCheckingInspection
class Horizontal(Enum):
	"""Repeated capability Horizontal"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2


# noinspection SpellCheckingInspection
class Hyst(Enum):
	"""Repeated capability Hyst"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4


# noinspection SpellCheckingInspection
class Item(Enum):
	"""Repeated capability Item"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Ix1 = 1
	Ix2 = 2
	Ix3 = 3
	Ix4 = 4
	Ix5 = 5
	Ix6 = 6
	Ix7 = 7
	Ix8 = 8
	Ix9 = 9
	Ix10 = 10
	Ix11 = 11
	Ix12 = 12
	Ix13 = 13
	Ix14 = 14
	Ix15 = 15
	Ix16 = 16


# noinspection SpellCheckingInspection
class Layout(Enum):
	"""Repeated capability Layout"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12
	Nr13 = 13
	Nr14 = 14
	Nr15 = 15
	Nr16 = 16


# noinspection SpellCheckingInspection
class Logic(Enum):
	"""Repeated capability Logic"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4


# noinspection SpellCheckingInspection
class Lvl(Enum):
	"""Repeated capability Lvl"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8


# noinspection SpellCheckingInspection
class Marker(Enum):
	"""Repeated capability Marker"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2


# noinspection SpellCheckingInspection
class MaskTest(Enum):
	"""Repeated capability MaskTest"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12
	Nr13 = 13
	Nr14 = 14
	Nr15 = 15
	Nr16 = 16
	Nr17 = 17
	Nr18 = 18
	Nr19 = 19
	Nr20 = 20
	Nr21 = 21
	Nr22 = 22
	Nr23 = 23
	Nr24 = 24
	Nr25 = 25
	Nr26 = 26
	Nr27 = 27
	Nr28 = 28
	Nr29 = 29
	Nr30 = 30
	Nr31 = 31
	Nr32 = 32


# noinspection SpellCheckingInspection
class Math(Enum):
	"""Repeated capability Math"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8


# noinspection SpellCheckingInspection
class MeasIndex(Enum):
	"""Repeated capability MeasIndex"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12
	Nr13 = 13
	Nr14 = 14
	Nr15 = 15
	Nr16 = 16
	Nr17 = 17
	Nr18 = 18
	Nr19 = 19
	Nr20 = 20
	Nr21 = 21
	Nr22 = 22
	Nr23 = 23
	Nr24 = 24


# noinspection SpellCheckingInspection
class NodeIx(Enum):
	"""Repeated capability NodeIx"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12
	Nr13 = 13
	Nr14 = 14
	Nr15 = 15
	Nr16 = 16
	Nr17 = 17
	Nr18 = 18
	Nr19 = 19
	Nr20 = 20
	Nr21 = 21
	Nr22 = 22
	Nr23 = 23
	Nr24 = 24
	Nr25 = 25
	Nr26 = 26
	Nr27 = 27
	Nr28 = 28
	Nr29 = 29
	Nr30 = 30
	Nr31 = 31
	Nr32 = 32


# noinspection SpellCheckingInspection
class Noise(Enum):
	"""Repeated capability Noise"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8


# noinspection SpellCheckingInspection
class Output(Enum):
	"""Repeated capability Output"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12
	Nr13 = 13
	Nr14 = 14
	Nr15 = 15
	Nr16 = 16
	Nr17 = 17
	Nr18 = 18
	Nr19 = 19
	Nr20 = 20
	Nr21 = 21
	Nr22 = 22
	Nr23 = 23
	Nr24 = 24
	Nr25 = 25
	Nr26 = 26
	Nr27 = 27
	Nr28 = 28
	Nr29 = 29
	Nr30 = 30
	Nr31 = 31
	Nr32 = 32


# noinspection SpellCheckingInspection
class Point(Enum):
	"""Repeated capability Point"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12
	Nr13 = 13
	Nr14 = 14
	Nr15 = 15
	Nr16 = 16


# noinspection SpellCheckingInspection
class Power(Enum):
	"""Repeated capability Power"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6


# noinspection SpellCheckingInspection
class Probe(Enum):
	"""Repeated capability Probe"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8


# noinspection SpellCheckingInspection
class ProbeDigital(Enum):
	"""Repeated capability ProbeDigital"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2


# noinspection SpellCheckingInspection
class PwrBus(Enum):
	"""Repeated capability PwrBus"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4


# noinspection SpellCheckingInspection
class RefCurve(Enum):
	"""Repeated capability RefCurve"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8


# noinspection SpellCheckingInspection
class RefLevel(Enum):
	"""Repeated capability RefLevel"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2


# noinspection SpellCheckingInspection
class Result(Enum):
	"""Repeated capability Result"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12
	Nr13 = 13
	Nr14 = 14
	Nr15 = 15
	Nr16 = 16


# noinspection SpellCheckingInspection
class Segment(Enum):
	"""Repeated capability Segment"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12
	Nr13 = 13
	Nr14 = 14
	Nr15 = 15
	Nr16 = 16
	Nr17 = 17
	Nr18 = 18
	Nr19 = 19
	Nr20 = 20
	Nr21 = 21
	Nr22 = 22
	Nr23 = 23
	Nr24 = 24
	Nr25 = 25
	Nr26 = 26
	Nr27 = 27
	Nr28 = 28
	Nr29 = 29
	Nr30 = 30
	Nr31 = 31
	Nr32 = 32


# noinspection SpellCheckingInspection
class Sequence(Enum):
	"""Repeated capability Sequence"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3


# noinspection SpellCheckingInspection
class SerialBus(Enum):
	"""Repeated capability SerialBus"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4


# noinspection SpellCheckingInspection
class Spectrum(Enum):
	"""Repeated capability Spectrum"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4


# noinspection SpellCheckingInspection
class ThrHold(Enum):
	"""Repeated capability ThrHold"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4


# noinspection SpellCheckingInspection
class TimingReference(Enum):
	"""Repeated capability TimingReference"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12
	Nr13 = 13
	Nr14 = 14
	Nr15 = 15
	Nr16 = 16
	Nr17 = 17
	Nr18 = 18
	Nr19 = 19
	Nr20 = 20
	Nr21 = 21
	Nr22 = 22
	Nr23 = 23
	Nr24 = 24
	Nr25 = 25
	Nr26 = 26
	Nr27 = 27
	Nr28 = 28
	Nr29 = 29
	Nr30 = 30
	Nr31 = 31
	Nr32 = 32


# noinspection SpellCheckingInspection
class Vertical(Enum):
	"""Repeated capability Vertical"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2


# noinspection SpellCheckingInspection
class Voltmeter(Enum):
	"""Repeated capability Voltmeter"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8


# noinspection SpellCheckingInspection
class WaveformGen(Enum):
	"""Repeated capability WaveformGen"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2


# noinspection SpellCheckingInspection
class Word(Enum):
	"""Repeated capability Word"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12
	Nr13 = 13
	Nr14 = 14
	Nr15 = 15
	Nr16 = 16
	Nr17 = 17
	Nr18 = 18
	Nr19 = 19
	Nr20 = 20
	Nr21 = 21
	Nr22 = 22
	Nr23 = 23
	Nr24 = 24
	Nr25 = 25
	Nr26 = 26
	Nr27 = 27
	Nr28 = 28
	Nr29 = 29
	Nr30 = 30
	Nr31 = 31
	Nr32 = 32


# noinspection SpellCheckingInspection
class Xdata(Enum):
	"""Repeated capability Xdata"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12
	Nr13 = 13
	Nr14 = 14
	Nr15 = 15
	Nr16 = 16
	Nr17 = 17
	Nr18 = 18
	Nr19 = 19
	Nr20 = 20
	Nr21 = 21
	Nr22 = 22
	Nr23 = 23
	Nr24 = 24
	Nr25 = 25
	Nr26 = 26
	Nr27 = 27
	Nr28 = 28
	Nr29 = 29
	Nr30 = 30
	Nr31 = 31
	Nr32 = 32


# noinspection SpellCheckingInspection
class XyAxis(Enum):
	"""Repeated capability XyAxis"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12
	Nr13 = 13
	Nr14 = 14
	Nr15 = 15
	Nr16 = 16
	Nr17 = 17
	Nr18 = 18
	Nr19 = 19
	Nr20 = 20
	Nr21 = 21
	Nr22 = 22
	Nr23 = 23
	Nr24 = 24
	Nr25 = 25
	Nr26 = 26
	Nr27 = 27
	Nr28 = 28
	Nr29 = 29
	Nr30 = 30
	Nr31 = 31
	Nr32 = 32


# noinspection SpellCheckingInspection
class Zone(Enum):
	"""Repeated capability Zone"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4


# noinspection SpellCheckingInspection
class Zoom(Enum):
	"""Repeated capability Zoom"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
