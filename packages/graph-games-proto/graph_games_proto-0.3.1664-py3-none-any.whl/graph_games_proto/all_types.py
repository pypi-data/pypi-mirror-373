import logging
import random
from uuid import uuid4
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional, Set, TypeVar, Generic, Union
from uuid import UUID
import uuid
from multipledispatch import dispatch



@dataclass(frozen=True)
class ScoreItem:
    code_idx: int
    amount: int
    json: Optional[str]

@dataclass(frozen=True)
class ScoreDiff:
    a: int
    b: int

@dataclass(frozen=True)
class QValueFormula:
    q_num: Optional[int]
    score_diff: ScoreDiff

    @classmethod
    def from_formula(cls, formula):
        return cls(formula.q_num, ScoreDiff(*formula.score_diff))

@dataclass(frozen=True)
class FrozenSymbolDrawing:
    name: str
    path_d: str
    polygons_json: Optional[str]

@dataclass(frozen=True)
class FrozenSymbolDrawingNoPolygons:
    name: str
    path_d: str

@dataclass(frozen=True)
class FrozenUnit:
    num: int
    quantity: int
    name: str
    symbol_uuid: Optional[UUID]
    board_idx: int
    is_wild: bool
    has_symbol: bool
    from_color: str
    from_strength: int
    via_color: Optional[str]
    via_strength: Optional[int]
    to_color: str
    to_strength: int
    border_color: str
    border_strength: int
    segment_color: str
    segment_strength: int
    stamp_hue: str
    stamp_strength: int
    symbol_hue: str
    symbol_strength: int
    segment_opacity: int
    symbol_drawing: FrozenSymbolDrawingNoPolygons
    dark_mode_from_color: str
    dark_mode_from_strength: int
    dark_mode_via_color: str
    dark_mode_via_strength: int
    dark_mode_to_color: str
    dark_mode_to_strength: int
    dark_mode_border_color: str
    dark_mode_border_strength: int
    dark_mode_segment_color: str
    dark_mode_segment_strength: int
    dark_mode_symbol_hue: str
    dark_mode_symbol_strength: int
    from_color_strength: str
    to_color_strength: str
    border_color_strength: str
    via_color_strength: Optional[str]


@dataclass(frozen=True)
class MapBoxViewConfig:
    latitude: float
    longitude: float
    zoom: float

@dataclass(frozen=True)
class LatLng:
    lat: float
    lng: float


@dataclass(frozen=True)
class FrozenPoint:
    num: int
    uuid: UUID
    name: str
    board_uuid: UUID
    lat: float
    lng: float

@dataclass(frozen=True)
class SegmentBox:
    north_west: LatLng
    north_east: LatLng
    south_west: LatLng
    south_east: LatLng

@dataclass(frozen=True)
class FrozenLink:
    num: int
    uuid: UUID
    board_uuid: UUID
    c1: UUID
    c2: UUID
    length: int
    width: int
    radius_a: int
    radius_b: int
    control_lat: float
    control_lng: float
    paths_json: str
    allow_mixed1: bool
    allow_mixed2: bool
    special1: bool
    special2: bool
    gap_pct: float
    start_gap_pct: float
    end_gap_pct: float
    spacing_between_paths: float
    segment_height_to_width: float
    segment_width_to_point_radius: float
    link_paths: List[FrozenLinkPath]
    point_a_uuid: UUID
    point_b_uuid: UUID
    is_double: bool


@dataclass(frozen=True)
class Setting:
    uuid: UUID
    name: str
    title: str
    cat: str
    default_value_json: str
    value_json: str
    field_type: str
    idx: int
    range_from: int
    range_to: int


@dataclass(frozen=True)
class FrozenMapStyle:
    uuid: UUID
    name: str
    mapbox_url: Optional[str]
    custom_tileset_name: Optional[str]
    tile_size: int
    max_zoom: int
    selected_zoom_limit: int
    is_global: bool
    src: str


@dataclass(frozen=True)
class FrozenMapConfig:
    initial_seconds_per_revolution: int
    initial_map_projection: str
    gamemode_map_projection: str
    gamemode_bearing: float
    max_zoom: Optional[float]
    fog_json: str
    fly_to_game_duration: int
    game_view_config: 'MapBoxViewConfig'
    setup_lat: float
    setup_lng: float
    setup_zoom: float


@dataclass(frozen=True)
class FrozenDeckUnit:
    quantity: int
    unit: FrozenUnit


@dataclass(frozen=True)
class FrozenDeck:
    uuid: UUID
    name: str
    custom: bool
    deck_units: List[FrozenDeckUnit]


@dataclass(frozen=True)
class FrozenFaction:
    uuid: UUID
    name: str
    user_uuid: UUID
    base_hue: str
    from_hue: str
    from_strength: int
    to_hue: str
    to_strength: int
    border_hue: str
    border_strength: int
    stamp_opacity: int
    path_hue: str
    path_strength: int
    dark_mode_base_hue: str
    dark_mode_path_hue: str
    dark_mode_path_strength: int
    symbol_drawing_name: str
    symbol_drawing_size: int
    has_symbol: bool
    symbol_hue: str
    symbol_strength: int
    dark_mode_symbol_hue: str
    dark_mode_symbol_strength: int
    symbol_drawing: "FrozenSymbolDrawing"


@dataclass(frozen=True)
class FrozenAudioSlot:
    uuid: UUID
    name: str


@dataclass(frozen=True)
class FrozenTrack:
    uuid: UUID
    len: int
    is_loop: bool
    custom: bool
    user_uuid: Optional[UUID]
    source_track_uuid: Optional[UUID]
    s3_content_uuid: UUID


@dataclass(frozen=True)
class FrozenCharacterTrackSlot:
    uuid: UUID
    track: FrozenTrack
    slot: FrozenAudioSlot


@dataclass(frozen=True)
class FrozenCharacter:
    uuid: UUID
    name: str
    symbol_drawing_id: int
    faction_uuid: Optional[UUID]
    rating_range_idx: Optional[int]
    custom: bool
    user_uuid: UUID
    s3_content_uuid: Optional[UUID]
    limit_level: bool
    level_min: int
    level_max: int
    symbol_drawing: FrozenSymbolDrawing
    faction: Optional[FrozenFaction]
    track_slots: List[FrozenCharacterTrackSlot]


@dataclass(frozen=True)
class FrozenPlayer:
    character: FrozenCharacter
    faction: FrozenFaction


@dataclass(frozen=True)
class FrozenBot:
    uuid: UUID
    level: int
    name: str

@dataclass(frozen=True)
class FrozenBoard:
    id: int
    created_at: datetime
    updated_at: datetime
    uuid: UUID
    suuid: str
    name: str
    custom: bool
    map_style_uuid: UUID
    dark_map_style_uuid: UUID
    light_mode_enabled: bool
    dark_mode_enabled: bool
    point_marker_radius: int
    point_marker_radius_in_pixels: float
    point_hue: str
    point_strength: int
    dark_mode_point_hue: str
    dark_mode_point_strength: int
    pin_stack_scalar: float
    player_symbol_scalar: float
    fly_to_game_duration: int
    seconds_per_revolution: int
    custom_len_scores: bool
    len_scores: List[FrozenLenScore]
    deck: FrozenDeck
    points: List[FrozenPoint]
    routes: List[FrozenRoute]
    game_view_config: MapBoxViewConfig
    settings: List[Setting]
    bots: List[FrozenBot]
    board_paths: List[FrozenPath]
    links: List[FrozenLink]
    map_style: FrozenMapStyle
    dark_map_style: FrozenMapStyle
    map_config: FrozenMapConfig


