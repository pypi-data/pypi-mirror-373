# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa
from typing import Any, Dict, List, Literal

from pydantic import BaseModel

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.composio_models import ComposioResult
from ..models.tools.salesforce_models import (
    AccountCreationWithContentTypeOptionInput,
    CreateCampaignRecordViaPostInput,
    CreateLeadWithSpecifiedContentTypeInput,
    CreateNewContactWithJsonHeaderInput,
    CreateNoteRecordWithContentTypeHeaderInput,
    CreateOpportunityRecordInput,
    DeleteALeadObjectByItsIdInput,
    ExecuteSoqlQueryInput,
    FetchAccountByIdWithQueryInput,
    FetchModifiedOrUnmodifiedSobjectsInput,
    QueryContactsByNameInput,
    RemoveAccountByUniqueIdentifierInput,
    RetrieveAccountDataAndErrorResponsesInput,
    RetrieveCampaignDataWithErrorHandlingInput,
    RetrieveLeadByIdInput,
    RetrieveLeadDataWithVariousResponsesInput,
    RetrieveOpportunitiesDataInput,
    RetrieveSpecificContactByIdInput,
    UpdateContactByIdInput,
)


__all__ = [
    "AccountCreationWithContentTypeOptionInput",
    "CreateCampaignRecordViaPostInput",
    "CreateLeadWithSpecifiedContentTypeInput",
    "CreateNewContactWithJsonHeaderInput",
    "CreateNoteRecordWithContentTypeHeaderInput",
    "CreateOpportunityRecordInput",
    "DeleteALeadObjectByItsIdInput",
    "ExecuteSoqlQueryInput",
    "FetchAccountByIdWithQueryInput",
    "FetchModifiedOrUnmodifiedSobjectsInput",
    "QueryContactsByNameInput",
    "RemoveAccountByUniqueIdentifierInput",
    "RetrieveAccountDataAndErrorResponsesInput",
    "RetrieveCampaignDataWithErrorHandlingInput",
    "RetrieveLeadByIdInput",
    "RetrieveLeadDataWithVariousResponsesInput",
    "RetrieveOpportunitiesDataInput",
    "RetrieveSpecificContactByIdInput",
    "UpdateContactByIdInput",
    "account_creation_with_content_type_option",
    "create_campaign_record_via_post",
    "create_lead_with_specified_content_type",
    "create_note_record_with_content_type_header",
    "execute_soql_query",
    "fetch_modified_or_unmodified_sobjects",
    "query_contacts_by_name",
    "remove_account_by_unique_identifier",
    "retrieve_account_data_and_error_responses",
    "retrieve_campaign_data_with_error_handling",
    "retrieve_lead_by_id",
    "retrieve_lead_data_with_various_responses",
    "retrieve_opportunities_data",
    "retrieve_specific_contact_by_id",
    "update_contact_by_id",
    "create_new_contact_with_json_header",
    "create_opportunity_record",
    "delete_a_lead_object_by_its_id",
    "fetch_account_by_id_with_query",
]


