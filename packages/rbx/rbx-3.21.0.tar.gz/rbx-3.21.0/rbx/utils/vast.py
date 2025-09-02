__all__ = [
    "AdParameters",
    "build_vpaid",
    "build_vast",
    "Creative",
    "MediaFile",
    "replace_cachebusting",
    "Tracker",
]

import dataclasses as dc
import json
import re
from typing import Literal, Optional, TypedDict, Union

from lxml import etree


@dc.dataclass
class MediaFile:
    url: str
    mimetype: str
    width: int
    height: int
    bitrate: Optional[int] = 0
    delivery: Literal["progressive"] = "progressive"


@dc.dataclass
class Creative:
    id: str
    name: str
    description: str
    duration: int
    files: [MediaFile]
    icon: Optional[bool] = False
    skipoffset: Optional[int] = 0


@dc.dataclass
class Wrapper:
    id: str
    uri: str


class Attribute(TypedDict):
    name: str
    value: str


class EventParameter(TypedDict):
    pixel: list[str]
    redirect: list[str]
    script: list[str]


class EventsParameters(TypedDict):
    clicks: list[str]
    engagement: EventParameter
    impression: EventParameter


class TrackingParameters(TypedDict):
    events: EventsParameters
    params: dict


class AdParameters(TypedDict):
    dcoMacros: dict
    tracking: TrackingParameters


@dc.dataclass
class Tracker:
    type: Literal["click", "clickthrough", "impression", "error", "event"]
    url: str
    attributes: Optional[list[Attribute]] = None

    def __hash__(self):
        return hash(
            (self.type, self.url, tuple(self.attributes) if self.attributes else None)
        )


