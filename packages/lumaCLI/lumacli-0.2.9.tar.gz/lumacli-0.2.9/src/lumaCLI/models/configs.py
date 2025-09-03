"""Pydantic models for Luma instance configuration."""
from typing import Optional, Any

from pydantic import BaseModel, EmailStr, model_validator, field_validator

allowed_icons = (
    "AcademicCap",
    "AdjustmentsHorizontal",
    "AdjustmentsVertical",
    "ArchiveBox",
    "ArchiveBoxArrowDown",
    "ArchiveBoxXMark",
    "ArrowDown",
    "ArrowDownCircle",
    "ArrowDownLeft",
    "ArrowDownOnSquare",
    "ArrowDownOnSquareStack",
    "ArrowDownRight",
    "ArrowDownTray",
    "ArrowLeft",
    "ArrowLeftCircle",
    "ArrowLeftOnRectangle",
    "ArrowLongDown",
    "ArrowLongLeft",
    "ArrowLongRight",
    "ArrowLongUp",
    "ArrowPath",
    "ArrowPathRoundedSquare",
    "ArrowRight",
    "ArrowRightCircle",
    "ArrowRightOnRectangle",
    "ArrowSmallDown",
    "ArrowSmallLeft",
    "ArrowSmallRight",
    "ArrowSmallUp",
    "ArrowTopRightOnSquare",
    "ArrowTrendingDown",
    "ArrowTrendingUp",
    "ArrowUp",
    "ArrowUpCircle",
    "ArrowUpLeft",
    "ArrowUpOnSquare",
    "ArrowUpOnSquareStack",
    "ArrowUpRight",
    "ArrowUpTray",
    "ArrowUturnDown",
    "ArrowUturnLeft",
    "ArrowUturnRight",
    "ArrowUturnUp",
    "ArrowsPointingIn",
    "ArrowsPointingOut",
    "ArrowsRightLeft",
    "ArrowsUpDown",
    "AtSymbol",
    "Backspace",
    "Backward",
    "Banknotes",
    "Bars2",
    "Bars3",
    "Bars3BottomLeft",
    "Bars3BottomRight",
    "Bars3CenterLeft",
    "Bars4",
    "BarsArrowDown",
    "BarsArrowUp",
    "Battery0",
    "Battery100",
    "Battery50",
    "Beaker",
    "Bell",
    "BellAlert",
    "BellSlash",
    "BellSnooze",
    "Bolt",
    "BoltSlash",
    "BookOpen",
    "Bookmark",
    "BookmarkSlash",
    "BookmarkSquare",
    "Briefcase",
    "BugAnt",
    "BuildingLibrary",
    "BuildingOffice",
    "BuildingOffice2",
    "BuildingStorefront",
    "Cake",
    "Calculator",
    "Calendar",
    "CalendarDays",
    "Camera",
    "ChartBar",
    "ChartBarSquare",
    "ChartPie",
    "ChatBubbleBottomCenter",
    "ChatBubbleBottomCenterText",
    "ChatBubbleLeft",
    "ChatBubbleLeftEllipsis",
    "ChatBubbleLeftRight",
    "ChatBubbleOvalLeft",
    "ChatBubbleOvalLeftEllipsis",
    "Check",
    "CheckBadge",
    "CheckCircle",
    "ChevronDoubleDown",
    "ChevronDoubleLeft",
    "ChevronDoubleRight",
    "ChevronDoubleUp",
    "ChevronDown",
    "ChevronLeft",
    "ChevronRight",
    "ChevronUp",
    "ChevronUpDown",
    "CircleStack",
    "Clipboard",
    "ClipboardDocument",
    "ClipboardDocumentCheck",
    "ClipboardDocumentList",
    "Clock",
    "Cloud",
    "CloudArrowDown",
    "CloudArrowUp",
    "CodeBracket",
    "CodeBracketSquare",
    "Cog",
    "Cog6Tooth",
    "Cog8Tooth",
    "CommandLine",
    "ComputerDesktop",
    "CpuChip",
    "CreditCard",
    "Cube",
    "CubeTransparent",
    "CurrencyBangladeshi",
    "CurrencyDollar",
    "CurrencyEuro",
    "CurrencyPound",
    "CurrencyRupee",
    "CurrencyYen",
    "CursorArrowRays",
    "CursorArrowRipple",
    "DevicePhoneMobile",
    "DeviceTablet",
    "Document",
    "DocumentArrowDown",
    "DocumentArrowUp",
    "DocumentChartBar",
    "DocumentCheck",
    "DocumentDuplicate",
    "DocumentMagnifyingGlass",
    "DocumentMinus",
    "DocumentPlus",
    "DocumentText",
    "EllipsisHorizontal",
    "EllipsisHorizontalCircle",
    "EllipsisVertical",
    "Envelope",
    "EnvelopeOpen",
    "ExclamationCircle",
    "ExclamationTriangle",
    "Eye",
    "EyeDropper",
    "EyeSlash",
    "FaceFrown",
    "FaceSmile",
    "Film",
    "FingerPrint",
    "Fire",
    "Flag",
    "Folder",
    "FolderArrowDown",
    "FolderMinus",
    "FolderOpen",
    "FolderPlus",
    "Forward",
    "Funnel",
    "Gif",
    "Gift",
    "GiftTop",
    "GlobeAlt",
    "GlobeAmericas",
    "GlobeAsiaAustralia",
    "GlobeEuropeAfrica",
    "HandRaised",
    "HandThumbDown",
    "HandThumbUp",
    "Hashtag",
    "Heart",
    "Home",
    "HomeModern",
    "Identification",
    "Inbox",
    "InboxArrowDown",
    "InboxStack",
    "InformationCircle",
    "Key",
    "Language",
    "Lifebuoy",
    "LightBulb",
    "Link",
    "ListBullet",
    "LockClosed",
    "LockOpen",
    "MagnifyingGlass",
    "MagnifyingGlassCircle",
    "MagnifyingGlassMinus",
    "MagnifyingGlassPlus",
    "Map",
    "MapPin",
    "Megaphone",
    "Microphone",
    "Minus",
    "MinusCircle",
    "MinusSmall",
    "Moon",
    "MusicalNote",
    "Newspaper",
    "NoSymbol",
    "PaintBrush",
    "PaperAirplane",
    "PaperClip",
    "Pause",
    "PauseCircle",
    "Pencil",
    "PencilSquare",
    "Phone",
    "PhoneArrowDownLeft",
    "PhoneArrowUpRight",
    "PhoneXMark",
    "Photo",
    "Play",
    "PlayCircle",
    "PlayPause",
    "Plus",
    "PlusCircle",
    "PlusSmall",
    "Power",
    "PresentationChartBar",
    "PresentationChartLine",
    "Printer",
    "PuzzlePiece",
    "QrCode",
    "QuestionMarkCircle",
    "QueueList",
    "Radio",
    "ReceiptPercent",
    "ReceiptRefund",
    "RectangleGroup",
    "RectangleStack",
    "RocketLaunch",
    "Rss",
    "Scale",
    "Scissors",
    "Server",
    "ServerStack",
    "Share",
    "ShieldCheck",
    "ShieldExclamation",
    "ShoppingBag",
    "ShoppingCart",
    "Signal",
    "SignalSlash",
    "Sparkles",
    "SpeakerWave",
    "SpeakerXMark",
    "Square2Stack",
    "Square3Stack3d",
    "Squares2x2",
    "SquaresPlus",
    "Star",
    "Stop",
    "StopCircle",
    "Sun",
    "Swatch",
    "TableCells",
    "Tag",
    "Ticket",
    "Trash",
    "Trophy",
    "Truck",
    "Tv",
    "User",
    "UserCircle",
    "UserGroup",
    "UserMinus",
    "UserPlus",
    "Users",
    "Variable",
    "VideoCamera",
    "VideoCameraSlash",
    "ViewColumns",
    "ViewfinderCircle",
    "Wallet",
    "Wifi",
    "Window",
    "Wrench",
    "WrenchScrewdriver",
    "XCircle",
    "XMark",
)


