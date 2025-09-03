from dataclasses import dataclass
from typing import Dict, Any, List

from pointr_cloud_common.dto.v9.base_dto import BaseDTO
from pointr_cloud_common.dto.v9.validation import ValidationError
from pointr_cloud_common.dto.v9.client_dtos import ClientDTO
from pointr_cloud_common.dto.v9.site_dtos import SiteDTO

@dataclass
class MigrationTreeDTO(BaseDTO):
    client: ClientDTO
    sites: List[SiteDTO]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "client": self.client.to_api_json(),
            "sites": [s.to_api_json() for s in self.sites]
        }
    
    def validate(self) -> bool:
        """Validate the DTO."""
        try:
            self.client.validate()
        except ValidationError as e:
            raise ValidationError(f"Invalid client: {str(e)}")
        
        for i, site in enumerate(self.sites):
            try:
                site.validate()
            except ValidationError as e:
                raise ValidationError(f"Invalid site at index {i}: {str(e)}")
        
        return True
