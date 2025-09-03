from dataclasses import dataclass
from pathlib import Path
from typing import Any

from htmldict import HTMLDict
from jinja2 import Environment, FileSystemLoader

CWD = Path(__file__).parent
TEMPLATES = CWD / "templates"
CWD_TEMPLATER = Environment(loader=FileSystemLoader(TEMPLATES))


class Email(HTMLDict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    id: str
    subject: str
    body: dict
    sender: dict

    # Recipients
    toRecipients: list
    ccRecipients: list
    bccRecipients: list

    # Timestamps
    receivedDateTime: str
    sentDateTime: str

    # Metadata
    isRead: bool
    hasAttachments: bool
    importance: str
    isDraft: bool
    conversationId: str
    conversationIndex: str
    webLink: str
    internetMessageId: str

    @property
    def view(self):
        template = CWD_TEMPLATER.get_template("email.html")
        return template.render(**self)


class Person(HTMLDict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Core identification
    id: str
    displayName: str
    givenName: str
    surname: str
    userPrincipalName: str

    # Contact information
    scoredEmailAddresses: list
    phones: list
    postalAddresses: list
    websites: list
    imAddress: str

    # Professional information
    jobTitle: str
    companyName: str
    yomiCompany: str
    department: str
    officeLocation: str
    profession: str

    # Personal information
    birthday: str
    personNotes: str
    isFavorite: bool

    # Classification
    personType: dict

    @property
    def primary_email(self):
        """Get the primary email address with highest relevance score"""
        if not self.scoredEmailAddresses:
            return None

        # Sort by relevance score and return the highest
        sorted_emails = sorted(
            self.scoredEmailAddresses,
            key=lambda x: x.get('relevanceScore', 0),
            reverse=True
        )
        return sorted_emails[0]['address']

    @property
    def relevance_score(self):
        """Get the highest relevance score for this person"""
        if not self.scoredEmailAddresses:
            return 0

        return max(email.get('relevanceScore', 0) for email in self.scoredEmailAddresses)

    @property
    def person_class(self):
        """Get the person class (Person, Group, etc.)"""
        return self.personType.get('class', 'Unknown') if self.personType else 'Unknown'

    @property
    def person_subclass(self):
        """Get the person subclass (OrganizationUser, UnifiedGroup, etc.)"""
        return self.personType.get('subclass', 'Unknown') if self.personType else 'Unknown'

    @property
    def is_group(self):
        """Check if this is a group rather than an individual person"""
        return self.person_class == 'Group'

    @property
    def is_organization_user(self):
        """Check if this is an organization user"""
        return self.person_subclass == 'OrganizationUser'

    @property
    def full_name(self):
        """Get the full name, falling back to displayName if givenName/surname not available"""
        if self.givenName and self.surname:
            return f"{self.givenName} {self.surname}"
        return self.displayName or "Unknown"

    @property
    def business_phone(self):
        """Get the primary business phone number"""
        if not self.phones:
            return None

        # Look for business phone first
        for phone in self.phones:
            if phone.get('type') == 'business':
                return phone.get('number')

        # Fall back to first available phone
        return self.phones[0].get('number') if self.phones else None

    @property
    def contact_summary(self):
        """Get a summary of contact information"""
        summary = {
            'name': self.full_name,
            'email': self.primary_email,
            'phone': self.business_phone,
            'title': self.jobTitle,
            'department': self.department,
            'company': self.companyName,
            'office': self.officeLocation,
            'type': self.person_class,
            'relevance': self.relevance_score
        }
        return {k: v for k, v in summary.items() if v}  # Remove None/empty values

    @property
    def view(self):
        """Render the person as HTML"""
        template = CWD_TEMPLATER.get_template("person.html")
        return template.render(contact_summary=self.contact_summary)

    def __str__(self):
        return f"{self.full_name} ({self.primary_email})"

    def __repr__(self):
        return f"Person(name='{self.full_name}', email='{self.primary_email}', type='{self.person_class}')"


class Me(HTMLDict):
    businessPhones: Any
    displayName: str
    givenName: str
    jobTitle: str
    mail: str
    mobilePhone: Any
    officeLocation: Any
    preferredLanguage: Any
    surname: str
    userPrincipalName: Any
    id: str

class Organization(HTMLDict):
    id: str
    deletedDateTime: Any
    businessPhones: Any
    city: Any
    country: Any
    countryLetterCode: Any
    createdDateTime: Any
    defaultUsageLocation: Any
    displayName: str
    isMultipleDataLocationsForServicesEnabled: Any
    marketingNotificationEmails: Any
    onPremisesLastSyncDateTime: Any
    onPremisesSyncEnabled: Any
    partnerTenantType: Any
    postalCode: Any
    preferredLanguage: Any
    securityComplianceNotificationMails: Any
    securityComplianceNotificationPhones: Any
    state: Any
    street: Any
    technicalNotificationMails: Any
    tenantType: str
    directorySizeQuota: Any
    privacyProfile: Any
    assignedPlans: Any
    onPremisesSyncStatus: Any
    provisionedPlans: Any
    verifiedDomains: Any


if __name__ == "__main__":
    email = {
        "@odata.etag": "W/\"CQAAABYAAADUwywT0x3WRJXfefGC8Xz/AAAwMhC1\"",
        "id": "AAMkADY1YmE3N2FhLWEwMzQtNDNkMC04Mzg3LTczMTdiMjk2NzRhMABGAAAAAADfsy0XtCMZS5XonZkyBLu6BwDUwywT0x3WRJXfefGC8Xz-AAAAAAEMAADUwywT0x3WRJXfefGC8Xz-AAAwQqIDAAA=",
        "createdDateTime": "2025-08-17T16:10:54Z",
        "lastModifiedDateTime": "2025-08-17T16:10:57Z",
        "changeKey": "CQAAABYAAADUwywT0x3WRJXfefGC8Xz/AAAwMhC1",
        "categories": [],
        "receivedDateTime": "2025-08-17T16:10:55Z",
        "sentDateTime": "2025-08-17T16:10:48Z",
        "hasAttachments": True,
        "internetMessageId": "<PlannerDueDate-4b3131a8-204c-4e0f-bfe0-1c2d12204f08-07ac8934-68b5-48d7-9e49-565862568fbc-r0-SendEmail-rh_cac-aid_ecacb0a7-6b24-406f-9435-7d50d8a98396@odspnotify>",
        "subject": "You have upcoming tasks due",
        "bodyPreview": "Hi Adele. You have 4 tasks due.\r\n        You have upcoming tasks\r\nOrder Patti Smoothie Stuff\r\nIn the plan  PattiF Logistics\r\n8/21/2025\r\nDue in 4 days\r\nStockReport AM\r\nIn the plan  PattiF Logistics\r\n8/24/2025\r\nDue in 7 days\r\nOrder Patti Smoothie Stuff\r\nIn ",
        "importance": "normal",
        "parentFolderId": "AAMkADY1YmE3N2FhLWEwMzQtNDNkMC04Mzg3LTczMTdiMjk2NzRhMAAuAAAAAADfsy0XtCMZS5XonZkyBLu6AQDUwywT0x3WRJXfefGC8Xz-AAAAAAEMAAA=",
        "conversationId": "AAQkADY1YmE3N2FhLWEwMzQtNDNkMC04Mzg3LTczMTdiMjk2NzRhMAAQAFFgHZ3kJEhGhBClnEVyKSM=",
        "conversationIndex": "AQHcD5GCUWAdneQkSEaEEKWcRXIpIw==",
        "isDeliveryReceiptRequested": "null",
        "isReadReceiptRequested": False,
        "isRead": False,
        "isDraft": False,
        "webLink": "https://outlook.office365.com/owa/?ItemID=AAMkADY1YmE3N2FhLWEwMzQtNDNkMC04Mzg3LTczMTdiMjk2NzRhMABGAAAAAADfsy0XtCMZS5XonZkyBLu6BwDUwywT0x3WRJXfefGC8Xz%2FAAAAAAEMAADUwywT0x3WRJXfefGC8Xz%2FAAAwQqIDAAA%3D&exvsurl=1&viewmodel=ReadMessageItem",
        "inferenceClassification": "focused",
        "body": {
            "contentType": "html",
            "content": "<html dir=\"ltr\" lang=\"en-us\"><head>\r\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"><style type=\"text/css\">\r\n<!--\r\n.headerBackgroundMsoTable\r\n\t{border-spacing:0px;\r\n\twidth:100%}\r\n-->\r\n</style></head><body style=\"margin:0px\"><div><table height=\"100%\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"border-spacing:0px\"><tbody><tr><td valign=\"top\" align=\"center\"><table align=\"center\" style=\"border-spacing:0px; width:100%!important; margin-right:auto; margin-left:auto; margin:0 auto; max-width:640px; font-family:'Segoe UI'; border:1px solid rgba(128,128,128,0.25); border-radius:4px\"><tbody><tr><td align=\"left\" style=\"padding:0px; margin:0px\"><table cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"border-spacing:0px; width:100%\"><tbody><tr><td align=\"center\"><div><table cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"border-spacing:0px; width:100%\"><tbody><tr><td colspan=\"1\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"width:100%\"><tbody><tr><td style=\"padding:32px\"><span style=\"font-family:'Segoe UI',sans-serif; font-weight:600; font-size:20px; color:#242424\">Hi Adele. You have 4 tasks due. </span></td></tr></tbody></table></td></tr></tbody></table></div></td></tr></tbody></table></td></tr><tr><td align=\"left\" style=\"padding:0px; margin:0px\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"width:100%; border-top:1px solid #E1DFDD; border-bottom:1px solid #E1DFDD; border-top:1px solid rgba(128,128,128,0.25); border-bottom:1px solid rgba(128,128,128,0.25)\"><tbody><tr><td style=\"padding:12px 32px 4px; background-color:#FAFAFA\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"width:100%\"><tbody><tr><td style=\"padding:11px 0 3px\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"width:100%\"><tbody><tr><td style=\"width:35px\"><img src=\"cid:39db5c79-1075-4204-b9d3-3fe9f1612786\" alt=\"Calendar Late\" width=\"30\" height=\"30\" border=\"0\" style=\"display:block; outline:none; border:none\"> </td><td><span style=\"font-family:'Segoe UI',sans-serif; font-weight:400; font-size:14px; color:#1B1A19\">You have <b>upcoming</b> tasks </span></td></tr></tbody></table></td></tr><tr><td style=\"padding:4px 0\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"width:100%; background-color:white; border:1px solid #E1DFDD; border:1px solid rgba(128,128,128,0.25); border-radius:4px\"><tbody><tr><td style=\"padding:12px 24px\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\"><tbody><tr><td style=\"padding:4px 0\"><a href=\"https://planner.cloud.microsoft/M365x63639251.onmicrosoft.com/en-US/Home/PlanViews/vTzrU8ilDEe2WnZp3wobLGUAEek-/B3HAH6m0UU6UgIREFNISfWUAK19q?Type=DueDate&amp;Channel=OdspNotify&amp;CreatedTime=638910438461558695\" data-loopstyle=\"{'link'}\" style=\"font-family:'Segoe UI',sans-serif; font-weight:600; font-size:14px; line-height:20px; color:#1B1A19; text-decoration:underline\">Order Patti Smoothie Stuff</a></td></tr><tr><td style=\"padding:4px 0\"><span style=\"font-family:'Segoe UI',sans-serif; font-weight:400; font-size:12px; line-height:20px; color:#605E5C\">In the plan <span style=\"\"><img src=\"cid:de059845-fa2a-4c03-b6a7-3ca94a6bd769\" alt=\"Planner\" width=\"20\" height=\"20\" border=\"0\" style=\"display:inline-block; vertical-align:bottom; border:none\"></span> <a href=\"https://planner.cloud.microsoft/M365x63639251.onmicrosoft.com/en-US/Home/PlanViews/vTzrU8ilDEe2WnZp3wobLGUAEek-?Type=DueDate&amp;Channel=OdspNotify&amp;CreatedTime=638910438461558695\" data-loopstyle=\"{'link'}\" style=\"color:#1B1A19; text-decoration:underline\">PattiF Logistics</a></span></td></tr><tr><td style=\"padding:4px 0\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\"><tbody><tr><td><img src=\"cid:d9f98195-47b4-4900-a2d7-0dedf83dda5d\" alt=\"Calendar\" width=\"16\" height=\"16\" border=\"0\" style=\"display:block; outline:none; border:none\"></td><td style=\"padding:0 4px\"><span style=\"font-family:'Segoe UI',sans-serif; font-weight:400; font-size:12px; line-height:20px; color:#1B1A19\">8/21/2025</span></td><td style=\"padding:0 8px\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"border-radius:12px; background-color:#EDEBE9\"><tbody><tr><td style=\"padding:0 10px\"><span style=\"font-family:'Segoe UI',sans-serif; font-weight:400; font-size:12px; line-height:20px; color:#323130\">Due in 4 days</span></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></td></tr><tr><td style=\"padding:4px 0\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"width:100%; background-color:white; border:1px solid #E1DFDD; border:1px solid rgba(128,128,128,0.25); border-radius:4px\"><tbody><tr><td style=\"padding:12px 24px\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\"><tbody><tr><td style=\"padding:4px 0\"><a href=\"https://planner.cloud.microsoft/M365x63639251.onmicrosoft.com/en-US/Home/PlanViews/vTzrU8ilDEe2WnZp3wobLGUAEek-/Q16nIEnVI0a4lTZZ79wa32UAAu7z?Type=DueDate&amp;Channel=OdspNotify&amp;CreatedTime=638910438461558695\" data-loopstyle=\"{'link'}\" style=\"font-family:'Segoe UI',sans-serif; font-weight:600; font-size:14px; line-height:20px; color:#1B1A19; text-decoration:underline\">StockReport AM</a></td></tr><tr><td style=\"padding:4px 0\"><span style=\"font-family:'Segoe UI',sans-serif; font-weight:400; font-size:12px; line-height:20px; color:#605E5C\">In the plan <span style=\"\"><img src=\"cid:de059845-fa2a-4c03-b6a7-3ca94a6bd769\" alt=\"Planner\" width=\"20\" height=\"20\" border=\"0\" style=\"display:inline-block; vertical-align:bottom; border:none\"></span> <a href=\"https://planner.cloud.microsoft/M365x63639251.onmicrosoft.com/en-US/Home/PlanViews/vTzrU8ilDEe2WnZp3wobLGUAEek-?Type=DueDate&amp;Channel=OdspNotify&amp;CreatedTime=638910438461558695\" data-loopstyle=\"{'link'}\" style=\"color:#1B1A19; text-decoration:underline\">PattiF Logistics</a></span></td></tr><tr><td style=\"padding:4px 0\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\"><tbody><tr><td><img src=\"cid:d9f98195-47b4-4900-a2d7-0dedf83dda5d\" alt=\"Calendar\" width=\"16\" height=\"16\" border=\"0\" style=\"display:block; outline:none; border:none\"></td><td style=\"padding:0 4px\"><span style=\"font-family:'Segoe UI',sans-serif; font-weight:400; font-size:12px; line-height:20px; color:#1B1A19\">8/24/2025</span></td><td style=\"padding:0 8px\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"border-radius:12px; background-color:#EDEBE9\"><tbody><tr><td style=\"padding:0 10px\"><span style=\"font-family:'Segoe UI',sans-serif; font-weight:400; font-size:12px; line-height:20px; color:#323130\">Due in 7 days</span></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></td></tr><tr><td style=\"padding:4px 0\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"width:100%; background-color:white; border:1px solid #E1DFDD; border:1px solid rgba(128,128,128,0.25); border-radius:4px\"><tbody><tr><td style=\"padding:12px 24px\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\"><tbody><tr><td style=\"padding:4px 0\"><a href=\"https://planner.cloud.microsoft/M365x63639251.onmicrosoft.com/en-US/Home/PlanViews/b6hxKqWKRUu3hFkrHFHtN2UABAqt/bbdxY3fGVEKZxL-HYK35YGUACWL9?Type=DueDate&amp;Channel=OdspNotify&amp;CreatedTime=638910438461558695\" data-loopstyle=\"{'link'}\" style=\"font-family:'Segoe UI',sans-serif; font-weight:600; font-size:14px; line-height:20px; color:#1B1A19; text-decoration:underline\">Order Patti Smoothie Stuff</a></td></tr><tr><td style=\"padding:4px 0\"><span style=\"font-family:'Segoe UI',sans-serif; font-weight:400; font-size:12px; line-height:20px; color:#605E5C\">In the plan <span style=\"\"><img src=\"cid:de059845-fa2a-4c03-b6a7-3ca94a6bd769\" alt=\"Planner\" width=\"20\" height=\"20\" border=\"0\" style=\"display:inline-block; vertical-align:bottom; border:none\"></span> <a href=\"https://planner.cloud.microsoft/M365x63639251.onmicrosoft.com/en-US/Home/PlanViews/b6hxKqWKRUu3hFkrHFHtN2UABAqt?Type=DueDate&amp;Channel=OdspNotify&amp;CreatedTime=638910438461558695\" data-loopstyle=\"{'link'}\" style=\"color:#1B1A19; text-decoration:underline\">Logistics</a></span></td></tr><tr><td style=\"padding:4px 0\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\"><tbody><tr><td><img src=\"cid:d9f98195-47b4-4900-a2d7-0dedf83dda5d\" alt=\"Calendar\" width=\"16\" height=\"16\" border=\"0\" style=\"display:block; outline:none; border:none\"></td><td style=\"padding:0 4px\"><span style=\"font-family:'Segoe UI',sans-serif; font-weight:400; font-size:12px; line-height:20px; color:#1B1A19\">8/21/2025</span></td><td style=\"padding:0 8px\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"border-radius:12px; background-color:#EDEBE9\"><tbody><tr><td style=\"padding:0 10px\"><span style=\"font-family:'Segoe UI',sans-serif; font-weight:400; font-size:12px; line-height:20px; color:#323130\">Due in 4 days</span></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></td></tr><tr><td style=\"padding:4px 0\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"width:100%; background-color:white; border:1px solid #E1DFDD; border:1px solid rgba(128,128,128,0.25); border-radius:4px\"><tbody><tr><td style=\"padding:12px 24px\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\"><tbody><tr><td style=\"padding:4px 0\"><a href=\"https://planner.cloud.microsoft/M365x63639251.onmicrosoft.com/en-US/Home/PlanViews/b6hxKqWKRUu3hFkrHFHtN2UABAqt/rZ3tUfiphUS5NMB8HoeKz2UAMaev?Type=DueDate&amp;Channel=OdspNotify&amp;CreatedTime=638910438461558695\" data-loopstyle=\"{'link'}\" style=\"font-family:'Segoe UI',sans-serif; font-weight:600; font-size:14px; line-height:20px; color:#1B1A19; text-decoration:underline\">StockReport AM</a></td></tr><tr><td style=\"padding:4px 0\"><span style=\"font-family:'Segoe UI',sans-serif; font-weight:400; font-size:12px; line-height:20px; color:#605E5C\">In the plan <span style=\"\"><img src=\"cid:de059845-fa2a-4c03-b6a7-3ca94a6bd769\" alt=\"Planner\" width=\"20\" height=\"20\" border=\"0\" style=\"display:inline-block; vertical-align:bottom; border:none\"></span> <a href=\"https://planner.cloud.microsoft/M365x63639251.onmicrosoft.com/en-US/Home/PlanViews/b6hxKqWKRUu3hFkrHFHtN2UABAqt?Type=DueDate&amp;Channel=OdspNotify&amp;CreatedTime=638910438461558695\" data-loopstyle=\"{'link'}\" style=\"color:#1B1A19; text-decoration:underline\">Logistics</a></span></td></tr><tr><td style=\"padding:4px 0\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\"><tbody><tr><td><img src=\"cid:d9f98195-47b4-4900-a2d7-0dedf83dda5d\" alt=\"Calendar\" width=\"16\" height=\"16\" border=\"0\" style=\"display:block; outline:none; border:none\"></td><td style=\"padding:0 4px\"><span style=\"font-family:'Segoe UI',sans-serif; font-weight:400; font-size:12px; line-height:20px; color:#1B1A19\">8/24/2025</span></td><td style=\"padding:0 8px\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"border-radius:12px; background-color:#EDEBE9\"><tbody><tr><td style=\"padding:0 10px\"><span style=\"font-family:'Segoe UI',sans-serif; font-weight:400; font-size:12px; line-height:20px; color:#323130\">Due in 7 days</span></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></td></tr><tr><td style=\"padding:20px 0\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\"><tbody><tr><td><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\"><tbody><tr><td align=\"center\" style=\"padding:6px 20px 6px 20px; border:1px solid #E1DFDD; border-radius:4px; background-color:#5B5FC7; box-shadow:0px 0px 4px rgba(0,0,0,0.09)\"><a href=\"https://planner.cloud.microsoft/M365x63639251.onmicrosoft.com/en-US/Home/MyTasks?Type=DueDate&amp;Channel=OdspNotify&amp;CreatedTime=638910438461558695\" target=\"_blank\"><strong style=\"display:inline-block; font-weight:600; font-size:14px; font-family:&quot;Segoe UI&quot;,sans-serif; line-height:20px; color:#ffffff; text-decoration:none\">Open in Browser </strong></a></td></tr></tbody></table></td><td style=\"padding-left:10px; padding-right:10px\"><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\"><tbody><tr><td align=\"center\" style=\"padding:6px 20px 6px 20px; border:1px solid #E1DFDD; border-radius:4px; background-color:#ffffff; box-shadow:0px 0px 4px rgba(0,0,0,0.09)\"><a href=\"https://teams.microsoft.com/l/entity/com.microsoft.teamspace.tab.planner/mytasks?tenantId=dd172b04-e4e2-4084-885c-47c9cc57f059&amp;webUrl=https%3a%2f%2ftasks.teams.microsoft.com%2fteamsui%2fpersonalApp%2falltasklists&amp;context=%7b%22subEntityId%22%3a%22%2fv1%2fassignedtome%3fnc%3demail%26nt%3dduedate%22%7d\" target=\"_blank\"><strong style=\"display:inline-block; font-weight:600; font-size:14px; font-family:&quot;Segoe UI&quot;,sans-serif; line-height:20px; color:#252424; text-decoration:none\">Open in Teams </strong></a></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></td></tr><tr><td align=\"left\" style=\"padding:0px; margin:0px\"><table cellpadding=\"0\" cellspacing=\"0\" border=\"0\" align=\"center\" style=\"border-spacing:0px; width:100%\"><tbody><tr><td align=\"left\" style=\"font-size:12px; line-height:16px; padding:20px 32px\"><div><table cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"border-spacing:0px; width:100%\"><tbody><tr><td><table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\"><tbody><tr><td style=\"font-family:'Segoe UI',SUWR,Verdana,sans-serif; font-size:10px; line-height:20px; color:#6b6b6b; padding:6px 0; letter-spacing:-0.01em\">You are receiving this email because you have subscribed to Microsoft Office 365. </td></tr><tr><td style=\"font-family:'Segoe UI',SUWR,Verdana,sans-serif; font-size:10px; line-height:20px; color:#6b6b6b; padding:6px 0; letter-spacing:-0.01em\">Notification settings: Go to <a href=\"https://tasks.office.com/\" target=\"_blank\" style=\"color:#6b6b6c; text-decoration:underline\">Planner</a>, select the gear icon, then select &quot;Notifications&quot;. </td></tr><tr><td align=\"left\" style=\"padding-top:12px; text-align:left; padding-bottom:12px\"><hr></td></tr><tr><td align=\"left\" style=\"padding-top:12px; text-align:left; padding-bottom:12px\"><img src=\"cid:d4345b38-890c-4f32-96e9-f1c5a70f9ee5\" alt=\"\" title=\"\" height=\"22\" width=\"90\" style=\"margin:0px; height:22px; width:90px\"> </td></tr><tr><td align=\"left\" style=\"padding-top:12px; text-align:left; padding-bottom:12px\"><table cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"border-spacing:0px; width:100%\"><tbody><tr><td align=\"left\" style=\"padding:0 4px 0 0; white-space:nowrap\"><p style=\"padding:0px; margin:0px; font-family:'Segoe UI',SUWR,Verdana,sans-serif; font-size:12px; line-height:20px; color:#6b6b6c; letter-spacing:-0.01em\"><a href=\"https://go.microsoft.com/fwlink/?LinkId=521839\" target=\"_blank\" title=\"\" style=\"padding:0px; margin:0px; font-family:'Segoe UI',SUWR,Verdana,sans-serif; font-size:12px; line-height:20px; color:#6b6b6c; letter-spacing:-0.01em\">Privacy&nbsp;Statement</a> </p></td></tr></tbody></table></td></tr><tr><td align=\"left\" style=\"padding-top:12px; text-align:left; padding-bottom:12px\"><table cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"border-spacing:0px; width:100%\"><tbody><tr><td align=\"left\"><p style=\"margin:0px; font-family:'Segoe UI',SUWR,Verdana,sans-serif; font-size:12px; line-height:20px; color:#6b6b6c; letter-spacing:-0.01em\">This email is generated through Contoso's use of Microsoft 365 and may contain content that is controlled by Contoso.</p></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></div></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></div><img src=\"https://southcentralusr-notifyp.svc.ms:443/api/v2/tracking/method/View?mi=bYzyl-mw-Eio6xskKG5XtA\" aria-hidden=\"true\" role=\"presentation\" height=\"1\" width=\"1\"></body></html>"
        },
        "sender": {
            "emailAddress": {
                "name": "Microsoft on behalf of your organization",
                "address": "noreply@planner.office365.com"
            }
        },
        "from": {
            "emailAddress": {
                "name": "Microsoft on behalf of your organization",
                "address": "noreply@planner.office365.com"
            }
        },
        "toRecipients": [
            {
                "emailAddress": {
                    "name": "Adele Vance",
                    "address": "AdeleV@M365x63639251.OnMicrosoft.com"
                }
            }
        ],
        "ccRecipients": [],
        "bccRecipients": [],
        "replyTo": [],
        "flag": {
            "flagStatus": "notFlagged"
        }
    }
    email = Email(**email)
    test_file = Path("test.html")
    test_file.touch(exist_ok=True)
    test_file.write_text(email.view)