def build_vast(
    *,
    id: str,
    creative: Union[Creative, Wrapper],
    trackers: Optional[list[Tracker]] = None,
    version: Optional[str] = "3.0",
) -> bytes:
    """Construct a VAST XML.

    Note that all trackers support multiple occurences except "clickthrough".
    """
    is_wrapper = isinstance(creative, Wrapper)
    has_video = (
        False
        if is_wrapper
        else any(file.mimetype.startswith("video") for file in creative.files)
    )

    tracking = {
        "errors": [],
        "impressions": [],
        "events": [],
        "clickthrough": None,
        "click": None,
    }
    for tracker in trackers or []:
        if tracker.type == "error":
            tracking["errors"].append(tracker)
        elif tracker.type == "impression":
            tracking["impressions"].append(tracker)
        elif tracker.type == "event":
            # VAST 2.0 does not support "closeLinear", "progress" and "skip" events.
            if version == "2.0" and tracker.attributes["event"] in (
                "closeLinear",
                "progress",
                "skip",
            ):
                continue
            # VAST Audio does not need "fullscreen" and "exitFullscreen" events.
            if not has_video and tracker.attributes["event"] in (
                "fullscreen",
                "exitFullscreen",
            ):
                continue
            tracking["events"].append(tracker)
        elif tracker.type == "clickthrough":
            tracking["clickthrough"] = tracker
        elif tracker.type == "click":
            tracking["click"] = tracker

    """Root element

    <VAST xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="vast.xsd"
        version="3.0">
        <Ad id="Placement ID">
            ...
        </Ad>
    </VAST>

    """
    ns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
    root = etree.Element(
        "VAST",
        attrib={
            f"{{{ns_xsi}}}noNamespaceSchemaLocation": "vast.xsd",
            "version": version,
        },
    )

    ad_elmt = etree.SubElement(root, "Ad")
    ad_elmt.set("id", id)

    """<Inline> element

        <InLine>
            <AdSystem>System</AdSystem>
            <AdTitle>Title</AdTitle>
            <Description><![CDATA[Description]]></Description>
            <Error><![CDATA[...]]></Error>
            <Impression><![CDATA[...]]></Impression>
        </InLine>

    <AdSystem>, <AdTitle> and <Impression> are required elements.

    or <Wrapper> element

        <Wrapper>
            <AdSystem>System</AdSystem>
            <VASTAdTagURI><![CDATA[...]]></VASTAdTagURI>
            <Error><![CDATA[...]]></Error>
            <Impression><![CDATA[...]]></Impression>
        </Wrapper>

    <AdSystem> and <Impression> are required elements.
    """
    if is_wrapper:
        inline_elmt = etree.SubElement(ad_elmt, "Wrapper")
    else:
        inline_elmt = etree.SubElement(ad_elmt, "InLine")

    ad_system_elmt = etree.SubElement(inline_elmt, "AdSystem")
    ad_system_elmt.text = "Scoota"

    if is_wrapper:
        ad_tag_uri_elmt = etree.SubElement(inline_elmt, "VASTAdTagURI")
        ad_tag_uri_elmt.text = etree.CDATA(creative.uri)

    else:
        ad_title_elmt = etree.SubElement(inline_elmt, "AdTitle")
        ad_title_elmt.text = creative.name

        description_elmt = etree.SubElement(inline_elmt, "Description")
        description_elmt.text = creative.description

    # <Error/>
    for tracker in tracking["errors"]:
        error_elmt = etree.SubElement(inline_elmt, "Error")
        error_elmt.text = etree.CDATA(tracker.url)

    # <Impression/>
    for tracker in tracking["impressions"]:
        imp_elmt = etree.SubElement(
            inline_elmt, "Impression", attrib=tracker.attributes
        )
        imp_elmt.text = etree.CDATA(tracker.url)

    """<Creatives> element.

    The <Creatives> element provides details about the files for each placement to be included
    as part of the ad experience.

        <Creatives>
            <Creative id="Creative ID">
                <Linear>
                    <Duration>HH:MM:SS.mmm</Duration>
                    <MediaFiles>
                        <MediaFile
                            delivery="progressive"
                            type="video/mp4"
                            width="300"
                            height="250">
                            <![CDATA[http://path/to/video.mp4]]>
                        </MediaFile>
                    </MediaFiles>
                    <TrackingEvents>
                        <Tracking><![CDATA[...]]></Tracking>
                    </TrackingEvents>
                    <VideoClicks>
                        <ClickThrough><![CDATA[...]]></ClickThrough>
                        <ClickTracking><![CDATA[...]]></ClickTracking>
                    </VideoClicks>
                    <Icon />
                </Linear>
            </Creative>
        </Creatives>

    A <Linear> element has two required child elements, <Duration> and <MediaFiles>.

    `delivery`, `type`, `width` and `height` are all required attributes of <MediaFile>. The
    `delivery` attribute defaults to progressive as we currently do not support streaming video.
    """
    has_tracking = len(tracking["events"]) > 0 or tracking["clickthrough"] is not None

    if not is_wrapper or has_tracking:
        # A wrapper with tracking needs the <Linear> element to exist
        creatives_elmt = etree.SubElement(inline_elmt, "Creatives")
        creative_elmt = etree.SubElement(
            creatives_elmt, "Creative", attrib={"id": creative.id}
        )
        linear_elmt = etree.SubElement(creative_elmt, "Linear")

    if not is_wrapper:
        if creative.skipoffset:
            linear_elmt.set(
                "skipoffset", milliseconds_to_HHMMSSmmm(creative.skipoffset)
            )

        # <Duration> element.
        duration_elmt = etree.SubElement(linear_elmt, "Duration")
        duration_elmt.text = milliseconds_to_HHMMSSmmm(creative.duration)

        # Required <MediaFiles> element.
        media_files_elmt = etree.SubElement(linear_elmt, "MediaFiles")
        for file in creative.files:
            attrib = {
                "delivery": file.delivery,
                "height": str(file.height),
                "maintainAspectRatio": "true",
                "scalable": "true",
                "type": file.mimetype,
                "width": str(file.width),
            }
            if file.bitrate:
                attrib["bitrate"] = str(file.bitrate)

            media_file_elmt = etree.SubElement(
                media_files_elmt,
                "MediaFile",
                attrib=attrib,
            )
            media_file_elmt.text = etree.CDATA(file.url)

    """Tracking <TrackingEvents> and <VideoClicks> elements.

        <TrackingEvents>
            <Tracking event="firstQuartile">
                <![CDATA[http://path/to/first/quartile]]>
            </Tracking>
        </TrackingEvents>
        <VideoClicks>
            <ClickThrough>
                <![CDATA[http://path/to/clickthrough]]>
            </ClickThrough>
            <ClickTracking>
                <![CDATA[http://path/to/click]]>
            </ClickTracking>
        </VideoClicks>

    """
    if len(tracking["events"]):
        events_elmt = etree.SubElement(linear_elmt, "TrackingEvents")
        for tracker in tracking["events"]:
            event_elmt = etree.SubElement(
                events_elmt, "Tracking", attrib=tracker.attributes
            )
            event_elmt.text = etree.CDATA(tracker.url)

    if tracking["clickthrough"]:
        tracker = tracking["clickthrough"]
        video_clicks_elmt = etree.SubElement(linear_elmt, "VideoClicks")
        clickthrough_elmt = etree.SubElement(
            video_clicks_elmt, "ClickThrough", attrib=tracker.attributes
        )
        clickthrough_elmt.text = etree.CDATA(tracker.url)
    else:
        video_clicks_elmt = None

    if tracking["click"]:
        tracker = tracking["click"]
        if video_clicks_elmt is None:
            video_clicks_elmt = etree.SubElement(linear_elmt, "VideoClicks")
        click_elmt = etree.SubElement(
            video_clicks_elmt, "ClickTracking", attrib=tracker.attributes
        )
        click_elmt.text = etree.CDATA(tracker.url)

    """AdChoices <Icon> element.

    Display AdChoices icon and will click through to //info.evidon.com/more_info/130210.
    """
    if not is_wrapper and creative.icon:
        icons_elmt = etree.SubElement(linear_elmt, "Icons")
        icon_elmt = etree.SubElement(
            icons_elmt,
            "Icon",
            attrib={
                "height": "15",
                "program": "AdChoices",
                "width": "77",
                "xPosition": "right",
                "yPosition": "top",
            },
        )
        static_resource_elmt = etree.SubElement(
            icon_elmt,
            "StaticResource",
            attrib={
                "creativeType": "image/png",
            },
        )
        static_resource_elmt.text = etree.CDATA("//c.betrad.com/icon/c_30_us.png")
        icon_clicks_elmt = etree.SubElement(icon_elmt, "IconClicks")
        icon_clickthrough_elmt = etree.SubElement(icon_clicks_elmt, "IconClickThrough")
        icon_clickthrough_elmt.text = etree.CDATA("//info.evidon.com/more_info/130210")

    return etree.tostring(root, encoding="UTF-8", xml_declaration=False)


