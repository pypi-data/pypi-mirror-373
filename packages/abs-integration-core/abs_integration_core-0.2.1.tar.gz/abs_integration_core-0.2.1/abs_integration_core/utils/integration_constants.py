from enum import Enum


class IntegrationProviders(str, Enum):
    SHAREPOINT = "sharepoint"
    DOCUSIGN = "docusign"
    GOOGLE = "google"
    OUTLOOK = "outlook"
    CALENDAR = "calendar"