@dataclass(frozen=True)
class ValidUser:
    is_disconnected: bool
    is_ready: bool
    level: int


@dataclass(frozen=True)
class MapConfig:
    initial_map_projection: str
    gamemode_map_projection: str
    gamemode_bearing: float
    max_zoom: Optional[float]
    fog_json: str
    initial_seconds_per_revolution: int
    fly_to_game_duration: int
    initial_view_config: MapBoxViewConfig
    game_view_config: MapBoxViewConfig
    setup_zoom: float
    setup_lat: float
    setup_lng: float


@dataclass(frozen=True)
class LenScore:
    id: int
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    board_uuid: Optional[UUID]
    len: int
    score: int

# Non-kwdef structs
@dataclass(frozen=True)
class AudioSlot:
    id: int
    uuid: UUID
    name: str
    locked_filters_json: str


@dataclass(frozen=True)
class CharacterTrackSlot:
    id: int
    uuid: UUID
    created_at: Optional[datetime]  # Julia's Union{Missing, DateTime} becomes Optional[datetime]
    updated_at: Optional[datetime]
    character_uuid: UUID
    track_uuid: UUID
    audio_slot_uuid: UUID


@dataclass(frozen=True)
class MapStyle:
    id: int
    uuid: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    user_uuid: UUID
    name: str
    style_json: str
    tile_size: int
    mapbox_url: Optional[str]
    custom_tileset_name: Optional[str]
    src: str
    is_global: bool
    max_zoom: int
    selected_zoom_limit: int
    tf1: int  # Julia UInt64; in Python, int is unbounded
    tags_json: str


# kwdef structs converted to dataclasses
@dataclass(frozen=True)
class UpdateMapInput:
    uuid: UUID
    name: str
    tag_uuids: List[UUID]


@dataclass(frozen=True)
class TrackSlotInput:
    uuid: UUID
    track_uuid: UUID
    slot_uuid: UUID


@dataclass(frozen=True)
class CreateBoardInput:
    uuid: UUID
    name: str
    map_style_uuid: UUID
    point_marker_radius: int
    point_marker_radius_in_pixels: float
    flat_map_view: bool
    track_slots: List[TrackSlotInput]
    gamemode_bearing: float
    setup_zoom: float
    setup_lat: float
    setup_lng: float
    point_hue: str
    point_strength: int
    dark_mode_point_hue: str
    dark_mode_point_strength: int
    dark_map_style_uuid: UUID
    light_mode_enabled: bool
    dark_mode_enabled: bool


@dataclass(frozen=True)
class UpdateBoardBasicsInput:
    uuid: UUID
    name: str
    map_style_uuid: UUID
    dark_map_style_uuid: UUID
    light_mode_enabled: bool
    dark_mode_enabled: bool
    gamemode_bearing: float
    setup_zoom: float
    setup_lat: float
    setup_lng: float


@dataclass(frozen=True)
class UpsertDeckInput:
    uuid: UUID
    name: str


@dataclass(frozen=True)
class UpdateBoardDeckInput:
    uuid: UUID
    deck_uuid: UUID


@dataclass(frozen=True)
class UpdateBoardWarInput:
    uuid: UUID
    war_uuid: UUID


@dataclass(frozen=True)
class UpdateBoardCabalInput:
    uuid: UUID
    cabal_uuid: UUID


@dataclass(frozen=True)
class UpdateBoardPointSettingsInput:
    uuid: UUID
    point_hue: str
    point_strength: int
    dark_mode_point_hue: str
    dark_mode_point_strength: int
    point_marker_radius: float
    point_marker_radius_in_pixels: float


# For UpdateCharacterInput, note that fields with default values must follow those without defaults.
@dataclass(frozen=True)
class UpdateCharacterInput:
    uuid: UUID
    name: str
    s3_content_uuid: UUID
    limit_level: bool
    level_min: int
    level_max: int
    tag_uuids: List[UUID]
    track_slots: List[TrackSlotInput]
    symbol_drawing_id: Optional[int] = 6253  # Default value provided


@dataclass(frozen=True)
class LenScoresInput:
    uuid: UUID
    custom_len_scores: bool
    lens: List[int]
    scores: List[int]


@dataclass(frozen=True)
class CreateTrackInput:
    uuid: UUID
    tag_uuids: List[UUID]
    length: int  # Note: "len" is a built-in name in Python. You might choose another name.
    s3_content_uuid: UUID
    source_track_uuid: Optional[UUID]  # Default is nothing (None)


@dataclass(frozen=True)
class UpdateTrackInput:
    uuid: UUID
    tag_uuids: List[UUID]


# For UpsertPlayerInput, non-default fields must precede fields with defaults.
@dataclass(frozen=True)
class UpsertPlayerInput:
    room_uuid: UUID
    faction_uuid: UUID
    player_idx: int
    locked: bool
    locked_color: bool
    locked_character: bool
    uuid: Optional[UUID]
    user_name: Optional[str]
    character_uuid: Optional[UUID]
    bot_uuid: Optional[UUID]
    level_min: int
    level_max: int


@dataclass(frozen=True)
class CommentInput:
    uuid: UUID
    room_uuid: UUID
    user_uuid: UUID
    content: str


@dataclass(frozen=True)
class ConnectionInput:
    page_size: int
    after: Optional[str]  # Julia's missing → None in Python
    before: Optional[str]
    cursor_cols: List[str]
    cursor_direction: str


@dataclass(frozen=True)
class PageInfo:
    count: int
    total_count: int
    count_before_start_cursor: int
    has_previous_page: bool
    has_next_page: bool
    start_cursor: Optional[str]  # Union{Nothing, String} in Julia
    end_cursor: Optional[str]
    refresh: ConnectionInput

@dataclass(frozen=True)
class MemoryItem:
    uuid: UUID
    key: str
    name: str

@dataclass(frozen=True)
class MemoryChannel:
    uuid: UUID
    key: str
    name: str

@dataclass(frozen=True)
class MemoryChannelConnection:
    nodes: List[MemoryChannel]
    page_info: PageInfo

@dataclass(frozen=True)
class MemoryItemConnection:
    nodes: List[MemoryItem]
    page_info: PageInfo

@dataclass(frozen=True)
class Server:
    id: int
    name: str
    status: int

@dataclass(frozen=True)
class InviteCodeStatus:
    code: str
    already_used: bool

@dataclass(frozen=True)
class SettingOption:
    id: int
    uuid: UUID
    name: str
    title: str
    field_type: str
    cat: str
    value_json: str
    range_from: int
    range_to: int
    idx: int

@dataclass(frozen=True)
class BoardSetting:
    id: int
    uuid: UUID
    board_uuid: Optional[UUID]  # Union{Missing, UUID} in Julia
    name: str
    value_json: str

@dataclass(frozen=True)
class Invite:
    id: int
    uuid: UUID
    created_at: Optional[datetime]      # Union{Missing, DateTime}
    updated_at: Optional[datetime]
    inviter_uuid: Optional[UUID]
    entered: bool
    new_user_uuid: Optional[UUID]
    code: str
    notes: Optional[str]

@dataclass(frozen=True)
class BatchedUUIDInput:
    uuids: List[UUID]