class Group(BaseModel):
    """Represents a group with metadata, slug, labels, and an optional icon.

    Attributes:
        meta_key (str): A key for metadata associated with the group.
        slug (str): A slug for the group, used in URLs or as an identifier.
        label_plural (str): The plural label for the group.
        label_singular (str): The singular label for the group.
        icon (Optional[str]): An optional icon for the group. Must be one of the allowed
            icons.
        in_sidebar (bool, optional): Whether the group should be displayed in the
            sidebar.
        visible (bool, optional): Whether the group should be displayed in Luma UI.

    Methods:
        icon_validator: Validates that the provided icon (if any) is in the allowed set.
    """

    meta_key: str
    slug: str
    label_plural: str
    label_singular: str
    icon: Optional[str] = None
    in_sidebar: Optional[bool] = True
    visible: Optional[bool] = True

    @field_validator("icon")
    def icon_validator(cls, v): # noqa: N805, ANN001
        """Validates the icon attribute.

        Ensures that if an icon is provided, it is one of the pre-approved icons.

        Args:
            v (str): The icon to validate.

        Returns:
            str: The validated icon.

        Raises:
            ValueError: If the icon is not in the allowed set.
        """
        if v is not None and v not in allowed_icons:
            msg = "Icon must be one of the allowed icons."
            raise ValueError(msg)
        return v


class Owner(BaseModel):
    """Represents an owner with email, name, and title.

    Attributes:
        email (EmailStr): The email address of the owner.
        first_name (str): The first name of the owner.
        last_name (str): The last name of the owner.
        title (str): The title of the owner.
    """

    email: EmailStr
    first_name: str
    last_name: str
    title: str


class MetadataField(BaseModel):
    """Represents metadata field configuration.

    Attributes:
        name (str): The name of the field.
        default (str): The default value to use.
    """

    name: str
    default: Any


class Config(BaseModel):
    """Configuration model holding information about groups and owners.

    Attributes:
        groups (Optional[list[Group]]): A list of Group objects. Ensures uniqueness of
            meta_keys and slugs among groups.
        owners (Optional[list[Owner]]): A list of Owner objects.

    Methods:
        validate_unique: Validates the uniqueness of meta_keys and slugs within the
            groups.
    """

    groups: Optional[list[Group]]
    owners: Optional[list[Owner]]

    @model_validator(mode='before')
    @classmethod
    def validate_unique(cls, values) -> dict:  # noqa: N805
        """Validates the uniqueness of 'meta_key' and 'slug' for each group.

        Args:
            values (dict): The values to validate.

        Returns:
            dict: The validated values.

        Raises:
            ValueError: If 'meta_key' or 'slug' is not unique across all groups.
        """
        groups = values.get("groups")
        if groups:
            # Check for unique meta_key

            meta_keys = {group['meta_key'] for group in groups}
            if len(meta_keys) != len(groups):
                msg = "meta_key must be unique for each group."
                raise ValueError(msg)

            # Check for unique slug
            slugs = {group['slug'] for group in groups}
            if len(slugs) != len(groups):
                msg = "slug must be unique for each group."
                raise ValueError(msg)
        return values
