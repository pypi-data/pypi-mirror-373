from typing import Optional, List

from pydantic import BaseModel

class Service(BaseModel):
    name: str
    groupName: str
    clusters: Optional[str] = ''
    cacheMillis: int = 1000
    hosts: List["Instance"] = []
    lastRefTime: int = 0
    checksum: str = ""
    allIps: bool = False
    reachProtectionThreshold: bool = False
    valid: bool = True

class Instance(BaseModel):
    instanceId: str = ''
    ip: str
    port: int
    weight: float = 1.0
    healthy: bool = True
    enabled: bool = True
    ephemeral: bool = True
    clusterName: str = ''
    serviceName: str = ''
    metadata: dict = {}
    instanceHeartBeatInterval: int = 5000
    instanceHeartBeatTimeout: int = 15000
    ipDeleteTimeout: int = 30000
    instanceIdGenerator: str = 'simple'