@dataclass(frozen=True)
class FilterInput:
    field_type: Optional[str]  # Defaulting missing values to None
    name: Optional[str]
    operator: Optional[str]
    value: Optional[str]

    @classmethod
    def from_params(cls, params: 'FilterInputParams') -> 'FilterInput':
        """
        Create a FilterInput instance from a FilterInputParams instance.
        """
        return cls(
            field_type=params.field_type,
            name=params.name,
            operator=params.operator,
            value=params.value
        )

@dataclass(frozen=True)
class FilterInputParams:
    field_type: Optional[str]
    name: Optional[str]
    operator: Optional[str]
    value: Optional[str]

@dataclass(frozen=True)
class SearchInput:
    active_cols: Optional[str]
    dashboard_context: Optional[str]
    input: ConnectionInput
    filters: List[FilterInput]

@dataclass(frozen=True)
class DashboardInput:
    connection_input: ConnectionInput
    filters: List[FilterInput]
    active_cols: List[str]
    dashboard_context: str

@dataclass(frozen=True)
class UserDashboardInput:
    connection_input: ConnectionInput
    filters: List[FilterInput]
    dashboard_context: str

@dataclass(frozen=True)
class LatLngInput:
    lat: float
    lng: float

@dataclass(frozen=True)
class SegmentBoxInput:
    northEast: LatLngInput
    southEast: LatLngInput
    southWest: LatLngInput
    northWest: LatLngInput

@dataclass(frozen=True)
class SegmentInput:
    unit_uuid: UUID
    box: SegmentBoxInput

@dataclass(frozen=True)
class OutputSystem:
    uuid: Optional[UUID]
    score: Optional[float]  # Representing Float32 as float in Python

@dataclass(frozen=True)
class OutputEnabled:
    output: bool
    score: Optional[float]

@dataclass(frozen=True)
class OutputMeasurement:
    uuid: UUID
    score: Optional[float]

@dataclass(frozen=True)
class DeepQTargetNode:
    eval_level: int
    tag_uuids: List[UUID]
    action_uuids: List[UUID]

@dataclass(frozen=True)
class DeepQOutputNode:
    q_value: int

@dataclass(frozen=True)
class DeepQInputNodeReading:
    se: Optional[int]
    eval_level: Optional[int]
    measurement_uuid: Optional[str]
    signature_uuids: List[UUID]
    action_uuids: List[UUID]

@dataclass(frozen=True)
class DeepQInputNode:
    system_uuid: Optional[str]  # Union{Nothing, Missing, String}
    make_uuid: Optional[str]
    model_num: Optional[str]
    readings: List[DeepQInputNodeReading]

# --------------------------------------------------------------------
# Helper types (you may already have these defined elsewhere)
# --------------------------------------------------------------------

@dataclass(frozen=True)
class LatLng:
    lat: float
    lng: float

@dataclass(frozen=True)
class SegmentBox:
    north_west: LatLng
    north_east: LatLng
    south_west: LatLng
    south_east: LatLng

# --------------------------------------------------------------------
# Data structures converted from Julia structs
# --------------------------------------------------------------------

@dataclass(frozen=True)
class Dashboard:
    id: int
    uuid: UUID
    created_at: Optional[datetime]
    context: str
    name: str
    user_uuid: UUID
    raw: Optional[str]

@dataclass(frozen=True)
class UserDashboard:
    id: int
    uuid: UUID
    created_at: Optional[datetime]
    user_uuid: UUID
    context: str
    name: str
    raw: Optional[str]

@dataclass(frozen=True)
class GQLRequest:
    id: int
    created_at: Optional[datetime]
    uuid: UUID
    suuid: str
    is_query: bool
    gql: str
    vars_json: str
    extra_json: str
    source_json: str
    seconds: Optional[float]
    error: Optional[str]

@dataclass(frozen=True)
class User:
    id: int
    uuid: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    name: Optional[str]
    level: int
    img: Optional[str]
    member: bool
    speed_idx: int
    is_public: bool
    is_ranked: bool
    logged_board_uuid: UUID
    static_board_config_uuid: UUID

@dataclass(frozen=True)
class Bot:
    id: int
    uuid: UUID
    level: int
    name: str
    net_version_uuid: Optional[UUID]
    board_uuid: UUID

@dataclass(frozen=True)
class GamePlayer:
    id: int
    uuid: UUID
    created_at: Optional[datetime]
    logged_game_uuid: UUID
    user_uuid: Optional[UUID]
    bot_uuid: Optional[UUID]
    player_idx: int
    faction_uuid: UUID
    faction_idx: int
    character_uuid: UUID
    character_idx: int
    json: str

@dataclass(frozen=True)
class RoomPlayer:
    id: int
    uuid: UUID
    room_uuid: UUID
    user_name: Optional[str]
    bot_uuid: Optional[UUID]
    player_idx: int
    clicked_ready: bool
    locked: bool
    locked_color: bool
    locked_character: bool
    level_min: int
    level_max: int
    faction_idx: int
    character_idx: int
    faction_uuid: UUID
    character_uuid: UUID
    last_ping: Optional[str]

@dataclass(frozen=True)
class NextGameSettings:
    room_players: List[RoomPlayer]
    is_ranked: bool
    speed_idx: int
    is_public: bool

@dataclass(frozen=True)
class Comment:
    id: int
    uuid: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    room_uuid: UUID
    user_uuid: UUID
    content: Optional[str]

@dataclass(frozen=True)
class Activity:
    id: int
    uuid: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    room_uuid: UUID
    content: Optional[str]

@dataclass(frozen=True)
class LoggedGame:
    id: int
    created_at: datetime
    updated_at: datetime
    uuid: UUID
    suuid: str
    room_uuid: UUID
    board_uuid: UUID
    num_players: int
    rated: bool
    seed: int
    logged_board_uuid: UUID
    speed_idx: int
    is_public: bool
    is_ranked: bool
    static_board_config_uuid: UUID

@dataclass(frozen=True)
class S3Upload:
    id: int
    uuid: UUID
    created_at: datetime
    user_uuid: UUID
    s3_key: str

@dataclass(frozen=True)
class S3Content:
    id: int
    uuid: UUID
    created_at: datetime
    len: Optional[int]
    width: Optional[int]
    height: Optional[int]
    max_zoom: Optional[int]
    user_uuid: UUID
    s3_upload_uuid: Optional[UUID]
    s3_path: str

@dataclass(frozen=True)
class Track:
    id: int
    created_at: datetime
    updated_at: datetime
    uuid: UUID
    len: int
    is_loop: bool
    custom: bool
    user_uuid: Optional[UUID]
    source_track_uuid: Optional[UUID]
    s3_content_uuid: UUID
    tf1: int  # Julia’s UInt64 can be mapped to Python’s int
    tags_json: str

@dataclass(frozen=True)
class TrackToPlay:
    track: Track
    player_uuid: UUID

@dataclass(frozen=True)
class StaticBoardConfig:
    id: int
    uuid: UUID
    created_at: datetime
    board_uuid: UUID
    json: str

@dataclass(frozen=True)
class LoggedBoard:
    id: int
    created_at: datetime
    uuid: UUID
    board_uuid: UUID
    json: str

@dataclass(frozen=True)
class RoomLoggedBoard:
    room_uuid: UUID
    logged_board_uuid: UUID