def build_vpaid(
    *,
    id: str,
    creative: Creative,
    ad_parameters: Optional[AdParameters] = None,
    trackers: Optional[list[Tracker]] = None,
    version: Optional[str] = "3.0",
) -> bytes:
    """Construct a VPAID VAST XML."""
    tracking = {"errors": [], "events": [], "clickthrough": None}
    for tracker in trackers or []:
        if tracker.type == "error":
            tracking["errors"].append(tracker)
        elif tracker.type == "event":
            # VAST 2.0 does not support "progress" and "skip" events.
            if version == "2.0" and tracker.attributes["event"] in ("progress", "skip"):
                continue
            tracking["events"].append(tracker)
        elif tracker.type == "clickthrough":
            tracking["clickthrough"] = tracker

    """Root element

    <VAST xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="vast.xsd"
        version="3.0">
        <Ad id="Placement ID">
            ...
        </Ad>
    </VAST>

    """
    ns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
    root = etree.Element(
        "VAST",
        attrib={
            f"{{{ns_xsi}}}noNamespaceSchemaLocation": "vast.xsd",
            "version": version,
        },
    )

    ad_elmt = etree.SubElement(root, "Ad")
    ad_elmt.set("id", id)

    """<Inline> element

        <InLine>
            <AdSystem>System</AdSystem>
            <AdTitle>Title</AdTitle>
            <Description><![CDATA[Description]]></Description>
            <Impression><![CDATA[...]]></Impression>
        </InLine>

    <AdSystem>, <AdTitle> and <Impression> are required elements.
    """
    inline_elmt = etree.SubElement(ad_elmt, "InLine")
    ad_system_elmt = etree.SubElement(inline_elmt, "AdSystem")
    ad_system_elmt.text = "Scoota"

    ad_title_elmt = etree.SubElement(inline_elmt, "AdTitle")
    ad_title_elmt.text = creative.name

    description_elmt = etree.SubElement(inline_elmt, "Description")
    description_elmt.text = creative.description

    # Dummy <Impression/>
    imp_elmt = etree.SubElement(inline_elmt, "Impression")
    imp_elmt.text = etree.CDATA("")

    # <Error/>
    for tracker in tracking["errors"]:
        error_elmt = etree.SubElement(inline_elmt, "Error")
        error_elmt.text = etree.CDATA(tracker.url)

    """<Creatives> element.

        <Creatives>
            <Creative id="Creative ID">
                <Linear>
                    <Duration>HH:MM:SS.mmm</Duration>
                    <MediaFiles>
                        <MediaFile
                            apiFramework="VPAID"
                            delivery="progressive"
                            type="application/javascript"
                            width="300"
                            height="250">
                            <![CDATA[http://path/to/vpaid.js]]>
                        </MediaFile>
                    </MediaFiles>
                    <AdParameters><![CDATA[...]]></AdParameters>
                </Linear>
            </Creative>
        </Creatives>

    """
    creatives_elmt = etree.SubElement(inline_elmt, "Creatives")
    creative_elmt = etree.SubElement(
        creatives_elmt, "Creative", attrib={"id": creative.id}
    )
    linear_elmt = etree.SubElement(creative_elmt, "Linear")

    if creative.skipoffset:
        linear_elmt.set("skipoffset", milliseconds_to_HHMMSSmmm(creative.skipoffset))

    # <Duration> element.
    duration_elmt = etree.SubElement(linear_elmt, "Duration")
    duration_elmt.text = milliseconds_to_HHMMSSmmm(creative.duration)

    # VPAID <MediaFiles> element.
    file = creative.files[0]
    media_files_elmt = etree.SubElement(linear_elmt, "MediaFiles")
    media_file_elmt = etree.SubElement(
        media_files_elmt,
        "MediaFile",
        attrib={
            "apiFramework": "VPAID",
            "delivery": file.delivery,
            "height": str(file.height),
            "type": file.mimetype,
            "width": str(file.width),
        },
    )
    media_file_elmt.text = etree.CDATA(file.url)

    """Tracking <TrackingEvents> and <VideoClicks> elements.

        <TrackingEvents>
            <Tracking event="firstQuartile">
                <![CDATA[http://path/to/first/quartile]]>
            </Tracking>
        </TrackingEvents>
        <VideoClicks>
            <ClickThrough>
                <![CDATA[http://path/to/clickthrough]]>
            </ClickThrough>
        </VideoClicks>

    """
    if len(tracking["events"]):
        events_elmt = etree.SubElement(linear_elmt, "TrackingEvents")
        for tracker in tracking["events"]:
            event_elmt = etree.SubElement(
                events_elmt, "Tracking", attrib=tracker.attributes
            )
            event_elmt.text = etree.CDATA(tracker.url)

    if tracking["clickthrough"]:
        tracker = tracking["clickthrough"]
        video_clicks_elmt = etree.SubElement(linear_elmt, "VideoClicks")
        clickthrough_elmt = etree.SubElement(
            video_clicks_elmt, "ClickThrough", attrib=tracker.attributes
        )
        clickthrough_elmt.text = etree.CDATA(tracker.url)

    # <AdParameters> element.
    if ad_parameters:
        ad_parameters_elmt = etree.SubElement(linear_elmt, "AdParameters")
        ad_parameters_elmt.text = etree.CDATA(json.dumps(ad_parameters))

    return etree.tostring(root, encoding="UTF-8", xml_declaration=False)


def milliseconds_to_HHMMSSmmm(milliseconds: int) -> str:
    """Convert milliseconds to HH:MM:SS.mmm string format."""
    hours, rem = divmod(milliseconds / 1000.0, 3600)
    minutes, seconds = divmod(rem, 60)

    return "{:0>2}:{:0>2}:{:06.3f}".format(int(hours), int(minutes), seconds)


def replace_cachebusting(url):
    """Replace [timestamp] and [cachebuster] macros with [CACHEBUSTING] macro."""
    return re.sub(
        pattern=r"\[(timestamp|cachebuster)\]",
        repl="[CACHEBUSTING]",
        string=url,
        flags=re.I,
    )