def account_creation_with_content_type_option(
    *,
    AccountNumber: str | None = DEFAULT,
    AccountSource: str | None = DEFAULT,
    Active__c: str | None = DEFAULT,
    AnnualRevenue: int | None = DEFAULT,
    BillingCity: str | None = DEFAULT,
    BillingCountry: str | None = DEFAULT,
    BillingGeocodeAccuracy: str | None = DEFAULT,
    BillingLatitude: int | None = DEFAULT,
    BillingLongitude: int | None = DEFAULT,
    BillingPostalCode: str | None = DEFAULT,
    BillingState: str | None = DEFAULT,
    BillingStreet: str | None = DEFAULT,
    CleanStatus: str | None = DEFAULT,
    CreatedById: str | None = DEFAULT,
    CreatedDate: str | None = DEFAULT,
    CustomerPriority__c: str | None = DEFAULT,
    DandbCompanyId: str | None = DEFAULT,
    Description: str | None = DEFAULT,
    DunsNumber: str | None = DEFAULT,
    Fax: str | None = DEFAULT,
    Id: str | None = DEFAULT,
    Industry: str | None = DEFAULT,
    IsDeleted: bool | None = DEFAULT,
    Jigsaw: str | None = DEFAULT,
    JigsawCompanyId: str | None = DEFAULT,
    LastActivityDate: str | None = DEFAULT,
    LastModifiedById: str | None = DEFAULT,
    LastModifiedDate: str | None = DEFAULT,
    LastReferencedDate: str | None = DEFAULT,
    LastViewedDate: str | None = DEFAULT,
    MasterRecordId: str | None = DEFAULT,
    NaicsCode: str | None = DEFAULT,
    NaicsDesc: str | None = DEFAULT,
    Name: str,
    NumberOfEmployees: int | None = DEFAULT,
    NumberofLocations__c: int | None = DEFAULT,
    OperatingHoursId: str | None = DEFAULT,
    OwnerId: str | None = DEFAULT,
    Ownership: str | None = DEFAULT,
    ParentId: str | None = DEFAULT,
    Phone: str | None = DEFAULT,
    PhotoUrl: str | None = DEFAULT,
    Rating: str | None = DEFAULT,
    SLAExpirationDate__c: str | None = DEFAULT,
    SLASerialNumber__c: str | None = DEFAULT,
    SLA__c: str | None = DEFAULT,
    ShippingCity: str | None = DEFAULT,
    ShippingCountry: str | None = DEFAULT,
    ShippingGeocodeAccuracy: str | None = DEFAULT,
    ShippingLatitude: int | None = DEFAULT,
    ShippingLongitude: int | None = DEFAULT,
    ShippingPostalCode: str | None = DEFAULT,
    ShippingState: str | None = DEFAULT,
    ShippingStreet: str | None = DEFAULT,
    Sic: str | None = DEFAULT,
    SicDesc: str | None = DEFAULT,
    Site: str | None = DEFAULT,
    SystemModstamp: str | None = DEFAULT,
    TickerSymbol: str | None = DEFAULT,
    Tradestyle: str | None = DEFAULT,
    Type: str | None = DEFAULT,
    UpsellOpportunity__c: str | None = DEFAULT,
    Website: str | None = DEFAULT,
    YearStarted: str | None = DEFAULT,
    attributes__type: str | None = DEFAULT,
    attributes__url: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Salesforce: Account Creation With Content Type Option"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = AccountCreationWithContentTypeOptionInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce",
        name="account_creation_with_content_type_option",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def create_campaign_record_via_post(
    *,
    ActualCost: int | None = DEFAULT,
    AmountAllOpportunities: int | None = DEFAULT,
    AmountWonOpportunities: int | None = DEFAULT,
    BudgetedCost: int | None = DEFAULT,
    CampaignMemberRecordTypeId: str | None = DEFAULT,
    CreatedById: str | None = DEFAULT,
    CreatedDate: str | None = DEFAULT,
    Description: str | None = DEFAULT,
    EndDate: str | None = DEFAULT,
    ExpectedResponse: int | None = DEFAULT,
    ExpectedRevenue: int | None = DEFAULT,
    Id: str | None = DEFAULT,
    IsActive: bool | None = DEFAULT,
    IsDeleted: bool | None = DEFAULT,
    LastActivityDate: str | None = DEFAULT,
    LastModifiedById: str | None = DEFAULT,
    LastModifiedDate: str | None = DEFAULT,
    LastReferencedDate: str | None = DEFAULT,
    LastViewedDate: str | None = DEFAULT,
    Name: str,
    NumberOfContacts: int | None = DEFAULT,
    NumberOfConvertedLeads: int | None = DEFAULT,
    NumberOfLeads: int | None = DEFAULT,
    NumberOfOpportunities: int | None = DEFAULT,
    NumberOfResponses: int | None = DEFAULT,
    NumberOfWonOpportunities: int | None = DEFAULT,
    NumberSent: int | None = DEFAULT,
    OwnerId: str | None = DEFAULT,
    ParentId: str | None = DEFAULT,
    StartDate: str | None = DEFAULT,
    Status: str | None = DEFAULT,
    SystemModstamp: str | None = DEFAULT,
    Type: str | None = DEFAULT,
    attributes__type: str | None = DEFAULT,
    attributes__url: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Salesforce: Create Campaign Record Via Post"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateCampaignRecordViaPostInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce",
        name="create_campaign_record_via_post",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def create_lead_with_specified_content_type(
    *,
    AnnualRevenue: int | None = DEFAULT,
    City: str | None = DEFAULT,
    CleanStatus: str | None = DEFAULT,
    Company: str,
    CompanyDunsNumber: str | None = DEFAULT,
    ConvertedAccountId: str | None = DEFAULT,
    ConvertedContactId: str | None = DEFAULT,
    ConvertedDate: str | None = DEFAULT,
    ConvertedOpportunityId: str | None = DEFAULT,
    Country: str | None = DEFAULT,
    CreatedById: str | None = DEFAULT,
    CreatedDate: str | None = DEFAULT,
    CurrentGenerators__c: str | None = DEFAULT,
    DandbCompanyId: str | None = DEFAULT,
    Description: str | None = DEFAULT,
    Email: str | None = DEFAULT,
    EmailBouncedDate: str | None = DEFAULT,
    EmailBouncedReason: str | None = DEFAULT,
    FirstName: str | None = DEFAULT,
    IndividualId: str | None = DEFAULT,
    Industry: str | None = DEFAULT,
    IsConverted: bool | None = DEFAULT,
    IsDeleted: bool | None = DEFAULT,
    IsPriorityRecord: bool | None = DEFAULT,
    IsUnreadByOwner: bool | None = DEFAULT,
    Jigsaw: str | None = DEFAULT,
    JigsawContactId: str | None = DEFAULT,
    LastActivityDate: str | None = DEFAULT,
    LastModifiedById: str | None = DEFAULT,
    LastModifiedDate: str | None = DEFAULT,
    LastName: str,
    LastReferencedDate: str | None = DEFAULT,
    LastViewedDate: str | None = DEFAULT,
    LeadSource: Literal[
        "Web", "Other", "Phone Inquiry", "Partner Referral", "Purchased List"
    ]
    | None = DEFAULT,
    MasterRecordId: str | None = DEFAULT,
    NumberOfEmployees: int | None = DEFAULT,
    NumberofLocations__c: int | None = DEFAULT,
    OwnerId: str | None = DEFAULT,
    Phone: str | None = DEFAULT,
    PhotoUrl: str | None = DEFAULT,
    PostalCode: str | None = DEFAULT,
    Primary__c: str | None = DEFAULT,
    ProductInterest__c: str | None = DEFAULT,
    Rating: str | None = DEFAULT,
    SICCode__c: str | None = DEFAULT,
    Salutation: Literal["Mr.", "Ms.", "Mrs.", "Dr.", "Prof."] | None = DEFAULT,
    State: str | None = DEFAULT,
    Status: str | None = DEFAULT,
    Street: str | None = DEFAULT,
    SystemModstamp: str | None = DEFAULT,
    Title: str | None = DEFAULT,
    Website: str | None = DEFAULT,
    attributes__type: str | None = DEFAULT,
    attributes__url: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Salesforce: Create Lead With Specified Content Type"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateLeadWithSpecifiedContentTypeInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce",
        name="create_lead_with_specified_content_type",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def create_note_record_with_content_type_header(
    *,
    Body: str,
    CreatedById: str | None = DEFAULT,
    CreatedDate: str | None = DEFAULT,
    Id: str | None = DEFAULT,
    IsDeleted: bool | None = DEFAULT,
    IsPrivate: bool | None = DEFAULT,
    LastModifiedById: str | None = DEFAULT,
    LastModifiedDate: str | None = DEFAULT,
    OwnerId: str | None = DEFAULT,
    ParentId: str,
    SystemModstamp: str | None = DEFAULT,
    Title: str,
    attributes__type: str | None = DEFAULT,
    attributes__url: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Salesforce: Create Note Record With Content Type Header"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateNoteRecordWithContentTypeHeaderInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce",
        name="create_note_record_with_content_type_header",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def execute_soql_query(*, soql_query: str) -> ComposioResult:
    """Execute Salesforce: Execute Soql Query"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ExecuteSoqlQueryInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce", name="execute_soql_query", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def fetch_modified_or_unmodified_sobjects(
    *, if_modified_since: str | None = DEFAULT, if_unmodified_since: str | None = DEFAULT
) -> ComposioResult:
    """Execute Salesforce: Fetch Modified Or Unmodified Sobjects"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = FetchModifiedOrUnmodifiedSobjectsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce",
        name="fetch_modified_or_unmodified_sobjects",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def query_contacts_by_name(
    *, contact_name: str, fields: str | None = DEFAULT, limit: int | None = DEFAULT
) -> ComposioResult:
    """Execute Salesforce: Query Contacts By Name"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = QueryContactsByNameInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce",
        name="query_contacts_by_name",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def remove_account_by_unique_identifier(*, id: str) -> ComposioResult:
    """Execute Salesforce: Remove Account By Unique Identifier"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = RemoveAccountByUniqueIdentifierInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce",
        name="remove_account_by_unique_identifier",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def retrieve_account_data_and_error_responses() -> ComposioResult:
    """Execute Salesforce: Retrieve Account Data And Error Responses"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = RetrieveAccountDataAndErrorResponsesInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce",
        name="retrieve_account_data_and_error_responses",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def retrieve_campaign_data_with_error_handling() -> ComposioResult:
    """Execute Salesforce: Retrieve Campaign Data With Error Handling"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = RetrieveCampaignDataWithErrorHandlingInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce",
        name="retrieve_campaign_data_with_error_handling",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def retrieve_lead_by_id(*, fields: str | None = DEFAULT, id: str) -> ComposioResult:
    """Execute Salesforce: Retrieve Lead By Id"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = RetrieveLeadByIdInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce", name="retrieve_lead_by_id", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def retrieve_lead_data_with_various_responses() -> ComposioResult:
    """Execute Salesforce: Retrieve Lead Data With Various Responses"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = RetrieveLeadDataWithVariousResponsesInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce",
        name="retrieve_lead_data_with_various_responses",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def retrieve_opportunities_data() -> ComposioResult:
    """Execute Salesforce: Retrieve Opportunities Data"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = RetrieveOpportunitiesDataInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce",
        name="retrieve_opportunities_data",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def retrieve_specific_contact_by_id(
    *, fields: str | None = DEFAULT, id: str
) -> ComposioResult:
    """Execute Salesforce: Retrieve Specific Contact By Id"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = RetrieveSpecificContactByIdInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce",
        name="retrieve_specific_contact_by_id",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def update_contact_by_id(
    *,
    AccountId: str | None = DEFAULT,
    AssistantName: str | None = DEFAULT,
    AssistantPhone: str | None = DEFAULT,
    Birthdate: str | None = DEFAULT,
    CleanStatus: str | None = DEFAULT,
    ContactSource: str | None = DEFAULT,
    CreatedById: str | None = DEFAULT,
    CreatedDate: str | None = DEFAULT,
    Department: str | None = DEFAULT,
    Description: str | None = DEFAULT,
    Email: str | None = DEFAULT,
    EmailBouncedDate: str | None = DEFAULT,
    EmailBouncedReason: str | None = DEFAULT,
    Fax: str | None = DEFAULT,
    FirstName: str | None = DEFAULT,
    HomePhone: str | None = DEFAULT,
    Id: str | None = DEFAULT,
    IndividualId: str | None = DEFAULT,
    IsDeleted: bool | None = DEFAULT,
    IsEmailBounced: bool | None = DEFAULT,
    IsPriorityRecord: bool | None = DEFAULT,
    Jigsaw: str | None = DEFAULT,
    JigsawContactId: str | None = DEFAULT,
    Languages__c: str | None = DEFAULT,
    LastActivityDate: str | None = DEFAULT,
    LastCURequestDate: str | None = DEFAULT,
    LastCUUpdateDate: str | None = DEFAULT,
    LastModifiedById: str | None = DEFAULT,
    LastModifiedDate: str | None = DEFAULT,
    LastName: str | None = DEFAULT,
    LastReferencedDate: str | None = DEFAULT,
    LastViewedDate: str | None = DEFAULT,
    LeadSource: str | None = DEFAULT,
    Level__c: str | None = DEFAULT,
    MailingCity: str | None = DEFAULT,
    MailingCountry: str | None = DEFAULT,
    MailingGeocodeAccuracy: str | None = DEFAULT,
    MailingLatitude: int | None = DEFAULT,
    MailingLongitude: int | None = DEFAULT,
    MailingPostalCode: str | None = DEFAULT,
    MailingState: str | None = DEFAULT,
    MailingStreet: str | None = DEFAULT,
    MasterRecordId: str | None = DEFAULT,
    MobilePhone: str | None = DEFAULT,
    Name: str | None = DEFAULT,
    OtherCity: str | None = DEFAULT,
    OtherCountry: str | None = DEFAULT,
    OtherGeocodeAccuracy: str | None = DEFAULT,
    OtherLatitude: int | None = DEFAULT,
    OtherLongitude: int | None = DEFAULT,
    OtherPhone: str | None = DEFAULT,
    OtherPostalCode: str | None = DEFAULT,
    OtherState: str | None = DEFAULT,
    OtherStreet: str | None = DEFAULT,
    OwnerId: str | None = DEFAULT,
    Phone: str | None = DEFAULT,
    PhotoUrl: str | None = DEFAULT,
    ReportsToId: str | None = DEFAULT,
    Salutation: str | None = DEFAULT,
    SystemModstamp: str | None = DEFAULT,
    Title: str | None = DEFAULT,
    attributes__type: str | None = DEFAULT,
    attributes__url: str | None = DEFAULT,
    id: str,
) -> ComposioResult:
    """Execute Salesforce: Update Contact By Id"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = UpdateContactByIdInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce", name="update_contact_by_id", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def create_new_contact_with_json_header(
    *,
    AccountId: str | None = DEFAULT,
    AssistantName: str | None = DEFAULT,
    AssistantPhone: str | None = DEFAULT,
    Birthdate: str | None = DEFAULT,
    CleanStatus: str | None = DEFAULT,
    ContactSource: str | None = DEFAULT,
    CreatedById: str | None = DEFAULT,
    CreatedDate: str | None = DEFAULT,
    Department: str | None = DEFAULT,
    Description: str | None = DEFAULT,
    Email: str | None = DEFAULT,
    EmailBouncedDate: str | None = DEFAULT,
    EmailBouncedReason: str | None = DEFAULT,
    Fax: str | None = DEFAULT,
    FirstName: str | None = DEFAULT,
    HomePhone: str | None = DEFAULT,
    Id: str | None = DEFAULT,
    IndividualId: str | None = DEFAULT,
    IsDeleted: bool | None = DEFAULT,
    IsEmailBounced: bool | None = DEFAULT,
    IsPriorityRecord: bool | None = DEFAULT,
    Jigsaw: str | None = DEFAULT,
    JigsawContactId: str | None = DEFAULT,
    Languages__c: str | None = DEFAULT,
    LastActivityDate: str | None = DEFAULT,
    LastCURequestDate: str | None = DEFAULT,
    LastCUUpdateDate: str | None = DEFAULT,
    LastModifiedById: str | None = DEFAULT,
    LastModifiedDate: str | None = DEFAULT,
    LastName: str,
    LastReferencedDate: str | None = DEFAULT,
    LastViewedDate: str | None = DEFAULT,
    LeadSource: str | None = DEFAULT,
    Level__c: str | None = DEFAULT,
    MailingCity: str | None = DEFAULT,
    MailingCountry: str | None = DEFAULT,
    MailingGeocodeAccuracy: str | None = DEFAULT,
    MailingLatitude: int | None = DEFAULT,
    MailingLongitude: int | None = DEFAULT,
    MailingPostalCode: str | None = DEFAULT,
    MailingState: str | None = DEFAULT,
    MailingStreet: str | None = DEFAULT,
    MasterRecordId: str | None = DEFAULT,
    MobilePhone: str | None = DEFAULT,
    Name: str | None = DEFAULT,
    OtherCity: str | None = DEFAULT,
    OtherCountry: str | None = DEFAULT,
    OtherGeocodeAccuracy: str | None = DEFAULT,
    OtherLatitude: int | None = DEFAULT,
    OtherLongitude: int | None = DEFAULT,
    OtherPhone: str | None = DEFAULT,
    OtherPostalCode: str | None = DEFAULT,
    OtherState: str | None = DEFAULT,
    OtherStreet: str | None = DEFAULT,
    OwnerId: str | None = DEFAULT,
    Phone: str | None = DEFAULT,
    PhotoUrl: str | None = DEFAULT,
    ReportsToId: str | None = DEFAULT,
    Salutation: str | None = DEFAULT,
    SystemModstamp: str | None = DEFAULT,
    Title: str | None = DEFAULT,
    attributes__type: str | None = DEFAULT,
    attributes__url: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Salesforce: Create New Contact With Json Header"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateNewContactWithJsonHeaderInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce",
        name="create_new_contact_with_json_header",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def create_opportunity_record(
    *,
    AccountId: str | None = DEFAULT,
    Amount: int | None = DEFAULT,
    CampaignId: str | None = DEFAULT,
    CloseDate: str,
    ContactId: str | None = DEFAULT,
    CreatedById: str | None = DEFAULT,
    CreatedDate: str | None = DEFAULT,
    CurrentGenerators__c: str | None = DEFAULT,
    DeliveryInstallationStatus__c: str | None = DEFAULT,
    Description: str | None = DEFAULT,
    ExpectedRevenue: int | None = DEFAULT,
    Fiscal: str | None = DEFAULT,
    FiscalQuarter: int | None = DEFAULT,
    FiscalYear: int | None = DEFAULT,
    ForecastCategory: str | None = DEFAULT,
    ForecastCategoryName: str | None = DEFAULT,
    HasOpenActivity: bool | None = DEFAULT,
    HasOpportunityLineItem: bool | None = DEFAULT,
    HasOverdueTask: bool | None = DEFAULT,
    Id: str | None = DEFAULT,
    IsClosed: bool | None = DEFAULT,
    IsDeleted: bool | None = DEFAULT,
    IsPrivate: bool | None = DEFAULT,
    IsWon: bool | None = DEFAULT,
    LastActivityDate: str | None = DEFAULT,
    LastAmountChangedHistoryId: str | None = DEFAULT,
    LastCloseDateChangedHistoryId: str | None = DEFAULT,
    LastModifiedById: str | None = DEFAULT,
    LastModifiedDate: str | None = DEFAULT,
    LastReferencedDate: str | None = DEFAULT,
    LastStageChangeDate: str | None = DEFAULT,
    LastViewedDate: str | None = DEFAULT,
    LeadSource: str | None = DEFAULT,
    MainCompetitors__c: str | None = DEFAULT,
    Name: str,
    NextStep: str | None = DEFAULT,
    OrderNumber__c: str | None = DEFAULT,
    OwnerId: str | None = DEFAULT,
    Pricebook2Id: str | None = DEFAULT,
    Probability: int | None = DEFAULT,
    PushCount: int | None = DEFAULT,
    StageName: str,
    SystemModstamp: str | None = DEFAULT,
    TotalOpportunityQuantity: int | None = DEFAULT,
    TrackingNumber__c: str | None = DEFAULT,
    Type: str | None = DEFAULT,
    attributes__type: str | None = DEFAULT,
    attributes__url: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Salesforce: Create Opportunity Record"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateOpportunityRecordInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce",
        name="create_opportunity_record",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def delete_a_lead_object_by_its_id(*, id: str) -> ComposioResult:
    """Execute Salesforce: Delete A Lead Object By Its Id"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = DeleteALeadObjectByItsIdInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce",
        name="delete_a_lead_object_by_its_id",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def fetch_account_by_id_with_query(
    *, fields: str | None = DEFAULT, id: str
) -> ComposioResult:
    """Execute Salesforce: Fetch Account By Id With Query"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = FetchAccountByIdWithQueryInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="salesforce",
        name="fetch_account_by_id_with_query",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)