@dataclass(frozen=True)
class Board:
    id: int
    created_at: datetime
    updated_at: datetime
    uuid: UUID
    suuid: str
    name: str
    custom: bool
    user_uuid: UUID
    fly_to_game_duration: int
    seconds_per_revolution: int
    point_marker_radius: int
    point_marker_radius_in_pixels: float
    initial_view_config_json: str
    game_view_config_json: str
    map_style_uuid: UUID
    dark_map_style_uuid: UUID
    initial_map_projection: str
    gamemode_map_projection: str
    gamemode_bearing: float
    max_zoom: Optional[float]
    initial_seconds_per_revolution: int
    fog_json: str
    ready: bool
    pin_stack_scalar: float
    player_symbol_scalar: float
    tf1: int  # Julia’s UInt64
    setup_lat: float
    setup_lng: float
    setup_zoom: float
    point_hue: str
    point_strength: int
    dark_mode_point_hue: str
    dark_mode_point_strength: int
    light_mode_enabled: bool
    dark_mode_enabled: bool
    deck_uuid: UUID
    war_uuid: UUID
    cabal_uuid: UUID
    custom_len_scores: bool

# --------------------------------------------------------------------
# Additional functions and helper structs
# --------------------------------------------------------------------

def getsegmentboxcentroid(x: SegmentBox) -> LatLng:
    """
    Compute the centroid of a SegmentBox by averaging the latitudes and longitudes.
    """
    avg_lat = (x.north_west.lat + x.north_east.lat + x.south_west.lat + x.south_east.lat) / 4
    avg_lng = (x.north_west.lng + x.north_east.lng + x.south_west.lng + x.south_east.lng) / 4
    return LatLng(lat=avg_lat, lng=avg_lng)

@dataclass(frozen=True)
class IntMatrix:
    nrows: int
    ncols: int
    items: List[int]

@dataclass(frozen=True)
class IntTensor:
    nrows: int
    ncols: int
    batch_size: int
    items: List[int]

@dataclass(frozen=True)
class EuclideanFeaturedGraph:
    adj_mat: IntMatrix
    node_coords: List[LatLng]
    edge_coords: List[SegmentBox]
    gf: IntMatrix
    nf: IntMatrix
    ef: IntMatrix


@dataclass(frozen=True)
class FeaturedGraph2:
    adj_mat: IntMatrix
    gf: IntMatrix
    nf: IntTensor
    ef: IntTensor

@dataclass(frozen=True)
class Point:
    id: int
    created_at: datetime
    updated_at: datetime
    uuid: UUID
    name: str
    board_uuid: UUID
    lat: float
    lng: float

@dataclass(frozen=True)
class Auth:
    id: int
    created_at: datetime
    updated_at: datetime
    uuid: UUID
    email: str
    user_uuid: UUID

@dataclass(frozen=True)
class Link:
    id: int
    created_at: datetime
    updated_at: datetime
    uuid: UUID
    board_uuid: UUID
    c1: UUID
    c2: UUID
    length: int
    width: int
    radius_a: int
    radius_b: int
    control_lat: float
    control_lng: float
    paths_json: str
    allow_mixed1: bool
    allow_mixed2: bool
    special1: bool
    special2: bool
    gap_pct: float
    start_gap_pct: float
    end_gap_pct: float
    spacing_between_paths: float
    segment_height_to_width: float
    segment_width_to_point_radius: float
    # Note: The Julia @scope annotation (archived => false) is not included here.
    
@dataclass(frozen=True)
class Segment:
    id: int
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    link_uuid: UUID
    unit_uuid: Optional[UUID]  # Union{Missing, UUID} becomes Optional[UUID]
    path_idx: int
    idx: int
    nw_lat: float
    nw_lng: float
    ne_lat: float
    ne_lng: float
    se_lat: float
    se_lng: float
    sw_lat: float
    sw_lng: float

@dataclass(frozen=True)
class AvailablePath:
    num: int
    fulfillment: List[int]

@dataclass(frozen=True)
class OrderedPointFullfillment:
    unit_card_num: int

@dataclass(frozen=True)
class OrderedFullfillment:
    segment_num: int
    unit_card_num: int

@dataclass(frozen=True)
class OrderedSegment:
    path_segment_num: int
    segment: Any  # Type not specified in the Julia struct

@dataclass(frozen=True)
class Cluster:
    id: int
    created_at: datetime
    updated_at: datetime
    uuid: UUID
    name: Optional[str]  # Union{Missing, String}
    board_uuid: UUID
    score: int
    hue: str
    strength: int
    is_named: bool

@dataclass(frozen=True)
class ClusterPoint:
    id: int
    uuid: UUID
    cluster_uuid: UUID
    point_uuid: UUID

@dataclass(frozen=True)
class Route:
    id: int
    created_at: datetime
    updated_at: datetime
    uuid: UUID
    name: Optional[str]  # Union{Missing, String}
    board_uuid: UUID
    point_a_uuid: UUID
    point_b_uuid: UUID
    score: int
    hue: str
    strength: int
    is_named: bool

@dataclass(frozen=True)
class Unit:
    id: int
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    name: str
    symbol_uuid: Optional[UUID]  # Union{Missing, UUID}
    symbol_drawing_uuid: UUID
    board_idx: int
    is_wild: bool
    has_symbol: bool
    from_color: str
    from_strength: int
    via_color: Optional[str]  # Union{Missing, String}
    via_strength: Optional[int]  # Union{Missing, Int}
    to_color: str
    to_strength: int
    border_color: str
    border_strength: int
    segment_color: str
    segment_strength: int
    stamp_hue: str
    stamp_strength: int
    symbol_hue: str
    symbol_strength: int
    segment_opacity: int
    symbol_drawing_name: str
    quantity: int
    dark_mode_from_color: str
    dark_mode_from_strength: int
    dark_mode_via_color: str
    dark_mode_via_strength: int
    dark_mode_to_color: str
    dark_mode_to_strength: int
    dark_mode_border_color: str
    dark_mode_border_strength: int
    dark_mode_segment_color: str
    dark_mode_segment_strength: int
    dark_mode_symbol_hue: str
    dark_mode_symbol_strength: int
    tags_json: str

@dataclass(frozen=True)
class Deck:
    id: int
    created_at: datetime
    updated_at: datetime
    uuid: UUID
    name: str
    user_uuid: UUID
    custom: bool
    tags_json: str

@dataclass(frozen=True)
class DeckUnit:
    id: int
    uuid: UUID
    deck_uuid: UUID
    unit_uuid: UUID
    quantity: int
    is_wild: bool

@dataclass(frozen=True)
class Path:
    id: int
    idx: int
    link_idx: int
    color: str
    spaces: int
    mountains: int
    wildcards: int
    start_point: Point
    end_point: Point

@dataclass(frozen=True)
class TrackSlot:
    uuid: UUID
    track: Any  # Replace with the actual type for Track if available
    slot: Any   # Replace with the actual type for AudioSlot if available

@dataclass(frozen=True)
class Cabal:
    id: int
    created_at: datetime
    updated_at: datetime
    uuid: UUID
    name: str
    user_uuid: UUID
    custom: bool
    tags_json: str

@dataclass(frozen=True)
class CabalCharacter:
    id: int
    uuid: UUID
    cabal_uuid: UUID
    character_uuid: UUID
    idx: int

@dataclass(frozen=True)
class War:
    id: int
    created_at: datetime
    updated_at: datetime
    uuid: UUID
    name: str
    user_uuid: UUID
    custom: bool
    tags_json: str

@dataclass(frozen=True)
class WarFaction:
    id: int
    uuid: UUID
    war_uuid: UUID
    faction_uuid: UUID
    idx: int


