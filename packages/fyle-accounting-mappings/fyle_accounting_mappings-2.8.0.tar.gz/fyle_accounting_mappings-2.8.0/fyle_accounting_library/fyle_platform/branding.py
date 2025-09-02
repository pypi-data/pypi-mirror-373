from dataclasses import dataclass
from typing import Union

from django.conf import settings

from .enums import BrandIdEnum


@dataclass
class Configuration:
    fixed_employee_field_mapping: Union[str, bool]

@dataclass
class Feature:
    real_time_export_1hr_orgs: bool

@dataclass
class FeatureConfig:
    configuration: Configuration
    feature: Feature

configurations = {
    BrandIdEnum.CO: FeatureConfig(
        configuration=Configuration(fixed_employee_field_mapping='VENDOR'),
        feature=Feature(real_time_export_1hr_orgs=False)
    ),
    BrandIdEnum.FYLE: FeatureConfig(
        configuration=Configuration(fixed_employee_field_mapping=False),
        feature=Feature(real_time_export_1hr_orgs=True)
    )
}

# Temporary hack till we add BRAND_ID to the environment variables for all apps
brand_id = None
try:
    brand_id = settings.BRAND_ID
except AttributeError:
    brand_id = BrandIdEnum.FYLE

feature_configuration = configurations.get(brand_id)
