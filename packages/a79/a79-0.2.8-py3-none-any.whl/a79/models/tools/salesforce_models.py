# This is a generated file by scripts/codegen/composio.py, do not edit manually
# ruff: noqa: E501  # Ignore line length issues in generated files
from typing import Literal, Optional

from pydantic import BaseModel, Field


class AccountCreationWithContentTypeOptionInput(BaseModel):
    """Input model for SALESFORCE_ACCOUNT_CREATION_WITH_CONTENT_TYPE_OPTION"""

    AccountNumber: Optional[str] = Field(
        default=None,
        description="""Account number assigned to this account (max 40 chars). Please provide a value of type string.""",
    )  # noqa: E501

    AccountSource: Optional[str] = Field(
        default=None,
        description="""Origin source of the account record (admin-defined picklist, values max 40 chars). Please provide a value of type string.""",
    )  # noqa: E501

    Active__c: Optional[str] = Field(
        default=None,
        description="""Custom field indicating if the account is active. Please provide a value of type string.""",
    )  # noqa: E501

    AnnualRevenue: Optional[int] = Field(
        default=None,
        description="""Estimated annual revenue. Please provide a value of type integer.""",
    )  # noqa: E501

    BillingCity: Optional[str] = Field(
        default=None,
        description="""City for the billing address (max 40 chars). Please provide a value of type string.""",
    )  # noqa: E501

    BillingCountry: Optional[str] = Field(
        default=None,
        description="""Country for the billing address (max 80 chars). Please provide a value of type string.""",
    )  # noqa: E501

    BillingGeocodeAccuracy: Optional[str] = Field(
        default=None,
        description="""Accuracy level of the geocode for the billing address. Please provide a value of type string.""",
    )  # noqa: E501

    BillingLatitude: Optional[int] = Field(
        default=None,
        description="""Latitude for the billing address (-90 to 90, up to 15 decimal places). Please provide a value of type integer.""",
    )  # noqa: E501

    BillingLongitude: Optional[int] = Field(
        default=None,
        description="""Longitude for the billing address (-180 to 180, up to 15 decimal places). Please provide a value of type integer.""",
    )  # noqa: E501

    BillingPostalCode: Optional[str] = Field(
        default=None,
        description="""Postal code for the billing address (max 20 chars). Please provide a value of type string.""",
    )  # noqa: E501

    BillingState: Optional[str] = Field(
        default=None,
        description="""State or province for the billing address (max 80 chars). Please provide a value of type string.""",
    )  # noqa: E501

    BillingStreet: Optional[str] = Field(
        default=None,
        description="""Street address for the billing location. Please provide a value of type string.""",
    )  # noqa: E501

    CleanStatus: Optional[str] = Field(
        default=None,
        description="""Data quality status compared with Data.com. Please provide a value of type string.""",
    )  # noqa: E501

    CreatedById: Optional[str] = Field(
        default=None,
        description="""ID of the user who created the account (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    CreatedDate: Optional[str] = Field(
        default=None,
        description="""Date and time of account creation (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    CustomerPriority__c: Optional[str] = Field(
        default=None,
        description="""Custom field for customer priority (e.g., High, Medium, Low). Please provide a value of type string.""",
    )  # noqa: E501

    DandbCompanyId: Optional[str] = Field(
        default=None,
        description="""Associated Dun & Bradstreet company ID for D&B integration (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    Description: Optional[str] = Field(
        default=None,
        description="""Text description of the account (max 32,000 chars). Please provide a value of type string.""",
    )  # noqa: E501

    DunsNumber: Optional[str] = Field(
        default=None,
        description="""D-U-N-S number (9-digit identifier, max 9 chars). For business accounts. Requires Data.com Prospector/Clean. Please provide a value of type string.""",
    )  # noqa: E501

    Fax: Optional[str] = Field(
        default=None,
        description="""Fax number for the account. Please provide a value of type string.""",
    )  # noqa: E501

    Id: Optional[str] = Field(
        default=None,
        description="""Unique identifier for the account (system-generated and read-only upon creation). Please provide a value of type string.""",
    )  # noqa: E501

    Industry: Optional[str] = Field(
        default=None,
        description="""Primary industry of the account (picklist, max 40 chars). Please provide a value of type string.""",
    )  # noqa: E501

    IsDeleted: Optional[bool] = Field(
        default=None,
        description="""Indicates if the account is in the Recycle Bin (read-only). Please provide a value of type boolean.""",
    )  # noqa: E501

    Jigsaw: Optional[str] = Field(
        default=None,
        description="""Data.com company ID reference (max 20 chars, API v22.0+). For business accounts. Read-only, do not modify. Please provide a value of type string.""",
    )  # noqa: E501

    JigsawCompanyId: Optional[str] = Field(
        default=None,
        description="""Associated Data.com company ID (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    LastActivityDate: Optional[str] = Field(
        default=None,
        description="""Most recent due date of an event or closed task associated with the record (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    LastModifiedById: Optional[str] = Field(
        default=None,
        description="""ID of the user who last modified the account (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    LastModifiedDate: Optional[str] = Field(
        default=None,
        description="""Date and time of last modification (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    LastReferencedDate: Optional[str] = Field(
        default=None,
        description="""Timestamp of when current user last accessed this record or related items (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    LastViewedDate: Optional[str] = Field(
        default=None,
        description="""Timestamp of when current user last viewed this account record (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    MasterRecordId: Optional[str] = Field(
        default=None,
        description="""ID of the master record if this account was merged (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    NaicsCode: Optional[str] = Field(
        default=None,
        description="""NAICS code (6-digit industry classifier, max 8 chars). For business accounts. Requires Data.com Prospector/Clean. Please provide a value of type string.""",
    )  # noqa: E501

    NaicsDesc: Optional[str] = Field(
        default=None,
        description="""Description of line of business based on NAICS code (max 120 chars). For business accounts. Requires Data.com Prospector/Clean. Please provide a value of type string.""",
    )  # noqa: E501

    Name: str = Field(
        description="""Name of the account (required, max 255 chars). For Person Accounts, this is a concatenated field from the associated contact and not directly modifiable. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    NumberOfEmployees: Optional[int] = Field(
        default=None,
        description="""Number of employees (max 8 digits). Please provide a value of type integer.""",
    )  # noqa: E501

    NumberofLocations__c: Optional[int] = Field(
        default=None,
        description="""Custom field for the number of physical locations. Please provide a value of type integer.""",
    )  # noqa: E501

    OperatingHoursId: Optional[str] = Field(
        default=None,
        description="""ID of associated operating hours. Requires Salesforce Field Service. Please provide a value of type string.""",
    )  # noqa: E501

    OwnerId: Optional[str] = Field(
        default=None,
        description="""ID of the Salesforce user owning this account. 'Transfer Record' permission may be needed to update if not the API user (API v16.0+). Please provide a value of type string.""",
    )  # noqa: E501

    Ownership: Optional[str] = Field(
        default=None,
        description="""Ownership structure (picklist). Please provide a value of type string.""",
    )  # noqa: E501

    ParentId: Optional[str] = Field(
        default=None,
        description="""ID of the parent account for subsidiary or hierarchical relationships. Please provide a value of type string.""",
    )  # noqa: E501

    Phone: Optional[str] = Field(
        default=None,
        description="""Primary phone number for the account (max 40 chars). Please provide a value of type string.""",
    )  # noqa: E501

    PhotoUrl: Optional[str] = Field(
        default=None,
        description="""URL path for the social network profile image (read-only). Blank if Social Accounts and Contacts is not enabled for the user. Please provide a value of type string.""",
    )  # noqa: E501

    Rating: Optional[str] = Field(
        default=None,
        description="""Prospect rating (picklist). Please provide a value of type string.""",
    )  # noqa: E501

    SLAExpirationDate__c: Optional[str] = Field(
        default=None,
        description="""Custom field for SLA expiration date. Please provide a value of type string.""",
    )  # noqa: E501

    SLASerialNumber__c: Optional[str] = Field(
        default=None,
        description="""Custom field for SLA serial number. Please provide a value of type string.""",
    )  # noqa: E501

    SLA__c: Optional[str] = Field(
        default=None,
        description="""Custom field for Service Level Agreement (SLA) type/details. Please provide a value of type string.""",
    )  # noqa: E501

    ShippingCity: Optional[str] = Field(
        default=None,
        description="""City for the shipping address (max 40 chars). Please provide a value of type string.""",
    )  # noqa: E501

    ShippingCountry: Optional[str] = Field(
        default=None,
        description="""Country for the shipping address (max 80 chars). Please provide a value of type string.""",
    )  # noqa: E501

    ShippingGeocodeAccuracy: Optional[str] = Field(
        default=None,
        description="""Accuracy level of the geocode for the shipping address. Please provide a value of type string.""",
    )  # noqa: E501

    ShippingLatitude: Optional[int] = Field(
        default=None,
        description="""Latitude for the shipping address (-90 to 90, up to 15 decimal places). Please provide a value of type integer.""",
    )  # noqa: E501

    ShippingLongitude: Optional[int] = Field(
        default=None,
        description="""Longitude for the shipping address (-180 to 180, up to 15 decimal places). Please provide a value of type integer.""",
    )  # noqa: E501

    ShippingPostalCode: Optional[str] = Field(
        default=None,
        description="""Postal code for the shipping address (max 20 chars). Please provide a value of type string.""",
    )  # noqa: E501

    ShippingState: Optional[str] = Field(
        default=None,
        description="""State or province for the shipping address (max 80 chars). Please provide a value of type string.""",
    )  # noqa: E501

    ShippingStreet: Optional[str] = Field(
        default=None,
        description="""Street address for the shipping location (max 255 chars). Please provide a value of type string.""",
    )  # noqa: E501

    Sic: Optional[str] = Field(
        default=None,
        description="""Standard Industrial Classification (SIC) code (max 20 chars). For business accounts only. Please provide a value of type string.""",
    )  # noqa: E501

    SicDesc: Optional[str] = Field(
        default=None,
        description="""Description of line of business based on SIC code (max 80 chars). For business accounts only. Please provide a value of type string.""",
    )  # noqa: E501

    Site: Optional[str] = Field(
        default=None,
        description="""Name of the account’s specific location or site (max 80 chars). Please provide a value of type string.""",
    )  # noqa: E501

    SystemModstamp: Optional[str] = Field(
        default=None,
        description="""Timestamp of last modification by user or automated process (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    TickerSymbol: Optional[str] = Field(
        default=None,
        description="""Stock market ticker symbol (max 20 chars). For business accounts only. Please provide a value of type string.""",
    )  # noqa: E501

    Tradestyle: Optional[str] = Field(
        default=None,
        description="""Organization's 'Doing Business As' (DBA) name (max 255 chars). For business accounts. Requires Data.com Prospector/Clean. Please provide a value of type string.""",
    )  # noqa: E501

    Type: Optional[str] = Field(
        default=None,
        description="""Type of account, influencing categorization and behavior. Please provide a value of type string.""",
    )  # noqa: E501

    UpsellOpportunity__c: Optional[str] = Field(
        default=None,
        description="""Custom field indicating upsell opportunity potential. Please provide a value of type string.""",
    )  # noqa: E501

    Website: Optional[str] = Field(
        default=None,
        description="""Website URL of the account (max 255 chars). Please provide a value of type string.""",
    )  # noqa: E501

    YearStarted: Optional[str] = Field(
        default=None,
        description="""Year the organization was established (max 4 chars). For business accounts. Requires Data.com Prospector/Clean. Please provide a value of type string.""",
    )  # noqa: E501

    attributes__type: Optional[str] = Field(
        default=None,
        description="""Internal Salesforce field: Type of the SObject (e.g., 'Account'). System-set or read-only. Please provide a value of type string.""",
    )  # noqa: E501

    attributes__url: Optional[str] = Field(
        default=None,
        description="""Internal Salesforce field: Relative API URL for this SObject record. System-set or read-only. Please provide a value of type string.""",
    )  # noqa: E501


class CreateCampaignRecordViaPostInput(BaseModel):
    """Input model for SALESFORCE_CREATE_CAMPAIGN_RECORD_VIA_POST"""

    ActualCost: Optional[int] = Field(
        default=None,
        description="""Actual cost of the campaign, in the organization's currency. Please provide a value of type integer.""",
    )  # noqa: E501

    AmountAllOpportunities: Optional[int] = Field(
        default=None,
        description="""Read-only. Total monetary amount of all opportunities (including closed/won) in this campaign, in organization's currency. Label: Value Opportunities in Campaign. Please provide a value of type integer.""",
    )  # noqa: E501

    AmountWonOpportunities: Optional[int] = Field(
        default=None,
        description="""Read-only. Total monetary amount of closed/won opportunities in this campaign, in organization's currency. Label: Value Won Opportunities in Campaign. Please provide a value of type integer.""",
    )  # noqa: E501

    BudgetedCost: Optional[int] = Field(
        default=None,
        description="""Budgeted cost for this campaign, in the organization's currency. Please provide a value of type integer.""",
    )  # noqa: E501

    CampaignMemberRecordTypeId: Optional[str] = Field(
        default=None,
        description="""Record type ID for associated CampaignMember records, determining their fields and layout. Please provide a value of type string.""",
    )  # noqa: E501

    CreatedById: Optional[str] = Field(
        default=None,
        description="""Read-only. ID of the user who created this campaign record. Please provide a value of type string.""",
    )  # noqa: E501

    CreatedDate: Optional[str] = Field(
        default=None,
        description="""Read-only. Creation date and time (ISO 8601). Please provide a value of type string.""",
    )  # noqa: E501

    Description: Optional[str] = Field(
        default=None,
        description="""Detailed description of the campaign (limit 32KB; first 255 characters displayed in reports). Please provide a value of type string.""",
    )  # noqa: E501

    EndDate: Optional[str] = Field(
        default=None,
        description="""Ending date for the campaign (YYYY-MM-DD); responses received after this date are still counted. Please provide a value of type string.""",
    )  # noqa: E501

    ExpectedResponse: Optional[int] = Field(
        default=None,
        description="""Percentage of responses expected from targeted individuals. Please provide a value of type integer.""",
    )  # noqa: E501

    ExpectedRevenue: Optional[int] = Field(
        default=None,
        description="""Expected revenue from this campaign, in the organization's currency. Please provide a value of type integer.""",
    )  # noqa: E501

    Id: Optional[str] = Field(
        default=None,
        description="""Unique identifier for the campaign record, usually system-generated upon creation. Please provide a value of type string.""",
    )  # noqa: E501

    IsActive: Optional[bool] = Field(
        default=None,
        description="""Indicates if the campaign is active. Label: Active. Please provide a value of type boolean.""",
    )  # noqa: E501

    IsDeleted: Optional[bool] = Field(
        default=None,
        description="""Indicates if the campaign record has been deleted. Please provide a value of type boolean.""",
    )  # noqa: E501

    LastActivityDate: Optional[str] = Field(
        default=None,
        description="""Read-only. Most recent activity date (event due date or closed task due date, YYYY-MM-DD). Please provide a value of type string.""",
    )  # noqa: E501

    LastModifiedById: Optional[str] = Field(
        default=None,
        description="""Read-only. ID of the user who last modified this campaign record. Please provide a value of type string.""",
    )  # noqa: E501

    LastModifiedDate: Optional[str] = Field(
        default=None,
        description="""Read-only. Last modification date and time (ISO 8601). Please provide a value of type string.""",
    )  # noqa: E501

    LastReferencedDate: Optional[str] = Field(
        default=None,
        description="""Read-only. Timestamp of current user's last access to this record, a related record, or a list view (ISO 8601). Please provide a value of type string.""",
    )  # noqa: E501

    LastViewedDate: Optional[str] = Field(
        default=None,
        description="""Read-only. Timestamp of current user's last view of this record/list view (ISO 8601). Null if only accessed (see LastReferencedDate) but not viewed. Please provide a value of type string.""",
    )  # noqa: E501

    Name: str = Field(
        description="""Required. Name of the campaign (limit 80 characters). Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    NumberOfContacts: Optional[int] = Field(
        default=None,
        description="""Read-only. Total contacts associated with this campaign. Label: Total Contacts. Please provide a value of type integer.""",
    )  # noqa: E501

    NumberOfConvertedLeads: Optional[int] = Field(
        default=None,
        description="""Read-only. Leads converted to an account and contact from this campaign. Label: Converted Leads. Please provide a value of type integer.""",
    )  # noqa: E501

    NumberOfLeads: Optional[int] = Field(
        default=None,
        description="""Read-only. Total leads associated with this campaign. Label: Leads in Campaign. Please provide a value of type integer.""",
    )  # noqa: E501

    NumberOfOpportunities: Optional[int] = Field(
        default=None,
        description="""Read-only. Total opportunities associated with this campaign. Label: Opportunities in Campaign. Please provide a value of type integer.""",
    )  # noqa: E501

    NumberOfResponses: Optional[int] = Field(
        default=None,
        description="""Read-only. Contacts and unconverted leads with Member Status “Responded”. Label: Responses in Campaign. Please provide a value of type integer.""",
    )  # noqa: E501

    NumberOfWonOpportunities: Optional[int] = Field(
        default=None,
        description="""Read-only. Closed or won opportunities from this campaign. Label: Won Opportunities in Campaign. Please provide a value of type integer.""",
    )  # noqa: E501

    NumberSent: Optional[int] = Field(
        default=None,
        description="""Total number of individuals targeted (e.g., emails sent). Label: Num Sent. Please provide a value of type integer.""",
    )  # noqa: E501

    OwnerId: Optional[str] = Field(
        default=None,
        description="""ID of the campaign owner. Defaults to the ID of the user making the API call. Please provide a value of type string.""",
    )  # noqa: E501

    ParentId: Optional[str] = Field(
        default=None,
        description="""ID of the parent Campaign record for hierarchical grouping. Please provide a value of type string.""",
    )  # noqa: E501

    StartDate: Optional[str] = Field(
        default=None,
        description="""Starting date for the campaign (YYYY-MM-DD). Please provide a value of type string.""",
    )  # noqa: E501

    Status: Optional[str] = Field(
        default=None,
        description="""Current status of the campaign (limit 40 characters). Please provide a value of type string.""",
    )  # noqa: E501

    SystemModstamp: Optional[str] = Field(
        default=None,
        description="""Read-only. Last modification date and time by a user or automated process (ISO 8601). Please provide a value of type string.""",
    )  # noqa: E501

    Type: Optional[str] = Field(
        default=None,
        description="""Type of campaign (limit 40 characters). Please provide a value of type string.""",
    )  # noqa: E501

    attributes__type: Optional[str] = Field(
        default=None,
        description="""sObject type, typically 'Campaign'. Please provide a value of type string.""",
    )  # noqa: E501

    attributes__url: Optional[str] = Field(
        default=None,
        description="""Read-only. Relative URL to the campaign record. Please provide a value of type string.""",
    )  # noqa: E501


class CreateLeadWithSpecifiedContentTypeInput(BaseModel):
    """Input model for SALESFORCE_CREATE_LEAD_WITH_SPECIFIED_CONTENT_TYPE"""

    AnnualRevenue: Optional[int] = Field(
        default=None,
        description="""Annual revenue of the lead’s company. Please provide a value of type integer.""",
    )  # noqa: E501

    City: Optional[str] = Field(
        default=None,
        description="""City for the address. Please provide a value of type string.""",
    )  # noqa: E501

    CleanStatus: Optional[str] = Field(
        default=None,
        description="""Record's clean status compared with Data.com (e.g., Matched, Different, Pending). Please provide a value of type string.""",
    )  # noqa: E501

    Company: str = Field(
        description="""Company name (up to 255 characters). If person accounts are enabled and this is null, lead converts to a person account. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    CompanyDunsNumber: Optional[str] = Field(
        default=None,
        description="""D-U-N-S number (unique 9-digit business ID; max 9 chars). Available if Data.com Prospector/Clean used. Please provide a value of type string.""",
    )  # noqa: E501

    ConvertedAccountId: Optional[str] = Field(
        default=None,
        description="""ID of the Account object from conversion. Read-only. Please provide a value of type string.""",
    )  # noqa: E501

    ConvertedContactId: Optional[str] = Field(
        default=None,
        description="""ID of the Contact object from conversion. Read-only. Please provide a value of type string.""",
    )  # noqa: E501

    ConvertedDate: Optional[str] = Field(
        default=None,
        description="""Conversion date. Read-only; set upon conversion. Please provide a value of type string.""",
    )  # noqa: E501

    ConvertedOpportunityId: Optional[str] = Field(
        default=None,
        description="""ID of the Opportunity from conversion. Read-only. Please provide a value of type string.""",
    )  # noqa: E501

    Country: Optional[str] = Field(
        default=None,
        description="""Country for the address. Please provide a value of type string.""",
    )  # noqa: E501

    CreatedById: Optional[str] = Field(
        default=None,
        description="""ID of user who created this. System-generated, read-only. Please provide a value of type string.""",
    )  # noqa: E501

    CreatedDate: Optional[str] = Field(
        default=None,
        description="""Creation timestamp. System-generated, read-only. Please provide a value of type string.""",
    )  # noqa: E501

    CurrentGenerators__c: Optional[str] = Field(
        default=None,
        description="""Custom field for information about current generators or similar equipment/services. Please provide a value of type string.""",
    )  # noqa: E501

    DandbCompanyId: Optional[str] = Field(
        default=None,
        description="""Associated D&B Company record ID. Available if Data.com used. Please provide a value of type string.""",
    )  # noqa: E501

    Description: Optional[str] = Field(
        default=None,
        description="""Description (up to 32,000 characters). Please provide a value of type string.""",
    )  # noqa: E501

    Email: Optional[str] = Field(
        default=None,
        description="""Email address. Please provide a value of type string.""",
    )  # noqa: E501

    EmailBouncedDate: Optional[str] = Field(
        default=None,
        description="""Date/time of last email bounce (if bounce management active). Please provide a value of type string.""",
    )  # noqa: E501

    EmailBouncedReason: Optional[str] = Field(
        default=None,
        description="""Reason for last email bounce (if bounce management active). Please provide a value of type string.""",
    )  # noqa: E501

    FirstName: Optional[str] = Field(
        default=None,
        description="""First name (up to 40 characters). Please provide a value of type string.""",
    )  # noqa: E501

    IndividualId: Optional[str] = Field(
        default=None,
        description="""Associated data privacy record ID. Available if Data Protection/Privacy enabled. Please provide a value of type string.""",
    )  # noqa: E501

    Industry: Optional[str] = Field(
        default=None,
        description="""Primary industry of the lead's company. Please provide a value of type string.""",
    )  # noqa: E501

    IsConverted: Optional[bool] = Field(
        default=None,
        description="""True if converted to Account/Contact/Opportunity; false otherwise. Read-only; set upon conversion. Please provide a value of type boolean.""",
    )  # noqa: E501

    IsDeleted: Optional[bool] = Field(
        default=None,
        description="""Indicates if the lead is in the Recycle Bin (true) or not (false). Salesforce defaults to false if this field is omitted. Please provide a value of type boolean.""",
    )  # noqa: E501

    IsPriorityRecord: Optional[bool] = Field(
        default=None,
        description="""True if this lead is marked as a priority record. Please provide a value of type boolean.""",
    )  # noqa: E501

    IsUnreadByOwner: Optional[bool] = Field(
        default=None,
        description="""True if assigned to an owner but not yet viewed by them. Salesforce defaults to true when a lead is created or its owner changes. Please provide a value of type boolean.""",
    )  # noqa: E501

    Jigsaw: Optional[str] = Field(
        default=None,
        description="""Data.com contact ID (max 20 chars). Indicates Data.com import. Do not modify; for import troubleshooting. Please provide a value of type string.""",
    )  # noqa: E501

    JigsawContactId: Optional[str] = Field(
        default=None,
        description="""Jigsaw contact ID. Read-only. Please provide a value of type string.""",
    )  # noqa: E501

    LastActivityDate: Optional[str] = Field(
        default=None,
        description="""Later of most recent event's Due Date or most recently closed task's Due Date. Read-only. Please provide a value of type string.""",
    )  # noqa: E501

    LastModifiedById: Optional[str] = Field(
        default=None,
        description="""ID of user who last modified this. System-generated, read-only. Please provide a value of type string.""",
    )  # noqa: E501

    LastModifiedDate: Optional[str] = Field(
        default=None,
        description="""Last modification timestamp. System-generated, read-only. Please provide a value of type string.""",
    )  # noqa: E501

    LastName: str = Field(
        description="""Last name of the lead (up to 80 characters). Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    LastReferencedDate: Optional[str] = Field(
        default=None,
        description="""Timestamp when current user last accessed this or related record. Read-only. Please provide a value of type string.""",
    )  # noqa: E501

    LastViewedDate: Optional[str] = Field(
        default=None,
        description="""Timestamp when current user last viewed. Null if only accessed (LastReferencedDate) but not viewed. Read-only. Please provide a value of type string.""",
    )  # noqa: E501

    LeadSource: Optional[
        Literal["Web", "Other", "Phone Inquiry", "Partner Referral", "Purchased List"]
    ] = Field(
        default=None,
        description="""Source of the lead. Please provide a value of type string.""",
    )  # noqa: E501

    MasterRecordId: Optional[str] = Field(
        default=None,
        description="""ID of the master record if this lead was deleted due to a merge; null otherwise. Please provide a value of type string.""",
    )  # noqa: E501

    NumberOfEmployees: Optional[int] = Field(
        default=None,
        description="""Number of employees at the lead’s company. Please provide a value of type integer.""",
    )  # noqa: E501

    NumberofLocations__c: Optional[int] = Field(
        default=None,
        description="""Custom field for the number of locations the lead's company has. Please provide a value of type integer.""",
    )  # noqa: E501

    OwnerId: Optional[str] = Field(
        default=None,
        description="""ID of the owner. Defaults to current user if unspecified. Please provide a value of type string.""",
    )  # noqa: E501

    Phone: Optional[str] = Field(
        default=None,
        description="""Primary phone number. Please provide a value of type string.""",
    )  # noqa: E501

    PhotoUrl: Optional[str] = Field(
        default=None,
        description="""Path for social network profile image URL; used with Salesforce instance URL. Empty if Social Accounts/Contacts disabled. Please provide a value of type string.""",
    )  # noqa: E501

    PostalCode: Optional[str] = Field(
        default=None,
        description="""Postal or ZIP code for the address. Please provide a value of type string.""",
    )  # noqa: E501

    Primary__c: Optional[str] = Field(
        default=None,
        description="""Custom field, possibly indicates if primary contact/lead. Please provide a value of type string.""",
    )  # noqa: E501

    ProductInterest__c: Optional[str] = Field(
        default=None,
        description="""Custom field indicating the product(s) the lead is interested in. Please provide a value of type string.""",
    )  # noqa: E501

    Rating: Optional[str] = Field(
        default=None,
        description="""Rating (e.g., Hot, Warm, Cold). Please provide a value of type string.""",
    )  # noqa: E501

    SICCode__c: Optional[str] = Field(
        default=None,
        description="""Custom field for Standard Industrial Classification (SIC) code. Please provide a value of type string.""",
    )  # noqa: E501

    Salutation: Optional[Literal["Mr.", "Ms.", "Mrs.", "Dr.", "Prof."]] = Field(
        default=None,
        description="""Salutation for the lead. Please provide a value of type string.""",
    )  # noqa: E501

    State: Optional[str] = Field(
        default=None,
        description="""State or province for the address. Please provide a value of type string.""",
    )  # noqa: E501

    Status: Optional[str] = Field(
        default=None,
        description="""Current status (e.g., Open, Contacted). Defined in LeadStatus object in Salesforce setup. Please provide a value of type string.""",
    )  # noqa: E501

    Street: Optional[str] = Field(
        default=None,
        description="""Street address. Please provide a value of type string.""",
    )  # noqa: E501

    SystemModstamp: Optional[str] = Field(
        default=None,
        description="""Timestamp of last modification by user or system. System-generated, read-only. Please provide a value of type string.""",
    )  # noqa: E501

    Title: Optional[str] = Field(
        default=None,
        description="""Title (e.g., CFO, CEO; up to 128 characters). Please provide a value of type string.""",
    )  # noqa: E501

    Website: Optional[str] = Field(
        default=None,
        description="""Website URL. Please provide a value of type string.""",
    )  # noqa: E501

    attributes__type: Optional[str] = Field(
        default=None,
        description="""SObject type (typically 'Lead'). Usually metadata, not set by user on creation. Please provide a value of type string.""",
    )  # noqa: E501

    attributes__url: Optional[str] = Field(
        default=None,
        description="""Relative URL of SObject record. Usually metadata, not set by user on creation. Please provide a value of type string.""",
    )  # noqa: E501


class CreateNoteRecordWithContentTypeHeaderInput(BaseModel):
    """Input model for SALESFORCE_CREATE_NOTE_RECORD_WITH_CONTENT_TYPE_HEADER"""

    Body: str = Field(
        description="""Content or body of the note. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    CreatedById: Optional[str] = Field(
        default=None,
        description="""ID of the user who created the note (system-generated, read-only on create). Please provide a value of type string.""",
    )  # noqa: E501

    CreatedDate: Optional[str] = Field(
        default=None,
        description="""Timestamp of note creation (system-generated, read-only on create). Please provide a value of type string.""",
    )  # noqa: E501

    Id: Optional[str] = Field(
        default=None,
        description="""Unique identifier for the Note object, typically auto-generated and not provided in the request. Please provide a value of type string.""",
    )  # noqa: E501

    IsDeleted: Optional[bool] = Field(
        default=None,
        description="""Indicates if the object is in the Recycle Bin. Label is Deleted. Please provide a value of type boolean.""",
    )  # noqa: E501

    IsPrivate: Optional[bool] = Field(
        default=None,
        description="""If true, restricts note visibility to the owner or users with "Modify All Data" permission. Label is Private. Please provide a value of type boolean.""",
    )  # noqa: E501

    LastModifiedById: Optional[str] = Field(
        default=None,
        description="""ID of the user who last modified the note (system-generated). Please provide a value of type string.""",
    )  # noqa: E501

    LastModifiedDate: Optional[str] = Field(
        default=None,
        description="""Timestamp of last modification (system-generated). Please provide a value of type string.""",
    )  # noqa: E501

    OwnerId: Optional[str] = Field(
        default=None,
        description="""ID of the Salesforce User who will own the note; defaults to the API user. Please provide a value of type string.""",
    )  # noqa: E501

    ParentId: str = Field(
        description="""ID of the parent Salesforce record (e.g., Account, Contact) to which this note is related; must reference an existing record. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    SystemModstamp: Optional[str] = Field(
        default=None,
        description="""Timestamp of last system change (system-generated). Please provide a value of type string.""",
    )  # noqa: E501

    Title: str = Field(
        description="""Title of the note. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    attributes__type: Optional[str] = Field(
        default=None,
        description="""SObject type, should be 'Note' if provided. Corresponds to `attributes.type` in the JSON body. Please provide a value of type string.""",
    )  # noqa: E501

    attributes__url: Optional[str] = Field(
        default=None,
        description="""API URL for the SObject. Corresponds to `attributes.url` in the JSON body (typically read-only). Please provide a value of type string.""",
    )  # noqa: E501


class ExecuteSoqlQueryInput(BaseModel):
    """Input model for SALESFORCE_EXECUTE_SOQL_QUERY"""

    soql_query: str = Field(
        description="""The SOQL (Salesforce Object Query Language) query to execute. Example: 'SELECT Id, Name, Email FROM Contact WHERE Name LIKE '%John%' LIMIT 10'. Make sure to follow SOQL syntax and escape single quotes properly. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class FetchModifiedOrUnmodifiedSobjectsInput(BaseModel):
    """Input model for SALESFORCE_FETCH_MODIFIED_OR_UNMODIFIED_SOBJECTS"""

    if_modified_since: Optional[str] = Field(
        default=None,
        alias="If-Modified-Since",
        description="""Fetch sObjects modified after this RFC3339 datetime string. Please provide a value of type string.""",
    )  # noqa: E501

    if_unmodified_since: Optional[str] = Field(
        default=None,
        description="""Fetch sObjects unmodified since this RFC3339 datetime string. Please provide a value of type string.""",
    )  # noqa: E501


class QueryContactsByNameInput(BaseModel):
    """Input model for SALESFORCE_QUERY_CONTACTS_BY_NAME"""

    contact_name: str = Field(
        description="""The name or partial name to search for within the 'Name' field of Salesforce Contact records. Supports partial matches (e.g., 'John' will find 'John Smith', 'John Doe', etc.). Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    fields: Optional[str] = Field(
        default="Id,Name,Email,Phone,AccountId",
        description="""Comma-separated list of Salesforce Contact object field API names to retrieve. Common field API names include: Id, Name, FirstName, LastName, Email, Phone, MobilePhone, Title, AccountId. Please provide a value of type string.""",
    )  # noqa: E501

    limit: Optional[int] = Field(
        default=20,
        description="""Maximum number of contact records to return. Please provide a value of type integer.""",
    )  # noqa: E501


class RemoveAccountByUniqueIdentifierInput(BaseModel):
    """Input model for SALESFORCE_REMOVE_ACCOUNT_BY_UNIQUE_IDENTIFIER"""

    id: str = Field(
        description="""Unique Salesforce Account ID (typically 15 or 18 characters). Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class RetrieveAccountDataAndErrorResponsesInput(BaseModel):
    """Input model for SALESFORCE_RETRIEVE_ACCOUNT_DATA_AND_ERROR_RESPONSES"""

    pass


class RetrieveCampaignDataWithErrorHandlingInput(BaseModel):
    """Input model for SALESFORCE_RETRIEVE_CAMPAIGN_DATA_WITH_ERROR_HANDLING"""

    pass


class RetrieveLeadByIdInput(BaseModel):
    """Input model for SALESFORCE_RETRIEVE_LEAD_BY_ID"""

    fields: Optional[str] = Field(
        default=None,
        description="""Comma-delimited list of Salesforce Lead field API names to return (e.g., Name,Email,Company). If omitted, all accessible fields are returned. Please provide a value of type string.""",
    )  # noqa: E501

    id: str = Field(
        description="""Unique identifier (ID) of the Salesforce Lead to retrieve. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class RetrieveLeadDataWithVariousResponsesInput(BaseModel):
    """Input model for SALESFORCE_RETRIEVE_LEAD_DATA_WITH_VARIOUS_RESPONSES"""

    pass


class RetrieveOpportunitiesDataInput(BaseModel):
    """Input model for SALESFORCE_RETRIEVE_OPPORTUNITIES_DATA"""

    pass


class RetrieveSpecificContactByIdInput(BaseModel):
    """Input model for SALESFORCE_RETRIEVE_SPECIFIC_CONTACT_BY_ID"""

    fields: Optional[str] = Field(
        default=None,
        description="""Comma-delimited string of Contact field API names to retrieve. If omitted, a default set of fields is returned. Please provide a value of type string.""",
    )  # noqa: E501

    id: str = Field(
        description="""The unique Salesforce ID of the Contact record to retrieve. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class UpdateContactByIdInput(BaseModel):
    """Input model for SALESFORCE_UPDATE_CONTACT_BY_ID"""

    AccountId: Optional[str] = Field(
        default=None,
        description="""Parent Account ID. When changing accounts for portal-enabled contacts, update up to 50 contacts at once, preferably after business hours. Please provide a value of type string.""",
    )  # noqa: E501

    AssistantName: Optional[str] = Field(
        default=None,
        description="""Assistant's name. Please provide a value of type string.""",
    )  # noqa: E501

    AssistantPhone: Optional[str] = Field(
        default=None,
        description="""Assistant's telephone number. Please provide a value of type string.""",
    )  # noqa: E501

    Birthdate: Optional[str] = Field(
        default=None,
        description="""Birthdate (YYYY-MM-DD). Year is ignored in report/SOQL filters. Please provide a value of type string.""",
    )  # noqa: E501

    CleanStatus: Optional[str] = Field(
        default=None,
        description="""Data quality status compared to Data.com (e.g., 'Matched', 'Pending'). Please provide a value of type string.""",
    )  # noqa: E501

    ContactSource: Optional[str] = Field(
        default=None,
        description="""Source of contact information (e.g., external system). Please provide a value of type string.""",
    )  # noqa: E501

    CreatedById: Optional[str] = Field(
        default=None,
        description="""ID of the user who created the contact (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    CreatedDate: Optional[str] = Field(
        default=None,
        description="""Creation date/time (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    Department: Optional[str] = Field(
        default=None, description="""Department. Please provide a value of type string."""
    )  # noqa: E501

    Description: Optional[str] = Field(
        default=None,
        description="""Description (up to 32KB). Label: 'Contact Description'. Please provide a value of type string.""",
    )  # noqa: E501

    Email: Optional[str] = Field(
        default=None,
        description="""Email address. Please provide a value of type string.""",
    )  # noqa: E501

    EmailBouncedDate: Optional[str] = Field(
        default=None,
        description="""Date/time of email bounce, if bounce management is active. Please provide a value of type string.""",
    )  # noqa: E501

    EmailBouncedReason: Optional[str] = Field(
        default=None,
        description="""Reason for email bounce, if bounce management is active. Please provide a value of type string.""",
    )  # noqa: E501

    Fax: Optional[str] = Field(
        default=None,
        description="""Business fax number. Label: 'Business Fax'. Please provide a value of type string.""",
    )  # noqa: E501

    FirstName: Optional[str] = Field(
        default=None,
        description="""Contact's first name, up to 40 characters. Please provide a value of type string.""",
    )  # noqa: E501

    HomePhone: Optional[str] = Field(
        default=None,
        description="""Home telephone number. Please provide a value of type string.""",
    )  # noqa: E501

    Id: Optional[str] = Field(
        default=None,
        description="""Salesforce Contact ID. Typically not required in the request body if the Contact ID is in the URL path; if provided, it must match the path ID. Please provide a value of type string.""",
    )  # noqa: E501

    IndividualId: Optional[str] = Field(
        default=None,
        description="""Associated data privacy record ID. Available if Data Protection and Privacy is enabled. Please provide a value of type string.""",
    )  # noqa: E501

    IsDeleted: Optional[bool] = Field(
        default=None,
        description="""Indicates if the contact is in the Recycle Bin. Label: 'Deleted'. Please provide a value of type boolean.""",
    )  # noqa: E501

    IsEmailBounced: Optional[bool] = Field(
        default=None,
        description="""Indicates if an email to the contact has bounced, if bounce management is active. Please provide a value of type boolean.""",
    )  # noqa: E501

    IsPriorityRecord: Optional[bool] = Field(
        default=None,
        description="""Indicates if this is a priority contact. Please provide a value of type boolean.""",
    )  # noqa: E501

    Jigsaw: Optional[str] = Field(
        default=None,
        description="""Data.com (Salesforce D&B) company ID. Max 20 chars. Do not modify; used for import troubleshooting. Please provide a value of type string.""",
    )  # noqa: E501

    JigsawContactId: Optional[str] = Field(
        default=None,
        description="""Data.com contact ID (read-only). Used for internal sync; do not modify. Please provide a value of type string.""",
    )  # noqa: E501

    Languages__c: Optional[str] = Field(
        default=None,
        description="""Custom field 'Languages__c': Languages spoken by the contact (e.g., English;Spanish). Please provide a value of type string.""",
    )  # noqa: E501

    LastActivityDate: Optional[str] = Field(
        default=None,
        description="""Date of the most recent activity or closed task (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    LastCURequestDate: Optional[str] = Field(
        default=None,
        description="""Timestamp of the last contact update request for data privacy (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    LastCUUpdateDate: Optional[str] = Field(
        default=None,
        description="""Timestamp of the last contact update for data privacy (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    LastModifiedById: Optional[str] = Field(
        default=None,
        description="""ID of the user who last modified the contact (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    LastModifiedDate: Optional[str] = Field(
        default=None,
        description="""Last modification date/time (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    LastName: Optional[str] = Field(
        default=None,
        description="""Contact's last name, up to 80 characters. Please provide a value of type string.""",
    )  # noqa: E501

    LastReferencedDate: Optional[str] = Field(
        default=None,
        description="""Timestamp of when current user last accessed this contact or related records (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    LastViewedDate: Optional[str] = Field(
        default=None,
        description="""Timestamp of when current user last viewed this contact; null if only referenced (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    LeadSource: Optional[str] = Field(
        default=None,
        description="""Lead source (e.g., Web, Partner Referral). Please provide a value of type string.""",
    )  # noqa: E501

    Level__c: Optional[str] = Field(
        default=None,
        description="""Custom field 'Level__c': Categorizes contact importance/engagement (e.g., Primary). Please provide a value of type string.""",
    )  # noqa: E501

    MailingCity: Optional[str] = Field(
        default=None,
        description="""Mailing address: city. Please provide a value of type string.""",
    )  # noqa: E501

    MailingCountry: Optional[str] = Field(
        default=None,
        description="""Mailing address: country. Please provide a value of type string.""",
    )  # noqa: E501

    MailingGeocodeAccuracy: Optional[str] = Field(
        default=None,
        description="""Mailing address: geocode accuracy. Please provide a value of type string.""",
    )  # noqa: E501

    MailingLatitude: Optional[int] = Field(
        default=None,
        description="""Mailing address: latitude (–90 to 90, up to 15 decimal places). Use with MailingLongitude. Please provide a value of type integer.""",
    )  # noqa: E501

    MailingLongitude: Optional[int] = Field(
        default=None,
        description="""Mailing address: longitude (–180 to 180, up to 15 decimal places). Use with MailingLatitude. Please provide a value of type integer.""",
    )  # noqa: E501

    MailingPostalCode: Optional[str] = Field(
        default=None,
        description="""Mailing address: postal code. Please provide a value of type string.""",
    )  # noqa: E501

    MailingState: Optional[str] = Field(
        default=None,
        description="""Mailing address: state/province. Please provide a value of type string.""",
    )  # noqa: E501

    MailingStreet: Optional[str] = Field(
        default=None,
        description="""Mailing address: street. Please provide a value of type string.""",
    )  # noqa: E501

    MasterRecordId: Optional[str] = Field(
        default=None,
        description="""ID of the master record if this contact was merged and deleted; null otherwise. Please provide a value of type string.""",
    )  # noqa: E501

    MobilePhone: Optional[str] = Field(
        default=None,
        description="""Mobile phone number. Please provide a value of type string.""",
    )  # noqa: E501

    Name: Optional[str] = Field(
        default=None,
        description="""Full name (read-only). Concatenation of FirstName, MiddleName, LastName, Suffix. Please provide a value of type string.""",
    )  # noqa: E501

    OtherCity: Optional[str] = Field(
        default=None,
        description="""Alternative address: city. Please provide a value of type string.""",
    )  # noqa: E501

    OtherCountry: Optional[str] = Field(
        default=None,
        description="""Alternative address: country. Please provide a value of type string.""",
    )  # noqa: E501

    OtherGeocodeAccuracy: Optional[str] = Field(
        default=None,
        description="""Alternative address: geocode accuracy. Please provide a value of type string.""",
    )  # noqa: E501

    OtherLatitude: Optional[int] = Field(
        default=None,
        description="""Alternative address: latitude (–90 to 90, up to 15 decimal places). Use with OtherLongitude. Please provide a value of type integer.""",
    )  # noqa: E501

    OtherLongitude: Optional[int] = Field(
        default=None,
        description="""Alternative address: longitude (–180 to 180, up to 15 decimal places). Use with OtherLatitude. Please provide a value of type integer.""",
    )  # noqa: E501

    OtherPhone: Optional[str] = Field(
        default=None,
        description="""Alternative address: phone number. Please provide a value of type string.""",
    )  # noqa: E501

    OtherPostalCode: Optional[str] = Field(
        default=None,
        description="""Alternative address: postal code. Please provide a value of type string.""",
    )  # noqa: E501

    OtherState: Optional[str] = Field(
        default=None,
        description="""Alternative address: state/province. Please provide a value of type string.""",
    )  # noqa: E501

    OtherStreet: Optional[str] = Field(
        default=None,
        description="""Alternative address: street. Please provide a value of type string.""",
    )  # noqa: E501

    OwnerId: Optional[str] = Field(
        default=None,
        description="""Salesforce User ID of the contact owner. Please provide a value of type string.""",
    )  # noqa: E501

    Phone: Optional[str] = Field(
        default=None,
        description="""Primary business phone. Label: 'Business Phone'. Please provide a value of type string.""",
    )  # noqa: E501

    PhotoUrl: Optional[str] = Field(
        default=None,
        description="""Relative path to profile photo (read-only). Combine with instance URL for full path. Empty if Social Accounts/Contacts is disabled. Please provide a value of type string.""",
    )  # noqa: E501

    ReportsToId: Optional[str] = Field(
        default=None,
        description="""Manager's Contact ID. Not available if IsPersonAccount is true. Please provide a value of type string.""",
    )  # noqa: E501

    Salutation: Optional[str] = Field(
        default=None,
        description="""Honorific for greetings (e.g., Mr., Ms., Dr.). Please provide a value of type string.""",
    )  # noqa: E501

    SystemModstamp: Optional[str] = Field(
        default=None,
        description="""Last system modification date/time (read-only). Please provide a value of type string.""",
    )  # noqa: E501

    Title: Optional[str] = Field(
        default=None,
        description="""Job title (e.g., CEO, Vice President). Please provide a value of type string.""",
    )  # noqa: E501

    attributes__type: Optional[str] = Field(
        default=None,
        description="""Salesforce SObject type (e.g., 'Contact'). Typically read-only, not for update requests. Please provide a value of type string.""",
    )  # noqa: E501

    attributes__url: Optional[str] = Field(
        default=None,
        description="""Relative API URL for this SObject. Typically read-only, not for update requests. Please provide a value of type string.""",
    )  # noqa: E501

    id: str = Field(
        description="""Unique Salesforce ID of the Contact to update (e.g., '001R0000005hDFYIA2'). This is a required path parameter. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class CreateNewContactWithJsonHeaderInput(BaseModel):
    """Input model for SALESFORCE_CREATE_NEW_CONTACT_WITH_JSON_HEADER"""

    AccountId: Optional[str] = Field(
        default=None,
        description="""Parent Account ID; must exist if specified. Caution advised when changing for portal-enabled contacts. Please provide a value of type string.""",
    )  # noqa: E501

    AssistantName: Optional[str] = Field(
        default=None,
        description="""Assistant's name. Please provide a value of type string.""",
    )  # noqa: E501

    AssistantPhone: Optional[str] = Field(
        default=None,
        description="""Assistant's phone. Please provide a value of type string.""",
    )  # noqa: E501

    Birthdate: Optional[str] = Field(
        default=None,
        description="""Birthdate (YYYY-MM-DD). SOQL queries ignore year for date comparisons (e.g., `Birthdate > TODAY`). Please provide a value of type string.""",
    )  # noqa: E501

    CleanStatus: Optional[str] = Field(
        default=None,
        description="""Record's clean status compared to Data.com (e.g., 'Matched' may appear as 'In Sync' in UI). Please provide a value of type string.""",
    )  # noqa: E501

    ContactSource: Optional[str] = Field(
        default=None,
        description="""Source of contact information, for more granular tracking than LeadSource. Please provide a value of type string.""",
    )  # noqa: E501

    CreatedById: Optional[str] = Field(
        default=None,
        description="""Read-only: ID of user who created contact. Please provide a value of type string.""",
    )  # noqa: E501

    CreatedDate: Optional[str] = Field(
        default=None,
        description="""Read-only: Timestamp of contact creation. Please provide a value of type string.""",
    )  # noqa: E501

    Department: Optional[str] = Field(
        default=None,
        description="""Contact's department. Please provide a value of type string.""",
    )  # noqa: E501

    Description: Optional[str] = Field(
        default=None,
        description="""Description (up to 32KB). Label: Contact Description. Please provide a value of type string.""",
    )  # noqa: E501

    Email: Optional[str] = Field(
        default=None,
        description="""Email address. Please provide a value of type string.""",
    )  # noqa: E501

    EmailBouncedDate: Optional[str] = Field(
        default=None,
        description="""Date and time of email bounce, if bounce management is active and an email bounced. Please provide a value of type string.""",
    )  # noqa: E501

    EmailBouncedReason: Optional[str] = Field(
        default=None,
        description="""Reason for email bounce, if bounce management is active and an email bounced. Please provide a value of type string.""",
    )  # noqa: E501

    Fax: Optional[str] = Field(
        default=None,
        description="""Primary business fax. Label: Business Fax. Please provide a value of type string.""",
    )  # noqa: E501

    FirstName: Optional[str] = Field(
        default=None,
        description="""Contact's first name (up to 40 characters). Please provide a value of type string.""",
    )  # noqa: E501

    HomePhone: Optional[str] = Field(
        default=None, description="""Home phone. Please provide a value of type string."""
    )  # noqa: E501

    Id: Optional[str] = Field(
        default=None,
        description="""Unique contact identifier, system-generated; omit for new contact creation. Please provide a value of type string.""",
    )  # noqa: E501

    IndividualId: Optional[str] = Field(
        default=None,
        description="""ID of associated data privacy record. Available if Data Protection & Privacy enabled. Please provide a value of type string.""",
    )  # noqa: E501

    IsDeleted: Optional[bool] = Field(
        default=None,
        description="""Read-only: True if contact is in Recycle Bin. Label: Deleted. Please provide a value of type boolean.""",
    )  # noqa: E501

    IsEmailBounced: Optional[bool] = Field(
        default=None,
        description="""True if email bounced; bounce management must be active. Please provide a value of type boolean.""",
    )  # noqa: E501

    IsPriorityRecord: Optional[bool] = Field(
        default=None,
        description="""True if contact is a priority record. Please provide a value of type boolean.""",
    )  # noqa: E501

    Jigsaw: Optional[str] = Field(
        default=None,
        description="""Read-only: Data.com Company ID (max 20 chars), indicates import from Data.com. Label: Data.com Key. Do not modify. Please provide a value of type string.""",
    )  # noqa: E501

    JigsawContactId: Optional[str] = Field(
        default=None,
        description="""Read-only: Jigsaw (Data.com) ID, links to Data.com contact data. Please provide a value of type string.""",
    )  # noqa: E501

    Languages__c: Optional[str] = Field(
        default=None,
        description="""Custom field: Languages spoken by the contact (e.g., English;Spanish). '__c' denotes a custom field. Please provide a value of type string.""",
    )  # noqa: E501

    LastActivityDate: Optional[str] = Field(
        default=None,
        description="""Read-only: Most recent due date of associated event or closed task. Please provide a value of type string.""",
    )  # noqa: E501

    LastCURequestDate: Optional[str] = Field(
        default=None,
        description="""Read-only: Timestamp of last contact update request (e.g., Data.com Clean). Please provide a value of type string.""",
    )  # noqa: E501

    LastCUUpdateDate: Optional[str] = Field(
        default=None,
        description="""Read-only: Timestamp of last update from a contact update request. Please provide a value of type string.""",
    )  # noqa: E501

    LastModifiedById: Optional[str] = Field(
        default=None,
        description="""Read-only: ID of user who last modified contact. Please provide a value of type string.""",
    )  # noqa: E501

    LastModifiedDate: Optional[str] = Field(
        default=None,
        description="""Read-only: Timestamp of last modification. Please provide a value of type string.""",
    )  # noqa: E501

    LastName: str = Field(
        description="""Required: Contact's last name (up to 80 characters). Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    LastReferencedDate: Optional[str] = Field(
        default=None,
        description="""Read-only: Timestamp current user last accessed contact, related record, or its list view. Please provide a value of type string.""",
    )  # noqa: E501

    LastViewedDate: Optional[str] = Field(
        default=None,
        description="""Read-only: Timestamp current user last viewed contact. Null if only referenced. Please provide a value of type string.""",
    )  # noqa: E501

    LeadSource: Optional[str] = Field(
        default=None,
        description="""Lead source for this contact (e.g., Web, Phone Inquiry). Please provide a value of type string.""",
    )  # noqa: E501

    Level__c: Optional[str] = Field(
        default=None,
        description="""Custom field: Contact's level (e.g., Primary, Secondary). '__c' denotes a custom field. Please provide a value of type string.""",
    )  # noqa: E501

    MailingCity: Optional[str] = Field(
        default=None,
        description="""Mailing address: City. Please provide a value of type string.""",
    )  # noqa: E501

    MailingCountry: Optional[str] = Field(
        default=None,
        description="""Mailing address: Country. Please provide a value of type string.""",
    )  # noqa: E501

    MailingGeocodeAccuracy: Optional[str] = Field(
        default=None,
        description="""Mailing address: Geocode accuracy. See Salesforce docs for geolocation compound fields. Please provide a value of type string.""",
    )  # noqa: E501

    MailingLatitude: Optional[int] = Field(
        default=None,
        description="""Mailing address: Latitude (-90 to 90, 15 decimal places). Use with MailingLongitude. Please provide a value of type integer.""",
    )  # noqa: E501

    MailingLongitude: Optional[int] = Field(
        default=None,
        description="""Mailing address: Longitude (-180 to 180, 15 decimal places). Use with MailingLatitude. Please provide a value of type integer.""",
    )  # noqa: E501

    MailingPostalCode: Optional[str] = Field(
        default=None,
        description="""Mailing address: Postal code. Please provide a value of type string.""",
    )  # noqa: E501

    MailingState: Optional[str] = Field(
        default=None,
        description="""Mailing address: State or province. Please provide a value of type string.""",
    )  # noqa: E501

    MailingStreet: Optional[str] = Field(
        default=None,
        description="""Mailing address: Street. Please provide a value of type string.""",
    )  # noqa: E501

    MasterRecordId: Optional[str] = Field(
        default=None,
        description="""Read-only: ID of the master record post-merge deletion; null otherwise. Please provide a value of type string.""",
    )  # noqa: E501

    MobilePhone: Optional[str] = Field(
        default=None,
        description="""Mobile phone. Please provide a value of type string.""",
    )  # noqa: E501

    Name: Optional[str] = Field(
        default=None,
        description="""Read-only: Full name, a concatenation of FirstName, MiddleName, LastName, and Suffix (up to 203 characters). Please provide a value of type string.""",
    )  # noqa: E501

    OtherCity: Optional[str] = Field(
        default=None,
        description="""Alternate address: City. Please provide a value of type string.""",
    )  # noqa: E501

    OtherCountry: Optional[str] = Field(
        default=None,
        description="""Alternate address: Country. Please provide a value of type string.""",
    )  # noqa: E501

    OtherGeocodeAccuracy: Optional[str] = Field(
        default=None,
        description="""Alternate address: Geocode accuracy. See Salesforce docs for geolocation compound fields. Please provide a value of type string.""",
    )  # noqa: E501

    OtherLatitude: Optional[int] = Field(
        default=None,
        description="""Alternate address: Latitude (-90 to 90, 15 decimal places). Use with OtherLongitude. Please provide a value of type integer.""",
    )  # noqa: E501

    OtherLongitude: Optional[int] = Field(
        default=None,
        description="""Alternate address: Longitude (-180 to 180, 15 decimal places). Use with OtherLatitude. Please provide a value of type integer.""",
    )  # noqa: E501

    OtherPhone: Optional[str] = Field(
        default=None,
        description="""Alternate address phone. Please provide a value of type string.""",
    )  # noqa: E501

    OtherPostalCode: Optional[str] = Field(
        default=None,
        description="""Alternate address: Postal code. Please provide a value of type string.""",
    )  # noqa: E501

    OtherState: Optional[str] = Field(
        default=None,
        description="""Alternate address: State or province. Please provide a value of type string.""",
    )  # noqa: E501

    OtherStreet: Optional[str] = Field(
        default=None,
        description="""Alternate address: Street. Please provide a value of type string.""",
    )  # noqa: E501

    OwnerId: Optional[str] = Field(
        default=None,
        description="""ID of the Salesforce user owning this contact. Defaults to the logged-in user if unspecified. Please provide a value of type string.""",
    )  # noqa: E501

    Phone: Optional[str] = Field(
        default=None,
        description="""Primary business phone. Label: Business Phone. Please provide a value of type string.""",
    )  # noqa: E501

    PhotoUrl: Optional[str] = Field(
        default=None,
        description="""Read-only: Path for social profile image URL (redirects). Empty if Social Accounts & Contacts disabled. Please provide a value of type string.""",
    )  # noqa: E501

    ReportsToId: Optional[str] = Field(
        default=None,
        description="""ID of manager contact reports to. Not for person accounts (IsPersonAccount true). Please provide a value of type string.""",
    )  # noqa: E501

    Salutation: Optional[str] = Field(
        default=None,
        description="""Honorific for the contact's name (e.g., Dr., Mr., Mrs.). Please provide a value of type string.""",
    )  # noqa: E501

    SystemModstamp: Optional[str] = Field(
        default=None,
        description="""Read-only: Timestamp of last system modification (user or automated). Please provide a value of type string.""",
    )  # noqa: E501

    Title: Optional[str] = Field(
        default=None,
        description="""Contact's title (e.g., CEO, Vice President). Please provide a value of type string.""",
    )  # noqa: E501

    attributes__type: Optional[str] = Field(
        default=None,
        description="""Salesforce SObject type, typically 'Contact'. Part of 'attributes' metadata. Please provide a value of type string.""",
    )  # noqa: E501

    attributes__url: Optional[str] = Field(
        default=None,
        description="""Relative URL for this SObject record, usually system-generated. Part of 'attributes' metadata. Please provide a value of type string.""",
    )  # noqa: E501


class CreateOpportunityRecordInput(BaseModel):
    """Input model for SALESFORCE_CREATE_OPPORTUNITY_RECORD"""

    AccountId: Optional[str] = Field(
        default=None,
        description="""ID of the linked Account. Often crucial for creating a valid opportunity. Please provide a value of type string.""",
    )  # noqa: E501

    Amount: Optional[int] = Field(
        default=None,
        description="""Estimated total sale amount. If products are involved, this may be auto-calculated, and direct updates might be ignored. Please provide a value of type integer.""",
    )  # noqa: E501

    CampaignId: Optional[str] = Field(
        default=None,
        description="""ID of the influencing Campaign. Ensure Campaign feature is enabled and ID is valid. Please provide a value of type string.""",
    )  # noqa: E501

    CloseDate: str = Field(
        description="""Expected close date (YYYY-MM-DD). Required. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    ContactId: Optional[str] = Field(
        default=None,
        description="""ID of the primary Contact. Set only during creation. Use OpportunityContactRole object to modify or add other contacts later. Please provide a value of type string.""",
    )  # noqa: E501

    CreatedById: Optional[str] = Field(
        default=None,
        description="""Read-only. ID of the user who created this record. Auto-set by Salesforce. Please provide a value of type string.""",
    )  # noqa: E501

    CreatedDate: Optional[str] = Field(
        default=None,
        description="""Read-only. Creation timestamp. Auto-set by Salesforce. Please provide a value of type string.""",
    )  # noqa: E501

    CurrentGenerators__c: Optional[str] = Field(
        default=None,
        description="""Custom field: Information on current generators. Please provide a value of type string.""",
    )  # noqa: E501

    DeliveryInstallationStatus__c: Optional[str] = Field(
        default=None,
        description="""Custom field: Delivery or installation status. Please provide a value of type string.""",
    )  # noqa: E501

    Description: Optional[str] = Field(
        default=None,
        description="""Detailed text description. Limit: 32,000 characters. Please provide a value of type string.""",
    )  # noqa: E501

    ExpectedRevenue: Optional[int] = Field(
        default=None,
        description="""Read-only. Calculated as Amount * Probability. Cannot be set during creation. Please provide a value of type integer.""",
    )  # noqa: E501

    Fiscal: Optional[str] = Field(
        default=None,
        description="""Fiscal period ('YYYY Q' format, e.g., '2024 1') based on CloseDate. Used if standard fiscal year settings not enabled. Often auto-derived. Please provide a value of type string.""",
    )  # noqa: E501

    FiscalQuarter: Optional[int] = Field(
        default=None,
        description="""Fiscal quarter (1-4) of CloseDate. Often auto-derived from CloseDate based on org's fiscal year settings. Please provide a value of type integer.""",
    )  # noqa: E501

    FiscalYear: Optional[int] = Field(
        default=None,
        description="""Fiscal year (e.g., 2024) of CloseDate. Often auto-derived from CloseDate based on org's fiscal year settings. Please provide a value of type integer.""",
    )  # noqa: E501

    ForecastCategory: Optional[str] = Field(
        default=None,
        description="""Forecast category (e.g., 'Pipeline', 'Best Case'). Often implied by StageName. For API v12.0+, typically set via ForecastCategoryName. Values depend on Salesforce configuration. Please provide a value of type string.""",
    )  # noqa: E501

    ForecastCategoryName: Optional[str] = Field(
        default=None,
        description="""Name of the forecast category (e.g., 'Pipeline'). API v12.0+. Often implied by StageName but can be overridden. Typically determines ForecastCategory. Please provide a value of type string.""",
    )  # noqa: E501

    HasOpenActivity: Optional[bool] = Field(
        default=None,
        description="""Read-only. Indicates if open activities (Events or Tasks) exist. API v35.0+. Please provide a value of type boolean.""",
    )  # noqa: E501

    HasOpportunityLineItem: Optional[bool] = Field(
        default=None,
        description="""Read-only. Indicates if associated line items (products) exist. System-managed; ignored during creation. Please provide a value of type boolean.""",
    )  # noqa: E501

    HasOverdueTask: Optional[bool] = Field(
        default=None,
        description="""Read-only. Indicates if overdue Tasks exist. API v35.0+. Please provide a value of type boolean.""",
    )  # noqa: E501

    Id: Optional[str] = Field(
        default=None,
        description="""System-generated unique identifier. Typically not provided during creation; providing it may be ignored or cause an error. Please provide a value of type string.""",
    )  # noqa: E501

    IsClosed: Optional[bool] = Field(
        default=None,
        description="""Read-only. Indicates if closed or open. Auto-set by Salesforce based on StageName; cannot be set on creation. Please provide a value of type boolean.""",
    )  # noqa: E501

    IsDeleted: Optional[bool] = Field(
        default=None,
        description="""Indicates if the record is in the Recycle Bin. Generally used for querying, not set during creation. Please provide a value of type boolean.""",
    )  # noqa: E501

    IsPrivate: Optional[bool] = Field(
        default=None,
        description="""If true, this opportunity is private and only visible to the owner and users with appropriate sharing access. Please provide a value of type boolean.""",
    )  # noqa: E501

    IsWon: Optional[bool] = Field(
        default=None,
        description="""Read-only. Indicates if won, lost, or open. Auto-set by Salesforce based on StageName; cannot be set on creation. Please provide a value of type boolean.""",
    )  # noqa: E501

    LastActivityDate: Optional[str] = Field(
        default=None,
        description="""Read-only. Date of the most recent activity (Event or Task). Not settable on creation. Please provide a value of type string.""",
    )  # noqa: E501

    LastAmountChangedHistoryId: Optional[str] = Field(
        default=None,
        description="""Read-only. ID of OpportunityHistory record tracking last Amount change (API v50.0+). Not settable on creation. Please provide a value of type string.""",
    )  # noqa: E501

    LastCloseDateChangedHistoryId: Optional[str] = Field(
        default=None,
        description="""Read-only. ID of OpportunityHistory record tracking last CloseDate change (API v50.0+). Not settable on creation. Please provide a value of type string.""",
    )  # noqa: E501

    LastModifiedById: Optional[str] = Field(
        default=None,
        description="""Read-only. ID of the user who last modified this record. Auto-set by Salesforce. Please provide a value of type string.""",
    )  # noqa: E501

    LastModifiedDate: Optional[str] = Field(
        default=None,
        description="""Read-only. Last modification timestamp. Auto-set by Salesforce. Please provide a value of type string.""",
    )  # noqa: E501

    LastReferencedDate: Optional[str] = Field(
        default=None,
        description="""Read-only. Timestamp of when current user last accessed this record or a related one. Not settable on creation. Please provide a value of type string.""",
    )  # noqa: E501

    LastStageChangeDate: Optional[str] = Field(
        default=None,
        description="""Read-only. Timestamp of last StageName change. Auto-set by Salesforce. Please provide a value of type string.""",
    )  # noqa: E501

    LastViewedDate: Optional[str] = Field(
        default=None,
        description="""Read-only. Timestamp of when current user last viewed this record. Not settable on creation. Please provide a value of type string.""",
    )  # noqa: E501

    LeadSource: Optional[str] = Field(
        default=None,
        description="""Lead or opportunity source (e.g., 'Web', 'Partner Referral'). Values depend on Salesforce configuration. Please provide a value of type string.""",
    )  # noqa: E501

    MainCompetitors__c: Optional[str] = Field(
        default=None,
        description="""Custom field: Identified main competitors. Please provide a value of type string.""",
    )  # noqa: E501

    Name: str = Field(
        description="""Descriptive name for the opportunity. Required. Limit: 120 characters. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    NextStep: Optional[str] = Field(
        default=None,
        description="""Next actionable step towards closing. Limit: 255 characters. Please provide a value of type string.""",
    )  # noqa: E501

    OrderNumber__c: Optional[str] = Field(
        default=None,
        description="""Custom field: Associated order number. Please provide a value of type string.""",
    )  # noqa: E501

    OwnerId: Optional[str] = Field(
        default=None,
        description="""ID of the User owning this opportunity. Defaults to creating user if unspecified (depending on settings). Ensure User ID is valid and active. Please provide a value of type string.""",
    )  # noqa: E501

    Pricebook2Id: Optional[str] = Field(
        default=None,
        description="""ID of the associated Price Book (Pricebook2). Generally required if adding products. Ensure products/price books are enabled and ID is valid. Please provide a value of type string.""",
    )  # noqa: E501

    Probability: Optional[int] = Field(
        default=None,
        description="""Likelihood (percentage, e.g., 75 for 75%) of closing. Often implied by StageName but can be overridden. Please provide a value of type integer.""",
    )  # noqa: E501

    PushCount: Optional[int] = Field(
        default=None,
        description="""Read-only. Used internally by Salesforce for mobile sync updates. Not user-settable. Please provide a value of type integer.""",
    )  # noqa: E501

    StageName: str = Field(
        description="""Current stage (e.g., 'Prospecting', 'Closed Won'). Required. May update ForecastCategoryName, IsClosed, IsWon, and Probability. Query OpportunityStage object or refer to Salesforce setup for valid names. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    SystemModstamp: Optional[str] = Field(
        default=None,
        description="""Read-only. Last system modification timestamp. Auto-set by Salesforce. Please provide a value of type string.""",
    )  # noqa: E501

    TotalOpportunityQuantity: Optional[int] = Field(
        default=None,
        description="""Total quantity of items (e.g., units, licenses). Used in quantity-based forecasting. Please provide a value of type integer.""",
    )  # noqa: E501

    TrackingNumber__c: Optional[str] = Field(
        default=None,
        description="""Custom field: Associated tracking number. Please provide a value of type string.""",
    )  # noqa: E501

    Type: Optional[str] = Field(
        default=None,
        description="""Opportunity type (e.g., 'New Business', 'Existing Customer'). Values depend on Salesforce configuration. Please provide a value of type string.""",
    )  # noqa: E501

    attributes__type: Optional[str] = Field(
        default=None,
        description="""SObject type for this record, typically 'Opportunity'. Please provide a value of type string.""",
    )  # noqa: E501

    attributes__url: Optional[str] = Field(
        default=None,
        description="""Relative URL for this Opportunity record. Please provide a value of type string.""",
    )  # noqa: E501


class DeleteALeadObjectByItsIdInput(BaseModel):
    """Input model for SALESFORCE_DELETE_A_LEAD_OBJECT_BY_ITS_ID"""

    id: str = Field(
        description="""The unique 15-character or 18-character ID of the Lead object to be deleted. Lead object IDs typically start with the prefix '00Q'. This is a required path parameter. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class FetchAccountByIdWithQueryInput(BaseModel):
    """Input model for SALESFORCE_FETCH_ACCOUNT_BY_ID_WITH_QUERY"""

    fields: Optional[str] = Field(
        default=None,
        description="""Optional comma-delimited list of Account field names to retrieve (e.g., 'Name,BillingCity,Industry'). If unspecified, null, or empty, all accessible Account fields are returned. Please provide a value of type string.""",
    )  # noqa: E501

    id: str = Field(
        description="""Unique identifier (ID) of the Salesforce Account to retrieve. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501