@dataclass(frozen=True)
class Character:
    id: int
    created_at: datetime
    updated_at: datetime
    uuid: UUID
    name: str
    ready: bool
    symbol_drawing_id: int
    symbol_drawing_uuid: UUID
    faction_uuid: Optional[UUID]  # corresponds to Union{Missing, UUID}
    rating_range_idx: Optional[int]  # Union{Missing, Int}
    custom: bool
    user_uuid: UUID
    s3_content_uuid: Optional[UUID]  # Union{Missing, UUID}
    limit_level: bool
    level_min: int
    level_max: int
    tf1: int  # Julia UInt64; in Python we simply use int
    tags_json: str

@dataclass(frozen=True)
class Faction:
    id: int
    created_at: datetime
    updated_at: datetime
    uuid: UUID
    name: str
    user_uuid: UUID
    base_hue: str
    from_hue: str
    from_strength: int
    to_hue: str
    to_strength: int
    border_hue: str
    border_strength: int
    stamp_opacity: int
    path_hue: str
    path_strength: int
    dark_mode_base_hue: str
    dark_mode_path_hue: str
    dark_mode_path_strength: int
    symbol_drawing_name: str
    symbol_drawing_uuid: UUID
    symbol_drawing_size: int
    has_symbol: bool
    symbol_hue: str
    symbol_strength: int
    dark_mode_symbol_hue: str
    dark_mode_symbol_strength: int
    tags_json: str

@dataclass(frozen=True)
class SymbolDrawing:
    id: int
    uuid: UUID
    name: str
    path_d: str
    polygons_json: Optional[str]  # Union{Missing, String}

@dataclass(frozen=True)
class XYCoords:
    x: float
    y: float

@dataclass(frozen=True)
class Polygon:
    xy_coords_list: List[XYCoords]

@dataclass(frozen=True)
class CapturedSegment:
    player_num: int
    segment_uuid: UUID

@dataclass(frozen=True)
class CapturedPoint:
    player_num: int
    point_uuid: UUID

# Functions that operate on a "Unit" (or UnitInput) object:
def getfromcolorstrength(x) -> str:
    return f"from-{x.from_color}-{x.from_strength}"

def gettocolorstrength(x) -> str:
    return f"to-{x.to_color}-{x.to_strength}"

def getbordercolorstrength(x) -> str:
    return f"border-{x.border_color}-{x.border_strength}"

def getviacolorstrength(x) -> Optional[str]:
    if x.via_color is None or x.via_strength is None:
        return None
    return f"via-{x.via_color}-{x.via_strength}"

@dataclass(frozen=True)
class Resource:
    id: int
    uuid: UUID
    name: str
    unit_uuid: Optional[UUID]  # Union{Missing, UUID}
    board_uuid: UUID
    board_idx: int
    is_wild: bool

@dataclass(frozen=True)
class PathScore:
    len: int
    score: int

# The following classes are modeled after Julia's @kwdef structs,
# so optional fields are given default values of None.

@dataclass(frozen=True)
class SettingInput:
    value_json: str
    name: str

@dataclass(frozen=True)
class CabalInput:
    name: Optional[str]  # Union{Missing, Nothing, String}
    uuid: UUID

@dataclass(frozen=True)
class ClusterInput:
    score: Optional[int]  # Union{Missing, Int}
    board_uuid: Optional[UUID]  # Union{Missing, UUID}
    name: Optional[str]  # Union{Missing, Nothing, String}
    hue: str
    strength: int
    is_named: bool
    uuid: UUID

@dataclass(frozen=True)
class RouteInput:
    point_a_uuid: Optional[UUID]  # Union{Missing, UUID}
    point_b_uuid: Optional[UUID]  # Union{Missing, UUID}
    score: Optional[int]  # Union{Missing, Int}
    board_uuid: Optional[UUID]  # Union{Missing, UUID}
    name: Optional[str]  # Union{Missing, Nothing, String}
    hue: str
    strength: int
    is_named: bool
    uuid: UUID

@dataclass(frozen=True)
class CharacterInput:
    name: Optional[str]  # Union{Missing, String}
    url: Optional[str]  # Union{Missing, String}
    player_uuid: Optional[UUID]  # Union{Missing, UUID}
    faction_uuid: Optional[UUID]  # Union{Missing, Nothing, UUID}
    uuid: UUID

@dataclass(frozen=True)
class WarInput:
    name: Optional[str]  # Union{Missing, String}
    uuid: UUID

@dataclass(frozen=True)
class FactionInput:
    name: Optional[str]  # Union{Missing, String}
    base_hue: Optional[str]  # Union{Missing, String}
    stamp_opacity: Optional[int]  # Union{Missing, Int}
    has_symbol: bool
    path_hue: str
    path_strength: int
    symbol_hue: str
    symbol_strength: int
    dark_mode_symbol_hue: str
    dark_mode_symbol_strength: int
    dark_mode_base_hue: Optional[str]  # Union{Missing, String}
    dark_mode_path_hue: str
    dark_mode_path_strength: int
    symbol_drawing_name: str
    symbol_drawing_size: int
    from_hue: str
    from_strength: int
    to_hue: str
    to_strength: int
    border_hue: str
    border_strength: int
    uuid: UUID

@dataclass(frozen=True)
class UnitInput:
    name: Optional[str]  # Union{Missing, String}
    board_uuid: Optional[UUID]
    has_symbol: Optional[bool]
    is_wild: Optional[bool]
    from_color: Optional[str]  # Union{Missing, String}
    from_strength: Optional[int]  # Union{Missing, Int}
    via_color: Optional[str]  # Union{Missing, Nothing, String}
    via_strength: Optional[int]  # Union{Missing, Nothing, Int}
    to_color: Optional[str]  # Union{Missing, String}
    to_strength: Optional[int]  # Union{Missing, Int}
    border_color: Optional[str]  # Union{Missing, String}
    border_strength: Optional[int]  # Union{Missing, Int}
    segment_color: Optional[str]  # Union{Missing, String}
    segment_strength: Optional[int]  # Union{Missing, Int}
    symbol_hue: Optional[str]  # Union{Missing, String}
    symbol_strength: Optional[int]  # Union{Missing, Int}
    dark_mode_from_color: Optional[str]  # Union{Missing, String}
    dark_mode_from_strength: Optional[int]  # Union{Missing, Int}
    dark_mode_via_color: Optional[str]  # Union{Missing, Nothing, String}
    dark_mode_via_strength: Optional[int]  # Union{Missing, Nothing, Int}
    dark_mode_to_color: Optional[str]  # Union{Missing, String}
    dark_mode_to_strength: Optional[int]  # Union{Missing, Int}
    dark_mode_border_color: Optional[str]  # Union{Missing, String}
    dark_mode_border_strength: Optional[int]  # Union{Missing, Int}
    dark_mode_segment_color: Optional[str]  # Union{Missing, String}
    dark_mode_segment_strength: Optional[int]  # Union{Missing, Int}
    dark_mode_symbol_hue: Optional[str]  # Union{Missing, String}
    dark_mode_symbol_strength: Optional[int]  # Union{Missing, Int}
    symbol_drawing_name: str
    uuid: UUID

@dataclass(frozen=True)
class PointInput:
    name: Optional[str]  # Union{Missing, String}
    lat: Optional[float]  # Union{Missing, Float64}
    lng: Optional[float]  # Union{Missing, Float64}
    board_uuid: Optional[UUID]  # Union{Missing, UUID}
    uuid: UUID

