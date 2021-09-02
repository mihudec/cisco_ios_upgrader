import ipaddress
import pathlib

from pydantic import BaseModel, constr, root_validator
from pydantic.typing import Optional, List, Union, Literal


HOSTNAME_STR = constr(strip_whitespace=True, regex=r'\S+')

class HostModel(BaseModel):

    name: HOSTNAME_STR
    host: Optional[Union[ipaddress.IPv4Address, HOSTNAME_STR]]
    platform: Optional[str]
    filesystems: List[str]
    src_file: pathlib.Path
    dest_file: Optional[constr(strip_whitespace=True, regex=r'\S+')]
    state: Optional[List[str]]
    faiure_reason: Optional[List[str]]

    def add_state(self, state):
        if self.state is None:
            self.state = []
        if state not in self.state:
            self.state.append(state)

    def add_failure_reason(self, reason):
        if self.faiure_reason is None:
            self.faiure_reason = []
        if reason not in self.faiure_reason:
            self.faiure_reason.append(reason)



class HostsFile(BaseModel):
    hosts: List[HostModel]


class NetmikoProvider(BaseModel):

    username: str
    password: str
    device_type: Literal['cisco_ios']
    ssh_config_file: Optional[pathlib.Path]
