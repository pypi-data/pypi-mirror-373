from typing import Dict, List, TypedDict


class _GoogleEntityInfo(TypedDict):
    id: str
    email: str
    displayName: str
    self: bool


class TimeInfo(TypedDict):
    date: str
    dateTime: str
    timeZone: str


class _AttendeeInfo(_GoogleEntityInfo):
    organizer: bool
    resource: bool
    optional: bool
    responseStatus: str
    comment: str
    additionalGuests: int


class _ExtendedPropertiesInfo(TypedDict):
    private: Dict[any, str]
    shared: Dict[any, str]


class _CreateRequestInfo(TypedDict):
    requestId: str
    conferenceSolutionKey: Dict[str, str]
    status: Dict[str, str]


class _ConferenceSolutionInfo(TypedDict):
    key: Dict[any, str]
    name: str
    iconUri: str


class _EntryPointInfo(TypedDict):
    entryPointType: str
    uri: str
    label: str
    pin: str
    accessCode: str
    meetingCode: str
    passcode: str
    password: str


class _ConferenceDataInfo(TypedDict):
    createRequest: _CreateRequestInfo
    entryPoints: List[_EntryPointInfo]
    conferenceSolution: _ConferenceSolutionInfo
    conferenceId: str
    signature: str
    notes: str


class _GadgetInfo(TypedDict):
    type: str
    title: str
    link: str
    iconLink: str
    width: int
    height: int
    display: str
    preferences: Dict[any, str]


class _OverridesInfo(TypedDict):
    method: str
    minutes: int


class _RemindersInfo(TypedDict):
    useDefault: bool
    overrides: List[_OverridesInfo]


class _URLInfo(TypedDict):
    url: str
    title: str


class _AttachmentInfo(TypedDict):
    fileUrl: str
    title: str
    mimeType: str
    iconLink: str
    fileId: str


class GoogleEventType(TypedDict):
    """
    The typing information for the Google event dictionary
    """

    kind: str
    id: str
    status: str
    htmlLink: str
    created: str
    updated: str
    summary: str
    description: str
    location: str
    colorId: str
    creator: _GoogleEntityInfo
    organizer: _GoogleEntityInfo
    start: TimeInfo
    end: TimeInfo
    endTimeUnspecified: bool
    recurrence: List[str]
    recurringEventId: str
    originalStartTime: TimeInfo
    transparency: str
    visibility: str
    iCalUID: str
    sequence: int
    attendees: List[_AttendeeInfo]
    attendeesOmitted: bool
    extendedProperties: _ExtendedPropertiesInfo
    hangoutLink: str
    conferenceData: _ConferenceDataInfo
    gadget: _GadgetInfo
    anyoneCanAddSelf: bool
    guestsCanInviteOthers: bool
    guestsCanModify: bool
    guestsCanSeeOtherGuests: bool
    privateCopy: bool
    locked: bool
    reminders: _RemindersInfo
    source: _URLInfo
    attachments: List[_AttachmentInfo]
    eventType: str