@dataclass(frozen=True)
class LinkInput:
    gap_pct: Optional[float]  # Union{Missing, Float64}
    start_gap_pct: Optional[float]  # Union{Missing, Float64}
    end_gap_pct: Optional[float]  # Union{Missing, Float64}
    spacing_between_paths: Optional[float]  # Union{Missing, Float64}
    segment_height_to_width: Optional[float]  # Union{Missing, Float64}
    segment_width_to_point_radius: Optional[float]  # Union{Missing, Float64}
    control_lat: Optional[float]  # Union{Missing, Float64}
    control_lng: Optional[float]  # Union{Missing, Float64}
    allow_mixed1: Optional[bool]
    allow_mixed2: Optional[bool]
    special1: Optional[bool]
    special2: Optional[bool]
    segments_json: Optional[str]  # Union{Missing, String}
    paths_json: Optional[str]  # Union{Missing, String}
    radius_a: Optional[int]  # Union{Missing, Int}
    radius_b: Optional[int]  # Union{Missing, Int}
    length: Optional[int]  # Union{Missing, Int}
    width: Optional[int]  # Union{Missing, Int}
    board_uuid: Optional[UUID]
    c1: Optional[UUID]
    c2: Optional[UUID]
    uuid: UUID

@dataclass(frozen=True)
class AuthInput:
    name: str
    email: str
    uuid: UUID

@dataclass(frozen=True)
class RoomIsPublicInput:
    is_public: bool
    uuid: UUID

@dataclass(frozen=True)
class RoomIsRankedInput:
    is_ranked: bool
    uuid: UUID

@dataclass(frozen=True)
class RoomSpeedInput:
    speed_idx: int
    uuid: UUID

@dataclass(frozen=True)
class RoomInput:
    board_uuid: UUID
    speed_idx: int
    is_public: bool
    is_ranked: bool
    uuid: UUID


@dataclass(frozen=True)
class MarketRefill:
    # "from" is renamed to "from_" because it's a reserved keyword in Python.
    from_: List[Optional[int]]
    to: List[Optional[int]]


@dataclass(frozen=True)
class PlayerScore:
    total: int
    breakdown: List[ScoreItem]


@dataclass(frozen=True)
class PlayerInfo:
    fig: Fig
    player_idx: int
    new_route_cards: List[int]
    route_cards: List[int]
    unit_cards: List[int]
    completed_routes: List[int]
    clusters: List[UUID]
    completed_clusters: List[UUID]
    paths: List[int]
    points: List[UUID]
    num_pieces: int
    num_point_pieces: int
    longest_road: List[int]
    longest_road_len: int
    final_score: Optional[PlayerScore]


@dataclass(frozen=True)
class State:
    game: Game
    fig: Fig
    action_history: List[Action]
    route_cards: List[int]
    route_discards: List[int]
    unit_cards: List[int]
    unit_discards: List[int]
    faceup_spots: List[Optional[int]]
    player_hands: List[PlayerInfo]
    last_to_play: Optional[int]
    terminal: bool
    longest_road_player_idxs: List[int]
    most_clusters_player_idxs: List[int]
    winners: List[int]
    market_refills: List[MarketRefill]


    def getlegalactionsforplayer(self, player_idx, repeat_player, last_action):

        if last_action == "DRAW_ROUTE":

        elif last_action in ("DRAW_UNIT_DECK", "DRAW_UNIT_FACEUP"):
            f = s.fig
            non_wild_card_spots = [] # getnonwildspotnums(s)
            action_specs = []
            if self.getsettingvalue("action_draw_unit_deck") and self.anyunitcardsleft():
                action_specs.append(ActionSpec(f, player_idx, "DRAW_UNIT_DECK"))
            if self.getsettingvalue("action_draw_unit_faceup") and non_wild_card_spots:
                action_specs.append(
                    ActionSpec(
                        player_idx=player_idx,
                        action_name="DRAW_UNIT_FACEUP",
                        draw_faceup_spots={spot_num: self.faceup_spots[spot_num] for spot_num in non_wild_card_spots},
                    )
                )
            return action_specs

        else:
            self.getlegalactionsforplayer_default(player_idx, repeat_player, last_action)



    def getlegalactionsforplayer_default(s::State, player_idx, repeat_player, last_action):
        min_initial_routes = getsettingvalue(s.fig, :min_initial_routes)
        min_chosen_routes = getsettingvalue(s.fig, :min_chosen_routes)

        # Initial Route Card Discard
        if getsettingvalue(s, :action_route_discard) && length(s.action_history) < s.game.num_players
            return [
                ActionSpec(
                    player_idx=player_idx, 
                    action_name=ROUTE_DISCARD,
                    return_route_option_sets=getrouteoptionsets(s, player_idx, min_initial_routes),
                )
            ]
        end

        action_specs = ActionSpec[]
        if getsettingvalue(s, :action_draw_unit_faceup) && !isempty(getvalidspotnums(s))
            push!(
                action_specs, 
                ActionSpec(
                    player_idx=player_idx, 
                    action_name=DRAW_UNIT_FACEUP,
                    draw_faceup_spots=Dict((spot_num, s.faceup_spots[spot_num]) for spot_num in getvalidspotnums(s)),
                )
            )
        end

        if getsettingvalue(s, :action_draw_route) && (length(s.route_cards) + length(s.route_discards)) >= min_chosen_routes
            push!(action_specs, ActionSpec(s.fig, player_idx, :DRAW_ROUTE))
        end

        if getsettingvalue(s, :action_draw_unit_deck) && (!isempty(s.unit_cards) || !isempty(s.unit_discards))
            push!(action_specs, ActionSpec(s.fig, player_idx, :DRAW_UNIT_DECK))
        end

        if getsettingvalue(s, :action_claim_path)
            append!(action_specs, getclaimpathactionspecs(s, player_idx))
        end

        if getsettingvalue(s.fig, :action_claim_point)
            append!(action_specs, getclaimpointactionspecs(s, player_idx))
        end

        action_specs



    def get_legal_action_specs(self, player_idx):
        # Causal function chain: gettoplay => getlegalactions => isterminal
        if self.terminal:
            return []
        if player_idx not in self.get_toplay():
            return []
        return getlegalactionsforplayer(state, player_idx, getrepeatplayerkey(state, player_idx), getlastactionkey(state))



    def get_all_legal_actions(self):
        to_play = self.get_toplay()[0]
        all_actions = []
        for action_spec in self.get_legal_action_specs(to_play):
            if action_spec.action_name == "CLAIM_POINT":
                all_actions.extend(action_spec.get_all_actions())
        return all_actions

    def get_toplay(self):
        last_action_key = self.getlastactionkey()

        if last_action_key is None:
            if self.getsettingvalue("action_route_discard"):
                return list(range(1, self.game.num_players + 1))
            return [self.getfirstplayeridx(self.game)]
        
        elif last_action_key == "ROUTE_DISCARD":
            num_actions_taken = len(self.action_history)
            if num_actions_taken < self.game.num_players:
                already_discarded_routes = [a.player_idx for a in s.action_history]
                return list(set(range(1, self.game.num_players + 1)) - set(already_discarded_routes))
            elif num_actions_taken == self.game.num_players:
                return [self.getfirstplayeridx(self.game)]
            return [self.getlastplayeridxplus1()]
        
        elif last_action_key == "DRAW_ROUTE":
            return [self.getlasttoplay()]
        
        elif last_action_key in ("DRAW_UNIT_DECK", "DRAW_UNIT_FACEUP"):
            if not self.anyunitcardsleft():
                return [self.getlastplayeridxplus1()]
            if self.lastactionwas("DRAW_UNIT_FACEUP"):
                if self.iscardnumwild(self.fig, self.getlastaction().draw_faceup_unit_card_num):
                    return [self.getlastplayeridxplus1()]
            last_toplay = self.getlasttoplay()
            if last_toplay != self.getlastlasttoplay() or self.lastlastactionwas("ROUTE_DISCARD"):
                return [last_toplay]
            return [self.getlastplayeridxplus1()]
        
        return [self.getlastplayeridxplus1()]



 
    
