from typing import List, Optional
from pydantic import BaseModel

class CarrierInfo(BaseModel):
    internal_ip: str
    carrier_unique_id: str
    source: Optional[str] = None
    protocol: Optional[str] = None
    carrier_type: str
    name: str
    path: Optional[str] = None
    internet_ip: Optional[str] = None
    repo_namespace: Optional[str] = None
    domain: Optional[str] = None
    repo_url: Optional[str] = None
    nat_ip: Optional[str] = None
    carrier_owner_unique_id: Optional[str] = None
    branch: Optional[str] = None
    tag: Optional[List[str]] = None
    port: Optional[int] = None
    repo_name: Optional[str] = None
    description: Optional[str] = None
    ip: Optional[str] = None

class ComponentInfo(BaseModel):
    component_unique_id: str
    status: Optional[str] = None
    component_name: Optional[str] = None
    ecosystem: Optional[str] = None
    supplier_name: Optional[str] = None
    component_version: Optional[str] = None
    tags: Optional[List[str]] = None
    component_desc: Optional[str] = None
    vendor: Optional[str] = None
    asset_type: Optional[str] = None
    asset_category: Optional[str] = None
    vuln_union_ids: Optional[List[str]] = None
    repository: Optional[str] = None

class VulnContextInfo(BaseModel):
    type: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    name: Optional[str] = None

class VulnIdentifierInfo(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None

class VulnReferenceInfo(BaseModel):
    url: Optional[str] = None
    type: Optional[str] = None

class VulnSolutionInfo(BaseModel):
    type: Optional[str] = None
    details: Optional[str] = None
    description: Optional[str] = None

class VulnCVSSInfo(BaseModel):
    version: Optional[str] = None
    vector: Optional[str] = None
    score: Optional[str] = None

class VulnInfo(BaseModel):
    vuln_unique_id: str
    security_capability_unique_id: str  # Mandatory field
    context: Optional[List[VulnContextInfo]] = None
    vulnerability_type: Optional[str] = None
    vuln_identifiers: Optional[List[VulnIdentifierInfo]] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    report_url: Optional[str] = None
    discovery_at: Optional[str] = None
    impact: Optional[str] = None
    severity: Optional[str] = None
    title: Optional[str] = None
    cwe_id: Optional[str] = None
    reference: Optional[List[VulnReferenceInfo]] = None
    solution: Optional[List[VulnSolutionInfo]] = None
    description: Optional[str] = None
    cve_id: Optional[str] = None
    owner_name: Optional[str] = None
    cvss: Optional[List[VulnCVSSInfo]] = None

class CarrierVulnPayload(BaseModel):
    carrier: CarrierInfo
    component_list: Optional[List[ComponentInfo]] = None
    vuln_list: Optional[List[VulnInfo]] = None 