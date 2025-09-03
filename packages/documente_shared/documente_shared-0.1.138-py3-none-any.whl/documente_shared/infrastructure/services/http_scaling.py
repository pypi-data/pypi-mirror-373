from dataclasses import dataclass

from loguru import logger

from documente_shared.application.payloads import camel_to_snake
from documente_shared.domain.entities.scaling import ScalingRequirements
from documente_shared.domain.interfaces.scaling import ScalingService
from documente_shared.infrastructure.documente_client import DocumenteClientMixin


@dataclass
class HttpScalingService(
    DocumenteClientMixin,
    ScalingService,
):
    def get_requirements(self) -> ScalingRequirements:
        response = self.session.get(f"{self.api_url}/v1/scaling-requirements/")
        if response.status_code == 200:
            response_json = response.json()
            return ScalingRequirements.from_dict(
                data=camel_to_snake(response_json.get('data', {}))
            )

        logger.warning(f'Error getting scaling requirements: {response.text}')
        return ScalingRequirements()