@dispatch(State, int, str, str)
def getlegalactionsforplayer_draw_route(self, player_idx, repeat_player, last_action):
    min_chosen_routes = self.getsettingvalue("min_chosen_routes")
    if not self.getsettingvalue("action_route_discard"):
        return []
    return [
        ActionSpec(
            player_idx=player_idx,
            action_name="ROUTE_DISCARD",
            return_route_option_sets=[] # TODO: getrouteoptionsets(s, player_idx, min_chosen_routes),
        )
    ]       


@dataclass(frozen=True)
class QValueTrajectories:
    scores: List[List[int]]
    q_values: List[int]
    formulas: List[QValueFormula]
    states: List[State]
    actions: List[Action]


@dataclass(frozen=True)
class LoggedAction:
    id: int
    uuid: UUID
    created_at: Optional[datetime]
    logged_game_uuid: UUID
    player_uuid: UUID
    player_idx: int
    action_name: str
    completion_uuid: Optional[UUID]
    game_idx: int
    action_json: str


@dataclass(frozen=True)
class Episode:
    states: List[State]
    logged_actions: List[LoggedAction]
    actions: List[Action]
    rewards: List[int]
    returns: List[int]
    private_scores: List[int]
    player_idx: int  # Adjust default if needed

@dataclass(frozen=True)
class RouteStatus:
    route_idx: int
    completed: bool





@dataclass(frozen=True)
class PublicPlayerInfo:
    score: int  # Deprecated field (rename final_score to score and use that)
    num_pieces: int
    num_point_pieces: int
    num_route_cards: int
    num_unit_cards: int
    paths: List[int]
    points: List[UUID]
    completed_clusters: List[UUID]
    route_statuses: List[RouteStatus]
    longest_road: List[int]
    longest_road_len: int
    final_score: Optional[PlayerScore]

@dataclass(frozen=True)
class PublicState:
    fig: Fig
    logged_game_uuid: UUID
    game_idx: int
    action_history: List[Action]
    to_play: List[int]
    num_route_cards: int
    num_route_discards: int
    num_unit_cards: int
    num_unit_discards: int
    faceup_spots: List[Optional[int]]
    player_hands: List[PublicPlayerInfo]
    captured_segments: List[CapturedSegment]
    captured_points: List[CapturedPoint]
    last_to_play: Optional[int]
    terminal: bool
    longest_road_player_idxs: List[int]
    most_clusters_player_idxs: List[int]
    winners: List[int]
    market_refills: List[MarketRefill]


@dataclass(frozen=True)
class SegmentStatus:
    path_num: int
    path_segment_num: int
    captured_by_me: bool
    captured_by_other: bool
    available_to_me: bool
    status: str
    segment: Any



@dataclass(frozen=True)
class OptionSet:
    option_idxs: Set[int]


@dataclass(frozen=True)
class PathCombos:
    path_idx: int
    default_combo: str
    sample_fulfillment: List[int]


@dataclass(frozen=True)
class PointCombos:
    point_uuid: UUID
    default_combo: str
    sample_fulfillment: List[int]


@dataclass(frozen=True)
class ActionSpec:
    return_route_option_sets: List[OptionSet]
    draw_faceup_spots: dict[int, int]
    paths: List[PathCombos]
    points: List[PointCombos]
    # These two fields are required (no default) so must be passed as keywords.
    player_idx: int
    action_name: str


@dataclass(frozen=True)
class PrivateState:
    public_state: PublicState
    legal_actions: List[ActionSpec]
    segment_statuses: List[SegmentStatus]
    hand: PlayerInfo

@dataclass(frozen=True)
class StateUpdate:
    prev: Optional[State]
    prev_action: Optional[Action]
    curr: State



@dataclass(frozen=True)
class Completion:
    id: int
    uuid: UUID
    created_at: Optional[datetime]
    price: float
    name: str
    request_body: str
    completion: str
    prompt: str
    prompt_ver: int
    prompt_hash: str
    request_body_hash: str
    system_prompt_ver: int
    schema_ver: int
    response_body: str
    browser_uuid: Optional[UUID]
    user_uuid: Optional[UUID]
    logged_game_uuid: UUID
    llm_uuid: UUID
    t: float
    num_in_tok: int
    num_out_tok: int

@dataclass(frozen=True)
class ConnectionInputParams:
    page_size: Optional[int]
    cursor_cols: Optional[List[str]]
    cursor_direction: Optional[str]
    after: Optional[str]
    before: Optional[str]

@dataclass(frozen=True)
class BoardLinkStatus:
    link_num: int
    captured_by_me: bool
    captured_by_other: bool
    segments_capturable: int
    total_segments: int

@dataclass(frozen=True)
class BoardPathStatus:
    path_num: int
    captured_by_me: bool
    captured_by_other: bool
    segments_capturable: int
    total_segments: int
    sample_capture_unit_nums: Optional[List[int]]


# 1. Hyperparams
@dataclass(frozen=True)
class Hyperparams:
    learning_rate: float
    batch_size: int
    num_epochs: int
    eval_interval: int
    dropout: float
    shuffle: bool
    augmentation: bool
    early_stopping: bool
    early_stopping_loss_threshold: float

# 2. Datatag
@dataclass(frozen=True)
class Datatag:
    id: int
    uuid: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    name: str
    context: str
    context_idx: int

# 3. UserTag
@dataclass(frozen=True)
class UserTag:
    id: int
    uuid: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    name: str
    context: str
    context_idx: int
    size: int
    user_uuid: UUID

# 4. NetSample
@dataclass(frozen=True)
class NetSample:
    id: int
    uuid: Optional[UUID]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    name: Optional[str]
    context: str
    multiplier: int
    notes: Optional[str]
    feature_filter_uuid: Optional[UUID]
    x_checksum: int
    xy_checksum: int
    y_checksum: int
    x_json: str
    y_json: Optional[str]
    recorded_yhat_json: Optional[str]
    archived: bool
    tf1: int
    tf2: int
    tf3: int
    tf4: int
    tf5: int
# Note: The Julia @scope NetSample :archived => false is omitted.

# 5. QNetVersion
@dataclass(frozen=True)
class QNetVersion:
    id: int
    uuid: UUID
    q_net_uuid: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    trained_at: Optional[datetime]
    name: Optional[str]
    source_size: int
    train_loss: Optional[float]
    train_acc: Optional[float]
    queued_at: Optional[datetime]
    training_failed_at: Optional[datetime]
    training_started_at: Optional[datetime]
    architecture: str
    hyperparams_json: str
    hyperparams_checksum: int
    static_board_config_uuid: UUID
# Note: @tablename QNetVersion :q_net_versions is omitted.

