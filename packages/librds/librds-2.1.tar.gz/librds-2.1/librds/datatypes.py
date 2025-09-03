from dataclasses import dataclass
from .af import AlternativeFrequencyEntryDecoded

@dataclass
class Group:
    a:int
    b:int
    c:int
    d:int
    is_version_b: bool
    def to_list(self) -> list[int]: return [self.a, self.b, self.c, self.d]
    def __iter__(self) -> list[int]: return self.to_list()

@dataclass
class GroupIdentifier:
    group_number: int
    group_version: bool

@dataclass
class Details:
    details="NOTSET"

@dataclass
class PSDetails(Details):
    segment: int
    di_dpty:bool
    ta: bool
    text: str
    af: AlternativeFrequencyEntryDecoded
    details="PS"

@dataclass
class FastSwitchingInformation(Details):
    segment: int
    di_dpty:bool
    ta: bool
    details="FSI"

@dataclass
class RTDetails(Details):
    segment: int
    ab: bool
    text: str
    details="RT"

@dataclass
class LongPSDetails(Details):
    segment: int
    text: str
    details="LPS"

@dataclass
class PTYNDetails(Details):
    segment: int
    ab: bool
    text: str
    details="PTYN"

@dataclass
class PINSLCetails(Details):
    data:int
    is_broadcaster_data:bool
    variant_code: int
    details="PINSLC"

@dataclass
class CTDetails(Details):
    mjd: int
    hour: int
    minute: int
    time_sense: bool
    local_offset: int
    details="CT"

@dataclass
class ODADetails(Details):
    data: list[int]
    details="ODA"

@dataclass
class ODAAidDetails(Details):
    oda_group: GroupIdentifier
    aid:int
    scb:int
    details="ODAAID"

@dataclass
class EONBDetails(Details):
    pi: int
    tp: bool
    ta: bool
    details="EONB"

@dataclass
class EONADetails(Details):
    pi: int
    tp: bool
    ta: bool
    ps_segment:int
    ps_text:str
    pty: int
    on_af: int
    variant_code:int
    details="EONA"

@dataclass
class DecodedGroup:
    raw_group: Group
    pi: int
    tp: bool
    pty: int
    group: GroupIdentifier
    details: Details