# 6. NetVersion
@dataclass(frozen=True)
class NetVersion:
    id: int
    uuid: UUID
    net_uuid: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    trained_at: Optional[datetime]
    name: Optional[str]
    context: str
    feed_uuid: UUID
    train_checksum: int
    test_checksum: int
    source_size: int
    train_loss: Optional[float]
    test_loss: Optional[float]
    train_acc: Optional[float]
    test_acc: Optional[float]
    queued_at: Optional[datetime]
    retest_queued: bool
    training_failed_at: Optional[datetime]
    training_started_at: Optional[datetime]
    architecture: str
    domain_config_json: str
    config_checksum: int
    hyperparams_json: str
    hyperparams_checksum: int

# 7. Feed
@dataclass(frozen=True)
class Feed:
    id: int
    uuid: Optional[UUID]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    context: str
    targeta_uuid: Optional[UUID]
    targetb_uuid: Optional[UUID]
    ratio: float
    source_size: Optional[int]
    a_checksum: Optional[int]
    b_checksum: Optional[int]

# 8. QNet
@dataclass(frozen=True)
class QNet:
    id: int
    uuid: UUID
    created_at: Optional[datetime]
    name: str
    architecture: str
    hyperparams_json: str
    hyperparams_checksum: int
    static_board_config_uuid: UUID
# Note: @scope QNet :archived => false and @tablename QNet :q_nets are omitted.

# 9. Net
@dataclass(frozen=True)
class Net:
    id: int
    uuid: UUID
    created_at: Optional[datetime]
    name: str
    context: str
    architecture: str
    feed_uuid: UUID
    domain_config_json: str
    config_checksum: int
    hyperparams_json: str
    hyperparams_checksum: int
    dev_default_uuid: Optional[UUID]
    default_uuid: Optional[UUID]
    filters_checksum: int
    filters_json: str
# Note: @scope Net :archived => false is omitted.

# 10. DeepQModel
@dataclass(frozen=True)
class DeepQModel:
    net: Net

# 11. DeepQSample
@dataclass(frozen=True)
class DeepQSample:
    sample: NetSample

# 12. DeepQSample2
@dataclass(frozen=True)
class DeepQSample2:
    x: Any
    y: Any

# 13. Source
@dataclass(frozen=True)
class Source:
    id: int
    uuid: Optional[UUID]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    datatag_uuid: UUID
    feed_uuid: UUID

# 14. DeepQFeedAnalysis
@dataclass(frozen=True)
class DeepQFeedAnalysis:
    uuid: UUID
    input_system_uuids: List[UUID]
    input_make_uuids: List[UUID]
    input_measurement_uuids: List[UUID]
    input_action_uuids: List[UUID]
    input_tag_uuids: List[UUID]
    output_action_uuids: List[UUID]
    output_tag_uuids: List[UUID]

# 15. DeepQSampleX
# Note: DeepQInputNode should be defined elsewhere.
@dataclass(frozen=True)
class DeepQSampleX:
    nodes: List[DeepQInputNode]  # Forward reference

# 16. DeepQSampleY
# Note: DeepQTargetNode should be defined elsewhere.
@dataclass(frozen=True)
class DeepQSampleY:
    nodes: List[DeepQTargetNode]  # Forward reference






# 18. NamePrScore
@dataclass(frozen=True)
class NamePrScore:
    uuid: Optional[UUID]
    name: str
    pr: float  # Using float in place of Float16
    score: float  # Using float in place of Float16

# 19. UserSession
@dataclass(frozen=True)
class UserSession:
    name: str
    email: str

# 20. MatchingNet
@dataclass(frozen=True)
class MatchingNet:
    is_default: bool
    net: Net

# 21. DeepQInferResult
@dataclass(frozen=True)
class DeepQInferResult:
    uuid: UUID
    hello: str
    q_value: int

# 22. FeatureNote
@dataclass(frozen=True)
class FeatureNote:
    name: str
    from_: int  # Renamed from 'from' since it's a reserved keyword in Python
    to: int



@dataclass(frozen=True)
class GQLMatrixRow:
    cols: List[float]  # In Julia these are Float32 values

@dataclass(frozen=True)
class GQLMatrixItem:
    i: Optional[int]           # Corresponds to Union{Nothing,Int} in Julia (Nothing -> None)
    f: Optional[float]         # Corresponds to Union{Nothing,Float32}
    is_embed: bool
    notes: Optional[List[str]] # Corresponds to Union{Nothing,Vector{String}}

@dataclass(frozen=True)
class GQLMatrix:
    is_embed: bool
    nrows: int
    ncols: int
    items: List[GQLMatrixItem]

@dataclass(frozen=True)
class GNNIn:
    gf: List[GQLMatrix]
    nf: List[GQLMatrix]
    ef: List[GQLMatrix]


@dataclass(frozen=True)
class ActionValue:
    action: Action
    value: float  # Using float (which is a double in Python) to represent Float32

@dataclass(frozen=True)
class ViewConfigInput:
    latitude: float
    longitude: float
    zoom: float

@dataclass(frozen=True)
class BoardInput:
    # Optional fields use None (instead of Julia's missing/nothing)
    name: Optional[str]
    map_style_uuid: Optional[UUID]
    initial_view_config: Optional[ViewConfigInput]
    initial_view_config_json: Optional[str]
    fly_to_game_duration: Optional[int]
    game_view_config: Optional[ViewConfigInput]
    game_view_config_json: Optional[str]
    point_marker_radius: Optional[int]
    point_marker_radius_in_pixels: Optional[float]
    map_projection: Optional[str]
    uuid: UUID

@dataclass(frozen=True)
class DeepQNode2:
    num: int
    capture_enabled: bool
    captured_by_me: bool
    captured_by_other: bool
    available_to_me: bool

@dataclass(frozen=True)
class DeepQNode:
    is_cluster: bool



@dataclass(frozen=True)
class DeepQEdge:
    status: SegmentStatus

@dataclass(frozen=True)
class PointStatus:
    uuid: UUID
    fulfillable: bool
    sample_fulfillment: List[OrderedPointFullfillment]

@dataclass(frozen=True)
class PathStatus:
    num: int
    fulfillable: bool
    segment_statuses: List[SegmentStatus]
    sample_fulfillment: List[OrderedFullfillment]


@dataclass(frozen=True)
class ActionInput:
    # Required fields come first.
    player_idx: int
    action_name: str
    # Optional fields follow.
    return_route_cards: Set[int]
    point_uuid: Optional[UUID]
    path_idx: Optional[int]
    unit_combo: Optional[str]
    draw_faceup_unit_card_num: Optional[int]
    draw_faceup_spot_num: Optional[int]

@dataclass(frozen=True)
class LoggedActionInput:
    action_input: ActionInput
    logged_game_uuid: UUID
    game_idx: int

@dataclass(frozen=True)
class ActionQValue:
    action: Optional[Action]
    q_value: int

@dataclass(frozen=True)
class Trajectory:
    player_idx: int
    action_q_values: List[ActionQValue]




@dataclass(frozen=True)
class QFunPolicy:
    def get_next_action(self, s):
        action_name = random.randint(1, 10)
        player_idx = gettoplay(s)[0]
        return AltAction(action_name=action_name, player_idx=player_idx)

    def get_imagined_state(self, player_idx, private_state, public_state, hidden_state_estimator):
        return None



@dataclass(frozen=True)
class UnitCount:
    unit_num: int
    count: int

@dataclass(frozen=True)
class SneakPeek:
    next_unit_card_num: Optional[int]











