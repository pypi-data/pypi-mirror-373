import logging
import random
from uuid import uuid4
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional, Set, TypeVar, Generic, Union
from uuid import UUID
import json
from multipledispatch import dispatch
from functools import reduce
from pyrsistent import PClass, field
from pyrsistent import v, pvector, PVector
import numpy as np
from functools import cmp_to_key
from itertools import combinations as itertools_combinations, chain
from collections import deque

class NoAction(PClass):
    pass

class RouteDiscardAction(PClass):
    pass

class DrawUnitDeckAction(PClass):
    pass

class DrawUnitFaceupAction(PClass):
    pass

class ClaimPointAction(PClass):
    pass

class MovePiecesToPathAction(PClass):
    pass


class TrueType(PClass):
    pass

class FalseType(PClass):
    pass


def generate_uuid_with_rng(rng):
    # uuid4 uses 128 bits, but we need 16 bytes (128 bits) for the UUID
    # Generate 16 random bytes using the seeded rng
    random_bytes = bytes(rng.getrandbits(8) for _ in range(16))
    # Create a UUID from the random bytes
    return UUID(bytes=random_bytes, version=4)


def getbooltype(bool):
    if bool:
        return TrueType()
    return FalseType()


class FrozenLenScore(PClass):
    length = field(type=int)
    score = field(type=int)
    def __todict__(self):
        return {
            "len": self.length,
            "score": self.score,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenLenScore(
            length=d["len"],
            score=d["score"]
        )


class Hook(PClass):
    uuid = field(type=str)
    name = field(type=str)
    when = field(type=str)
    code = field(type=str)
    def __todict__(self):
        return {
            "uuid": str(self.uuid),
            "name": self.name,
            "when": self.when,
            "code": self.code,
        }
    @staticmethod
    def __fromdict__(d):
        return Hook(
            uuid=str(d["uuid"]),
            name=d["name"],
            when=d["when"],
            code=d["code"],
        )


class FrozenLink2(PClass):
    num = field(type=int)
    uuid = field(type=str)
    c1 = field(type=str)
    c2 = field(type=str)
    length = field(type=int)
    width = field(type=int)
    special1 = field(type=bool)
    special2 = field(type=bool)
    score = field(type=int)  # Default score to 0
    def __todict__(self):
        return {
            "num": self.num,
            "uuid": str(self.uuid),
            "c1": str(self.c1),
            "c2": str(self.c2),
            "length": self.length,
            "width": self.width,
            "special1": self.special1,
            "special2": self.special2,
            "score": self.score,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenLink2(
            num=d["num"],
            uuid=str(d["uuid"]),
            c1=str(d["c1"]),
            c2=str(d["c2"]),
            length=d["length"],
            width=d["width"],
            special1=d["special1"],
            special2=d["special2"],
            score=d["score"],
        )


# Implementing the following Julia function:
# struct ScoreDiff
#     a::Int
#     b::Int
# end
class ScoreDiff(PClass):
    a = field(type=int)
    b = field(type=int)
    def __todict__(self):
        return {
            "a": self.a,
            "b": self.b,
        }
    @staticmethod
    def __fromdict__(d):
        return ScoreDiff(
            a=d["a"],
            b=d["b"]
        )


class RouteStatus(PClass):
    route_uuid = field(type=str)
    completed = field(type=bool)
    def __todict__(self):
        return {
            "route_uuid": self.route_uuid,
            "completed": self.completed,
        }
    @staticmethod
    def __fromdict__(d):
        return RouteStatus(
            route_uuid=d["route_uuid"],
            completed=d["completed"]
        )


# Implementing the following Julia function:
# struct QValueFormula
#     q_num::Union{Nothing,Int}
#     score_diff::ScoreDiff
#     function QValueFormula(formula)
#         new(formula.q_num, ScoreDiff(formula.score_diff...))
#     end
# end
class QValueFormula(PClass):
    q_num = field(type=(int, type(None)), initial=None)  # Union{Nothing,Int}
    score_diff = field(type=ScoreDiff)  # ScoreDiff
    def __todict__(self):
        return {
            "q_num": self.q_num,
            "score_diff": self.score_diff.__todict__()
        }
    @staticmethod
    def __fromdict__(d):
        return QValueFormula(
            q_num=d.get("q_num"),
            score_diff=ScoreDiff.__fromdict__(d["score_diff"])
        )


# Implementing the following Julia function:
# struct QValueTrajectories
#     scores::Vector{Vector{Int}}
#     q_values::Vector{Int}
#     formulas::Vector{QValueFormula}
#     states::Vector{State}
#     actions::Vector{Action}
# end
class QValueTrajectories(PClass):
    scores = field(type=list)  # List[List[int]]
    q_values = field(type=list)  # List[int]
    formulas = field(type=list)  # List[QValueFormula]
    states_no_terminal = field(type=list)  # List[State]
    actions = field(type=list)  # List[Action]
    def __todict__(self):
        return {
            "scores": self.scores,
            "q_values": self.q_values,
            "formulas": [f.__todict__() for f in self.formulas],
            "states_no_terminal": [s.__todict__() for s in self.states_no_terminal],
            "actions": [a.__todict__() for a in self.actions],
        }
    @staticmethod
    def __fromdict__(d):
        return QValueTrajectories(
            scores=d["scores"],
            q_values=d["q_values"],
            formulas=[QValueFormula.__fromdict__(f) for f in d["formulas"]],
            states_no_terminal=[State.__fromdict__(s) for s in d["states_no_terminal"]],
            actions=[AltAction.__fromdict__(a) for a in d["actions"]],
        )



# Implementing the following Julia function:
# struct CapturedPoint
#     player_num::Int
#     point_uuid::UUID
# end
class CapturedPoint(PClass):
    player_num = field(type=int)
    point_uuid = field(type=str)
    def __todict__(self):
        return {
            "player_num": self.player_num,
            "point_uuid": str(self.point_uuid),
        }
    @staticmethod
    def __fromdict__(d):
        return CapturedPoint(
            player_num=d["player_num"],
            point_uuid=d["point_uuid"]
        )


# Implementing the following Julia function:
# struct CapturedSegment
#     player_num::Int
#     segment_uuid::UUID
# end
class CapturedSegment(PClass):
    player_num = field(type=int)
    segment_uuid = field(type=str)
    def __todict__(self):
        return {
            "player_num": self.player_num,
            "segment_uuid": str(self.segment_uuid),
        }
    @staticmethod
    def __fromdict__(d):
        return CapturedSegment(
            player_num=d["player_num"],
            segment_uuid=d["segment_uuid"]
        )


class FrozenPoint2(PClass):
    num = field(type=int)
    uuid = field(type=str)
    def __todict__(self):
        return {
            "num": self.num,
            "uuid": self.uuid,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenPoint2(
            num=d["num"],
            uuid=d["uuid"]
        )


class FrozenCluster(PClass):
    uuid = field(type=str)
    points = field(type=list)  # List[UUID]
    score = field(type=int)
    # uuid: UUID
    # points: List[UUID]
    # score: int
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "points": self.points,
            "score": self.score,
        }



# Implementing the following Julia function:
# @kwdef struct FrozenSegment
#     uuid::UUID
#     link_uuid::UUID
#     unit_uuid::Union{Nothing,UUID}
#     path_idx::Int
#     idx::Int
# end
class FrozenSegment(PClass):
    uuid = field(type=str)
    link_uuid = field(type=str)
    unit_uuid = field(type=(str, type(None)), initial=None)
    path_idx = field(type=int)
    idx = field(type=int)
    pieces = field(type=list)  # List[Piece]
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "link_uuid": self.link_uuid,
            "unit_uuid": self.unit_uuid,
            "path_idx": self.path_idx,
            "idx": self.idx,
            "pieces": [p.__todict__() for p in self.pieces],
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenSegment(
            uuid=d["uuid"],
            link_uuid=d["link_uuid"],
            unit_uuid=d.get("unit_uuid"),  # Handle None case
            path_idx=d["path_idx"],
            idx=d["idx"],
            pieces=[Piece.__fromdict__(p) for p in d["pieces"]]
        )


# Implementing the following Julia function:
# struct OrderedSegment
#     path_segment_num::Int
#     segment
# end
class OrderedSegment(PClass):
    path_segment_num = field(type=int)
    segment = field(type=FrozenSegment)  # UUID
    def __todict__(self):
        return {
            "path_segment_num": self.path_segment_num,
            "segment": self.segment.__todict__(),
        }
    @staticmethod
    def __fromdict__(d):
        return OrderedSegment(
            path_segment_num=d["path_segment_num"],
            segment=FrozenSegment.__fromdict__(d["segment"])
        )


# Implementing the following Julia function:
# struct SegmentStatus
#     path_num::Int
#     path_segment_num::Int
#     captured_by_me::Bool
#     captured_by_other::Bool
#     available_to_me::Bool
#     status::String
#     segment
# end
class SegmentStatus(PClass):
    path_idx = field(type=int)
    path_num = field(type=int)
    path_segment_num = field(type=int)
    captured_by_me = field(type=bool)
    captured_by_other = field(type=bool)
    available_to_me = field(type=bool)
    status = field(type=str)
    segment = field(type=FrozenSegment)  # UUID
    def __todict__(self):
        return {
            "path_idx": self.path_idx,
            "path_num": self.path_num,
            "path_segment_num": self.path_segment_num,
            "captured_by_me": self.captured_by_me,
            "captured_by_other": self.captured_by_other,
            "available_to_me": self.available_to_me,
            "status": self.status,
            "segment": self.segment.__todict__(),
        }
    @staticmethod
    def __fromdict__(d):
        return SegmentStatus(
            path_idx=d["path_idx"],
            path_num=d["path_num"],
            path_segment_num=d["path_segment_num"],
            captured_by_me=d["captured_by_me"],
            captured_by_other=d["captured_by_other"],
            available_to_me=d["available_to_me"],
            status=d["status"],
            segment=FrozenSegment.__fromdict__(d["segment"])
        )


# Implementing the following Julia function:
# struct OrderedFullfillment
#     segment_num::Int
#     unit_card_num::Int
# end
class OrderedFullfillment(PClass):
    segment_num = field(type=int)
    unit_card_num = field(type=int)
    def __todict__(self):
        return {
            "segment_num": self.segment_num,
            "unit_card_num": self.unit_card_num,
        }
    @staticmethod
    def __fromdict__(d):
        return OrderedFullfillment(
            segment_num=d["segment_num"],
            unit_card_num=d["unit_card_num"]
        )

# Implementing the following Julia function:
# struct PathStatus
#     num::Int
#     fulfillable::Bool
#     segment_statuses::Vector{SegmentStatus}
#     sample_fulfillment::Vector{OrderedFullfillment}
# end
class PathStatus(PClass):
    idx = field(type=int)
    num = field(type=int)
    fulfillable = field(type=bool)
    segment_statuses = field(type=list)  # List[SegmentStatus]
    sample_fulfillment = field(type=list)  # List[OrderedFullfillment]
    def __todict__(self):
        return {
            "idx": self.idx,
            "num": self.num,
            "fulfillable": self.fulfillable,
            "segment_statuses": [x.__todict__() for x in self.segment_statuses],
            "sample_fulfillment": [x.__todict__() for x in self.sample_fulfillment],
        }
    @staticmethod
    def __fromdict__(d):
        return PathStatus(
            idx=d["idx"],
            num=d["num"],
            fulfillable=d["fulfillable"],
            segment_statuses=[SegmentStatus.__fromdict__(x) for x in d["segment_statuses"]],
            sample_fulfillment=[OrderedSegment.__fromdict__(x) for x in d["sample_fulfillment"]]
        )


# Implementing the following Julia function:
# @kwdef struct FrozenLinkPath
#     is_mixed::Bool
#     segments::Vector{FrozenSegment}
# end
class FrozenLinkPath(PClass):
    is_mixed = field(type=bool)
    segments = field(type=list)  # List[FrozenSegment]
    def __todict__(self):
        return {
            "is_mixed": self.is_mixed,
            "segments": [x.__todict__() for x in self.segments],
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenLinkPath(
            is_mixed=d["is_mixed"],
            segments=[FrozenSegment.__fromdict__(x) for x in d["segments"]]
        )


@dataclass(frozen=True)
class FrozenPath:
    num: int
    link_num: int
    start_point_uuid: str
    end_point_uuid: str
    start_point_num: int
    end_point_num: int
    path: FrozenLinkPath
    def __todict__(self):
        return {
            "num": self.num,
            "link_num": self.link_num,
            "start_point_uuid": self.start_point_uuid,
            "end_point_uuid": self.end_point_uuid,
            "start_point_num": self.start_point_num,
            "end_point_num": self.end_point_num,
            "path": self.path.__todict__(),
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenPath(
            num=d["num"],
            link_num=d["link_num"],
            start_point_uuid=d["start_point_uuid"],
            end_point_uuid=d["end_point_uuid"],
            start_point_num=d["start_point_num"],
            end_point_num=d["end_point_num"],
            path=FrozenLinkPath.__fromdict__(d["path"])
        )


class FrozenSetting(PClass):
    name = field(type=str)
    value_json = field(type=str)
    # name: str
    # value_json: str
    def __todict__(self):
        return {
            "name": self.name,
            "value_json": self.value_json,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenSetting(
            name=d["name"],
            value_json=d["value_json"]
        )


class FrozenDeckUnit2(PClass):
    num = field(type=int)
    quantity = field(type=int)
    is_wild = field(type=bool)
    unit_uuid = field(type=str)
    def __todict__(self):
        return {
            "num": self.num,
            "quantity": self.quantity,
            "is_wild": self.is_wild,
            "unit_uuid": self.unit_uuid,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenDeckUnit2(
            num=d["num"],
            quantity=d["quantity"],
            is_wild=d["is_wild"],
            unit_uuid=d["unit_uuid"]
        )


@dataclass(frozen=True)
class FrozenBoardConfigDataclass:
    deck_units: List[FrozenDeckUnit2]
    len_scores: List[FrozenLenScore]
    links: List[FrozenLink2]
    clusters: List[FrozenCluster]
    points: List[FrozenPoint2]
    board_paths: List[FrozenPath]
    settings: List[FrozenSetting]


@dataclass(frozen=True)
class Action:
    player_idx: int
    action_name: str
    return_route_cards: Set[int]
    point_uuid: Optional[UUID]
    path_idx: Optional[int]
    unit_combo: Optional[str]
    draw_faceup_unit_card_num: Optional[int]
    draw_faceup_spot_num: Optional[int]
    def __str__(self):
        return f"Action({self.action_name})"
    def __repr__(self):
        return self.__str__()


class FrozenRoute(PClass):
    num = field(type=int)
    uuid = field(type=str)
    point_a_uuid = field(type=str)
    point_b_uuid = field(type=str)
    score = field(type=int)
    start_num = field(type=int)
    end_num = field(type=int)
    def __todict__(self):
        return {
            "num": self.num,
            "uuid": self.uuid,
            "point_a_uuid": self.point_a_uuid,
            "point_b_uuid": self.point_b_uuid,
            "score": self.score,
            "start_num": self.start_num,
            "end_num": self.end_num,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenRoute(
            num=d["num"],
            uuid=d["uuid"],
            point_a_uuid=d["point_a_uuid"],
            point_b_uuid=d["point_b_uuid"],
            score=d["score"],
            start_num=d["start_num"],
            end_num=d["end_num"]
        )


class FrozenPieceTemplate(PClass):
    uuid = field(type=str)
    idx = field(type=int)
    has_player = field(type=bool)
    quantity = field(type=int)
    seed = field(type=int)
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "idx": self.idx,
            "has_player": self.has_player,
            "quantity": self.quantity,
            "seed": self.seed,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenPieceTemplate(
            uuid=d["uuid"],
            idx=d["idx"],
            has_player=d["has_player"],
            quantity=d["quantity"],
            seed=d["seed"],
        )
    

class FrozenDekCard(PClass):
    uuid = field(type=str)
    idx = field(type=int)
    quantity = field(type=int)
    resource_uuid = field(type=(str, type(None)), initial=None)
    goal_uuid = field(type=(str, type(None)), initial=None)
    is_wild = field(type=bool)
    dek_uuid = field(type=str)
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "idx": self.idx,
            "quantity": self.quantity,
            "resource_uuid": self.resource_uuid,
            "goal_uuid": self.goal_uuid,
            "is_wild": self.is_wild,
            "dek_uuid": self.dek_uuid
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenDekCard(
            uuid=d["uuid"],
            idx=d["idx"],
            quantity=d["quantity"],
            resource_uuid=d["resource_uuid"],
            goal_uuid=d["goal_uuid"],
            is_wild=d["is_wild"],
            dek_uuid=d["dek_uuid"]
        )


class FrozenDek(PClass):
    uuid = field(type=str)
    idx = field(type=int)
    seed = field(type=int)
    dek_cards = field(type=list)  # List[FrozenDekCard]
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "idx": self.idx,
            "seed": self.seed,
            "dek_cards": [card.__todict__() for card in self.dek_cards],
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenDek(
            uuid=d["uuid"],
            idx=d["idx"],
            seed=d["seed"],
            dek_cards=[FrozenDekCard.__fromdict__(card) for card in d["dek_cards"]],
        )
    

class FrozenBonus(PClass):
    uuid = field(type=str)
    code = field(type=str)
    score = field(type=int)
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "code": self.code,
            "score": self.score,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenBonus(
            uuid=d["uuid"],
            code=d["code"],
            score=d["score"],
        )


class FrozenGoal(PClass):
    uuid = field(type=str)
    description = field(type=(str, type(None)), initial=None)
    node_uuids = field(type=(list, type(None)), initial=None)  # List[str]
    edge_uuids = field(type=(list, type(None)), initial=None)
    region_uuids = field(type=(list, type(None)), initial=None)
    score = field(type=int)
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "node_uuids": self.node_uuids,
            "edge_uuids": self.edge_uuids,
            "region_uuids": self.region_uuids,
            "score": self.score,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenGoal(
            uuid=d["uuid"],
            node_uuids=d["node_uuids"],
            edge_uuids=d["edge_uuids"],
            region_uuids=d["region_uuids"],
            score=d["score"]
        )


class FrozenBoardConfig(PClass):
    bonuses = field(type=list)  # List[FrozenBonus]
    goals = field(type=list)  # List[FrozenGoal]
    deks = field(type=list)  # List[FrozenDek]
    piece_templates = field(type=list)  # List[FrozenPieceTemplate]
    routes = field(type=list)  # List[FrozenRoute]
    deck_units = field(type=list)  # List[FrozenDeckUnit2]
    settings = field(type=list)  # List[FrozenSetting]
    points = field(type=list)  # List[FrozenPoint2]
    clusters = field(type=list)  # List[FrozenCluster]
    board_paths = field(type=list)  # List[FrozenPath]
    len_scores = field(type=list)  # List[FrozenLenScore]
    links = field(type=list)  # List[FrozenLink2]
    hooks = field(type=list)  # List[Hook]
    def __todict__(self):
        return {
            "bonuses": [b.__todict__() for b in self.bonuses],
            "goals": [g.__todict__() for g in self.goals],
            "deks": [d.__todict__() for d in self.deks],
            "piece_templates": [x.__todict__() for x in self.piece_templates],
            "routes": [x.__todict__() for x in self.routes],
            "deck_units": [x.__todict__() for x in self.deck_units],
            "settings": [x.__todict__() for x in self.settings],
            "points": [x.__todict__() for x in self.points],
            "clusters": [x.__todict__() for x in self.clusters],
            "board_paths": [x.__todict__() for x in self.board_paths],
            "len_scores": [x.__todict__() for x in self.len_scores],
            "links": [x.__todict__() for x in self.links],
            "hooks": [x.__todict__() for x in self.hooks],
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenBoardConfig(
            bonuses=[FrozenBonus.__fromdict__(x) for x in d['bonuses']],
            goals=[FrozenGoal.__fromdict__(x) for x in d['goals']],
            deks=[FrozenDek.__fromdict__(x) for x in d['deks']],
            piece_templates=[FrozenPieceTemplate.__fromdict__(x) for x in d['piece_templates']],
            routes = initfrozenroutes(d),
            deck_units = getdeckunits(d['deck_units']),
            settings = getsettings(d['settings']),
            points = getpoints(d["points"]),
            clusters = getclusters(d["clusters"]),
            board_paths = getboardpaths(d["board_paths"]),
            len_scores=[FrozenLenScore.__fromdict__(x) for x in d['len_scores']],
            links=[FrozenLink2.__fromdict__(x) for x in d['links']],
            hooks=[Hook.__fromdict__(x) for x in d.get('hooks', [])]
        )


@dispatch(dict)
def initboardconfig(d):
    return FrozenBoardConfig.__fromdict__(d)


class StaticBoardConfig(PClass):
    uuid = field(type=str)
    board_config = field(type=FrozenBoardConfig)
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "board_config": self.board_config.__todict__()
        }
    @staticmethod
    def __fromdict__(d):
        return StaticBoardConfig(
            uuid=d["uuid"],
            board_config=FrozenBoardConfig.__fromdict__(d["board_config"])
        )


@dispatch(dict)
def initfrozenroutes(d):
    pointuuids2nums = {p['uuid']: n for n, p in enumerate(d['points'])}
    return [
        FrozenRoute(
            num=i+1,
            uuid=r['uuid'],
            point_a_uuid=r['point_a_uuid'],
            point_b_uuid=r['point_b_uuid'],
            score=r['score'],
            start_num=pointuuids2nums[r['point_a_uuid']],
            end_num=pointuuids2nums[r['point_b_uuid']],
        )
        for i, r in enumerate(d['routes'])
    ]


MAX_PATH_LENGTH = 100

# Implementing the following Julia function:
# function getfrozenpathscores(b::FrozenBoardConfig)
#     d = Dict()
#     for x in b.len_scores
#         d[x.len] = x.score
#     end
#     [get(d, i, 0) for i in collect(1:MAX_PATH_LENGTH)]
# end
@dispatch(FrozenBoardConfig)
def getfrozenpathscores(b):
    d = {x.length: x.score for x in b.len_scores}
    return [d.get(i, 0) for i in range(1, MAX_PATH_LENGTH + 1)]


# Sample json data
# {"board_paths": [
#         {
#             "num": 1,
#             "path": {
#                 "is_mixed": false,
#                 "segments": [
#                     {
#                         "idx": 0,
#                         "uuid": "54fe6576-13a1-445a-ba19-dd1809798cea",
#                         "path_idx": 0,
#                         "link_uuid": "0e90684e-d9ab-4d31-bb12-33ab4e11c91a",
#                         "unit_uuid": null
#                     }
#                 ]
#             },
#             "link_num": 1,
#             "end_point_num": 6,
#             "start_point_num": 8
#         },
# ]}
def getboardpaths(d):
    return [
        FrozenPath(
            num=x['num'],
            link_num=x['link_num'],
            start_point_uuid=x['start_point_uuid'],
            end_point_uuid=x['end_point_uuid'],
            start_point_num=x['start_point_num'],
            end_point_num=x['end_point_num'],
            path=getlinkpath(x['path']),
        )
        for x in d
    ]


def getlinkpath(d):
    return FrozenLinkPath(
        is_mixed=d['is_mixed'],
        segments=getsegments(d['segments']),
    )


def getsegments(d):
    return [
        FrozenSegment(
            idx=x['idx'],
            uuid=x['uuid'],
            path_idx=x['path_idx'],
            link_uuid=x['link_uuid'],
            unit_uuid=x['unit_uuid'],
            pieces=[],
        )
        for x in d
    ]


def getclusters(d):
    return [
        FrozenCluster(
            uuid=x['uuid'],
            points=[p for p in x['points']],
            score=x['score'],
        )
        for n, x in enumerate(d)
    ]


def getpoints(d):
    return [
        FrozenPoint2(
            num=n,
            uuid=x['uuid'],
        )
        for n, x in enumerate(d)
    ]

def getsettings(d):
    return [
        BoardSetting(
            name=x['name'],
            value_json=x['value_json'],
        )
        for n, x in enumerate(d)
    ]


def getdeckunits(d):
    return [
        FrozenDeckUnit2(
            num=x['num'],
            quantity=x['quantity'],
            is_wild=x['is_wild'],
            unit_uuid=x['unit_uuid']
        )
        for n, x in enumerate(d)
    ]


class BoardSetting(PClass):
    name = field(type=str)
    value_json = field(type=str)
    def __todict__(self):
        return {
            "name": self.name,
            "value_json": self.value_json,
        }




class Fig(PClass):
    # TODO: the two fields below should just be a "StaticBoardConfig" object
    static_board_config_uuid = field(type=str)
    board_config = field(type=FrozenBoardConfig)
    path_scores = field(type=list)  # List[int]
    # graph = field(type=int)
    # path_scores = field(type=int)
    # graph: BoardGraph
    # path_scores: List[int]
    def __todict__(self):
        return {
            "static_board_config_uuid": self.static_board_config_uuid,
            "board_config": self.board_config.__todict__(),
            "path_scores": self.path_scores,
        }
    @staticmethod
    def __fromdict__(d):
        return initfig(
            d["static_board_config_uuid"], 
            FrozenBoardConfig.__fromdict__(d["board_config"]),
        )


@dispatch(str, FrozenBoardConfig)
def initfig(static_board_config_uuid, board_config):
    return Fig(
        static_board_config_uuid=static_board_config_uuid,
        board_config=board_config,
        path_scores=getfrozenpathscores(board_config),
    )


class GameConfig(PClass):
    uuid = field(type=str)
    started_at = field(type=str)
    num_players = field(type=int)
    fig = field(type=Fig)
    seed = field(type=int) 
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "started_at": self.started_at,
            "num_players": self.num_players,
            "fig": self.fig.__todict__(),
            "seed": self.seed,
        }
    @staticmethod
    def __fromdict__(d):
        return GameConfig(
            uuid=d["uuid"],
            started_at=d["started_at"],
            num_players=d["num_players"],
            fig=Fig.__fromdict__(d["fig"]),
            seed=d["seed"]
        )


class ActionDrawUnit:
   def __init__(self):
       pass


# struct PublicState
#     fig::Fig
#     logged_game_uuid::UUID
#     action_history::Vector{Action}
#     to_play::Vector{Int}
#     num_route_cards::Int
#     num_route_discards::Int
#     num_unit_cards::Int
#     num_unit_discards::Int
#     faceup_spots::Vector{Union{Nothing,Int}}
#     player_hands::Vector{PublicPlayerInfo}
#     captured_segments::Vector{CapturedSegment}
#     captured_points::Vector{CapturedPoint}
#     last_to_play::Union{Nothing,Int}
#     terminal::Bool
#     longest_road_player_idxs::Vector{Int}
#     most_clusters_player_idxs::Vector{Int}
#     winners::Vector{Int}
#     market_refills::Vector{MarketRefill}


class AltAction(PClass):
    player_idx = field(type=int)
    action_name = field(type=str)
    path_idx = field(type=(int, type(None)), initial=None)
    return_route_cards = field(type=list, initial=[])  # List[int]
    draw_faceup_unit_card_num = field(type=(int, type(None)), initial=None)
    draw_faceup_spot_num = field(type=(int, type(None)), initial=None)
    point_uuid = field(type=(str, type(None)), initial=None)
    unit_combo = field(type=(str, type(None)), initial=None)  # TODO: should be list of int
    def __todict__(self):
        return {
            "player_idx": self.player_idx,
            "action_name": self.action_name,
            "path_idx": self.path_idx,
            "return_route_cards": self.return_route_cards,
            "draw_faceup_unit_card_num": self.draw_faceup_unit_card_num,
            "draw_faceup_spot_num": self.draw_faceup_spot_num,
            "point_uuid": self.point_uuid,
            "unit_combo": self.unit_combo
        }
    @staticmethod
    def __fromdict__(json_dict):
        return AltAction(
            player_idx=json_dict["player_idx"],
            action_name=json_dict["action_name"],
            path_idx=json_dict.get("path_idx", None),  # Handle missing key gracefully
            return_route_cards=json_dict.get("return_route_cards", []),  # Handle missing key gracefully
            draw_faceup_unit_card_num=json_dict.get("draw_faceup_unit_card_num", None),  # Handle missing key gracefully
            draw_faceup_spot_num=json_dict.get("draw_faceup_spot_num", None),  # Handle missing key gracefully
            point_uuid=json_dict.get("point_uuid", None),  # Handle missing key gracefully
            unit_combo=json_dict.get("unit_combo", None)  # Handle missing key gracefully
        )


class ActionSpec(PClass):
    # # TODO: should remove "player_idx" as it's always the same as "to_play"
    player_idx = field(type=int)
    action_name = field(type=str)
    return_route_option_sets = field(type=list, initial=[])  # List[OptionSet]
    draw_faceup_spots = field(type=dict, initial={})  # Dict{Int, int}
    points = field(type=list, initial=[])  # List[PointCombos]
    paths = field(type=list, initial=[])  # List[PathCombos]
    def __todict__(self):
        return {
            "player_idx": self.player_idx,
            "action_name": self.action_name,
            "return_route_option_sets": [x.__todict__() for x in self.return_route_option_sets],
            "draw_faceup_spots": self.draw_faceup_spots,
            "points": [x.__todict__() for x in self.points],
            "paths": [x.__todict__() for x in self.paths],
        }
    @staticmethod
    def __fromdict__(d):
        print("""d["return_route_option_sets"]""", d["return_route_option_sets"])
        return ActionSpec(
            player_idx=d["player_idx"],
            action_name=d["action_name"],
            return_route_option_sets=[OptionSet.__fromdict__(x) for x in d["return_route_option_sets"]],
            draw_faceup_spots=d["draw_faceup_spots"],
            points=[PointCombos.__fromdict__(x) for x in d["points"]],
            paths=[PathCombos.__fromdict__(x) for x in d["paths"]],
        )


# Implementing the following Julia function:
# struct PathCombos
#     path_idx::Int
#     default_combo::String
#     sample_fulfillment::Vector{Int}
# end
class PathCombos(PClass):
    path_idx = field(type=int)
    default_combo = field(type=str)
    sample_fulfillment = field(type=list)  # List[int]
    def __todict__(self):
        return {
            "path_idx": self.path_idx,
            "default_combo": self.default_combo,
            "sample_fulfillment": self.sample_fulfillment,
        }
    @staticmethod
    def __fromdict__(d):
        return PathCombos(
            path_idx=d["path_idx"],
            default_combo=d["default_combo"],
            sample_fulfillment=d["sample_fulfillment"]
        )


# Implementing the following Julia function:
# struct OptionSet
#     option_idxs::Set{Int}
# end
class OptionSet(PClass):
    option_idxs = field(type=set)  # Set[int]
    def __todict__(self):
        return {
            "option_idxs": list(self.option_idxs),
        }
    @staticmethod
    def __fromdict__(d):
        return OptionSet(
            option_idxs=set(d["option_idxs"])
        )


class PointCombos(PClass):
    point_uuid = field(type=str)
    default_combo = field(type=str)
    sample_fulfillment = field(type=list)  # List[int]
    def __todict__(self):
        return {
            "point_uuid": self.point_uuid,
            "default_combo": self.default_combo,
            "sample_fulfillment": self.sample_fulfillment,
        }
    @staticmethod
    def __fromdict__(d):
        return PointCombos(
            point_uuid=d["point_uuid"],
            default_combo=d["default_combo"],
            sample_fulfillment=d["sample_fulfillment"]
        )


class PlayerInfo(PClass):
    fig = field(type=Fig)
    player_idx = field(type=int)
    new_route_cards = field(type=PVector)  # List[int]
    route_cards = field(type=PVector)  # List[int]
    unit_cards = field(type=PVector)  # List[int]
    completed_routes = field(type=list)  # List[int]
    completed_clusters = field(type=list)  # List[UUID]
    paths = field(type=list)  # List[int]
    points = field(type=list)  # List[UUID]
    tokens = field(type=list)  # List[UUID]
    num_pieces = field(type=int)
    num_point_pieces = field(type=int)
    longest_road = field(type=list)  # List[int]
    longest_road_len = field(type=int)
    final_score = field(type=object)  # Union{Nothing, PlayerScore}
    def __todict__(self):
        return {
            "fig": self.fig.__todict__(),
            "player_idx": self.player_idx,
            "new_route_cards": list(self.new_route_cards),
            "route_cards": list(self.route_cards),
            "unit_cards": list(self.unit_cards),
            "completed_routes": self.completed_routes,
            "completed_clusters": self.completed_clusters,
            "paths": self.paths,
            "points": self.points,
            "tokens": self.tokens,
            "num_pieces": self.num_pieces,
            "num_point_pieces": self.num_point_pieces,
            "longest_road": self.longest_road,
            "longest_road_len": self.longest_road_len,
            "final_score": self.final_score.__todict__() if self.final_score else None,
        }
    @staticmethod
    def __fromdict__(d):
        return PlayerInfo(
            fig=Fig.__fromdict__(d["fig"]),
            player_idx=d["player_idx"],
            new_route_cards=pvector(d["new_route_cards"]),
            route_cards=pvector(d["route_cards"]),
            unit_cards=pvector(d["unit_cards"]),
            completed_routes=d["completed_routes"],
            completed_clusters=d["completed_clusters"],
            paths=d["paths"],
            points=d["points"],
            tokens=d["tokens"],
            num_pieces=d["num_pieces"],
            num_point_pieces=d["num_point_pieces"],
            longest_road=d["longest_road"],
            longest_road_len=d["longest_road_len"],
            final_score=PlayerScore.__fromdict__(d["final_score"]) if d.get("final_score") else None,
        )
    @staticmethod
    def clone(hand):
        return PlayerInfo.__fromdict__(hand.__todict__())


class PublicPlayer(PClass):
    idx = field(type=int)
    pieces = field(type=list)  # List[Piece]
    deck_counts = field(type=list)
    piece_template_counts = field(type=list)
    def __todict__(self):
        return {
            "idx": self.idx,
            "pieces": self.pieces,
            "deck_counts": list(self.deck_counts),
            "piece_template_counts": list(self.piece_template_counts),
        }
    @staticmethod
    def __fromdict__(d):
        return PublicPlayer(
            idx=d["idx"],
            pieces=d["pieces"],
            deck_counts=list(d["deck_counts"]),
            piece_template_counts=list(d["piece_template_counts"]),
        )


class Player(PClass):
    idx = field(type=int)
    pieces = field(type=list)  # List[Piece]
    cards = field(type=list)  # List[Card]
    discard_tray = field(type=list)  # List[Card]
    def __todict__(self):
        return {
            "idx": self.idx,
            "pieces": self.pieces,
            "cards": self.cards,
            "discard_tray": self.discard_tray,
        }
    @staticmethod
    def __fromdict__(d):
        return Player(
            idx=d["idx"],
            pieces=d["pieces"],
            cards=d["cards"],
            discard_tray=d["discard_tray"]
        )
    
class GoalCompletion(PClass):
    goal_uuid = field(type=str)
    complete = field(type=bool, initial=False)
    def __todict__(self):
        return {
            "goal_uuid": self.goal_uuid,
            "complete": self.complete,
        }
    @staticmethod
    def __fromdict__(d):
        return GoalCompletion(
            goal_uuid=d["goal_uuid"],
            complete=d.get("complete")
        )


class PlayerGraph(PClass):
    player_idx = field(type=int)
    neighbors = field(type=list)  # List[List[int]]
    def __todict__(self):
        return {
            "player_idx": self.player_idx,
            "neighbors": self.neighbors,
        }
    @staticmethod
    def __fromdict__(d):
        return PlayerGraph(
            player_idx=d["player_idx"],
            neighbors=d["neighbors"],
        )


class PlayerNode(PClass):
    player_idx = field(type=int)
    node_idx = field(type=int)
    neighbors = field(type=list)  # List[int]
    def __todict__(self):
        return {
            "player_idx": self.player_idx,
            "node_idx": self.node_idx,
            "neighbors": self.neighbors,
        }
    @staticmethod
    def __fromdict__(d):
        return PlayerNode(
            player_idx=d["player_idx"],
            node_idx=d["node_idx"],
            neighbors=d["neighbors"]
        )


class PrivatePlayerScore(PClass):
    items = field(type=list)  # List[ScoreItem2]
    total = field(type=int)
    def __todict__(self):
        return {
            "items": [x.__todict__() for x in self.items], 
            "total": self.total,
        }
    @staticmethod
    def __fromdict__(d):
        return PrivatePlayerScore(
            items=[ScoreItem2.__fromdict__(x) for x in d["items"]],
            total=d["total"]
        )


# Implementing the following Julia function:
# struct PrivateState
#     legal_actions::Vector{ActionSpec}
#     segment_statuses::Vector{SegmentStatus}
#     hand::PlayerInfo
# end
class PrivateState(PClass):
    player_score = field(type=PrivatePlayerScore)
    player = field(type=Player)
    legal_actions_2 = field(type=list)  # List[LegalAction]
    legal_actions = field(type=list)  # List[ActionSpec]
    hand = field(type=PlayerInfo)
    goal_completions = field(type=list, initial=[])  # List[GoalCompletion]
    def __todict__(self):
        return {
            "player_score": self.player_score.__todict__(),
            "player": self.player.__todict__(),
            "legal_actions_2": [x.__todict__() for x in self.legal_actions_2],
            "legal_actions": [x.__todict__() for x in self.legal_actions],
            "hand": self.hand.__todict__(),
            "goal_completions": [x.__todict__() for x in self.goal_completions],
        }
    @staticmethod
    def __fromdict__(d):
        return PrivateState(
            player_score=PrivatePlayerScore.__fromdict__(d["player_score"]),
            player=Player.__fromdict__(d["player"]),
            legal_actions_2=[LegalAction.__fromdict__(x) for x in d["legal_actions_2"]],
            legal_actions=[ActionSpec.__fromdict__(x) for x in d["legal_actions"]],
            hand=PlayerInfo.__fromdict__(d["hand"]),
            goal_completions=[GoalCompletion.__fromdict__(x) for x in d["goal_completions"]],
        )


class PublicDeck(PClass):
    idx = field(type=int)
    uuid = field(type=str)
    units = field(type=list)  # List[Card]
    facedown_stack_len = field(type=int)
    discard_len = field(type=int)
    faceup_spots = field(type=list)  # List[Card]
    def __todict__(self):
        return {
            "idx": self.idx,
            "uuid": self.uuid,
            "units": [unit.__todict__() for unit in self.units],
            "facedown_stack_len": self.facedown_stack_len,
            "discard_len": self.discard_len,
            "faceup_spots": self.faceup_spots,
        }
    @staticmethod
    def __fromdict__(d):
        return PublicDeck(
            idx=d["idx"],
            uuid=d["uuid"],
            units=[Card.__fromdict__(card) for card in d["units"]],
            facedown_stack_len=d["facedown_stack_len"],
            discard_len=d["discard_len"],
            faceup_spots=d["faceup_spots"],
        )


class ActionKeepOptional(PClass):
    card_uuids = field(type=list)  # List[int]
    def __todict__(self):
        return {
            "card_uuids": self.card_uuids,
        }
    @staticmethod
    def __fromdict__(d):
        return ActionKeepOptional(
            card_uuids=d["card_uuids"]
        )
    

class LegalActionKeep(PClass):
    deck_idx = field(type=int)
    min = field(type=(int, type(None)), initial=None)  # Optional[int]
    max = field(type=(int, type(None)), initial=None)  # Optional[int]
    def get_public(self, state):
        return self
    def __todict__(self):
        return {
            "deck_idx": self.deck_idx,
            "min": self.min,
            "max": self.max,
        }
    @staticmethod
    def __fromdict__(d):
        return LegalActionKeep(
            deck_idx=d["deck_idx"],
            min=d.get("min"),  # Handle None case
            max=d.get("max"),  # Handle None case
        )
    

class LegalActionDiscard(PClass):
    deck_idx = field(type=int)
    min = field(type=(int, type(None)), initial=None)  # Optional[int]
    max = field(type=(int, type(None)), initial=None)  # Optional[int]
    def get_public(self, state):
        return self
    def __todict__(self):
        return {
            "deck_idx": self.deck_idx,
            "min": self.min,
            "max": self.max,
        }
    @staticmethod
    def __fromdict__(d):
        return LegalActionDiscard(
            deck_idx=d["deck_idx"],
            min=d.get("min"),  # Handle None case
            max=d.get("max")  # Handle None case
        )


class PublicActionMovePiecesToPathOptional(PClass):
    piece_uuids = field(type=list)  # List[str]
    card_uuids = field(type=list)  # List[int]
    def __todict__(self):
        return {
            "piece_uuids": self.piece_uuids,
            "card_uuids": self.card_uuids,
        }
    @staticmethod
    def __fromdict__(d):
        return PublicActionMovePiecesToPathOptional(
            piece_uuids=d["piece_uuids"],
            card_uuids=d["card_uuids"]
        )


class ActionMovePiecesToPathOptional(PClass):
    piece_uuids = field(type=list)  # List[str]
    card_uuids = field(type=list)  # List[str]
    def get_public(self, state):
        return PublicActionMovePiecesToPathOptional(
            piece_uuids=self.piece_uuids,
            card_uuids=self.card_uuids,
        )
    def __todict__(self):
        return {
            "piece_uuids": self.piece_uuids,
            "card_uuids": self.card_uuids,
        }
    @staticmethod
    def __fromdict__(d):
        return ActionMovePiecesToPathOptional(
            piece_uuids=d["piece_uuids"],
            card_uuids=d["card_uuids"]
        )
    

class PublicLegalActionMovePiecesToPath(PClass):
    path_idx = field(type=int)
    def __todict__(self):
        return {
            "path_idx": self.path_idx
        }
    @staticmethod
    def __fromdict__(d):
        return PublicLegalActionMovePiecesToPath(
            path_idx=d["path_idx"]
        )


class LegalActionMovePiecesToPath(PClass):
    path_idx = field(type=int)
    default = field(type=ActionMovePiecesToPathOptional)  # Optional[MovePiecesToPathAction]
    def get_public(self, state):
        return PublicLegalActionMovePiecesToPath(
            path_idx=self.path_idx,
        )
    def __todict__(self):
        return {
            "path_idx": self.path_idx,
            "default": self.default.__todict__(),
        }
    @staticmethod
    def __fromdict__(d):
        return LegalActionMovePiecesToPath(
            path_idx=d["path_idx"],
            default=ActionMovePiecesToPathOptional.__fromdict__(d["default"])
        )


    
class LegalActionFaceupDraw(PClass):
    deck_idx = field(type=int)
    card_uuid = field(type=str)
    def get_public(self, state):
        return self
    def __todict__(self):
        return {
            "deck_idx": self.deck_idx,
            "card_uuid": self.card_uuid,
        }
    @staticmethod
    def __fromdict__(d):
        return LegalActionFaceupDraw(
            deck_idx=d["deck_idx"],
            card_uuid=d["card_uuid"],
        )


class LegalActionDraw(PClass):
    deck_idx = field(type=int)
    quantity = field(type=int)
    def get_public(self, state):
        return self
    def __todict__(self):
        return {
            "deck_idx": self.deck_idx,
            "quantity": self.quantity,
        }
    @staticmethod
    def __fromdict__(d):
        return LegalActionDraw(
            deck_idx=d["deck_idx"],
            quantity=d["quantity"]
        )
    

class LegalActionDrawDiscard(PClass):
    deck_idx = field(type=int)
    quantity = field(type=int)
    min = field(type=(int, type(None)), initial=None)  # Optional[int]
    max = field(type=(int, type(None)), initial=None)  # Optional[int]
    def get_public(self, state):
        return self
    def __todict__(self):
        return {
            "deck_idx": self.deck_idx,
            "quantity": self.quantity,
            "min": self.min,
            "max": self.max,
        }
    @staticmethod
    def __fromdict__(d):
        return LegalActionDrawDiscard(
            deck_idx=d["deck_idx"],
            quantity=d["quantity"],
            min=d.get("min"),  # Handle None case
            max=d.get("max")  # Handle None case
        )


class PublicLegalAction(PClass):
    player_idx = field(type=int)
    name = field(type=str)
    discard = field(type=(LegalActionDiscard, type(None)), initial=None)  # LegalActionDiscard
    keep = field(type=(LegalActionKeep, type(None)), initial=None)  # LegalActionKeep
    draw = field(type=(LegalActionDraw, type(None)), initial=None)  # LegalActionDraw
    draw_discard = field(type=(LegalActionDrawDiscard, type(None)), initial=None)  # LegalActionDrawDiscard
    faceup_draw = field(type=(LegalActionFaceupDraw, type(None)), initial=None)  # LegalActionFaceupDraw
    move_pieces_to_path = field(type=(PublicLegalActionMovePiecesToPath, type(None)), initial=None)  # PublicLegalActionMovePiecesToPath
    def __todict__(self):
        return {
            "player_idx": self.player_idx,
            "name": self.name,
            "discard": self.discard.__todict__() if self.discard else None,
            "keep": self.keep.__todict__() if self.keep else None,
            "draw": self.draw.__todict__() if self.draw else None,
            "draw_discard": self.draw_discard.__todict__() if self.draw_discard else None,
            "faceup_draw": self.faceup_draw.__todict__() if self.faceup_draw else None,
            "move_pieces_to_path": self.move_pieces_to_path.__todict__() if self.move_pieces_to_path else None,
        }
    @staticmethod
    def __fromdict__(d):
        return PublicLegalAction(
            player_idx=d["player_idx"],
            name=d["name"],
            discard=LegalActionDiscard.__fromdict__(d["discard"]) if d.get("discard") else None,
            keep=LegalActionKeep.__fromdict__(d["keep"]) if d.get("keep") else None,
            draw=LegalActionDraw.__fromdict__(d["draw"]) if d.get("draw") else None,
            draw_discard=LegalActionDrawDiscard.__fromdict__(d["draw_discard"]) if d.get("draw_discard") else None,
            faceup_draw=LegalActionFaceupDraw.__fromdict__(d["faceup_draw"]) if d.get("faceup_draw") else None,
            move_pieces_to_path=LegalActionMovePiecesToPath.__fromdict__(d["move_pieces_to_path"]) if d.get("move_pieces_to_path") else None,
        )


class LegalAction(PClass):
    player_idx = field(type=int)
    name = field(type=str)
    title = field(type=(str, type(None)), initial=None)  # Optional[str]
    instruction = field(type=(str, type(None)), initial=None)  # Optional[str]
    allotted_seconds = field(type=int, initial=120)  # int
    allotted_since_action_idx = field(type=int, initial=-1)  # int
    btn_text = field(type=(str, type(None)), initial=None)  # Optional[str]
    discard = field(type=(LegalActionDiscard, type(None)), initial=None)  # LegalActionDiscard
    keep = field(type=(LegalActionKeep, type(None)), initial=None)  # LegalActionKeep
    draw = field(type=(LegalActionDraw, type(None)), initial=None)  # LegalActionDraw
    draw_discard = field(type=(LegalActionDrawDiscard, type(None)), initial=None)  # LegalActionDrawDiscard
    faceup_draw = field(type=(LegalActionFaceupDraw, type(None)), initial=None)  # LegalActionFaceupDraw
    move_pieces_to_path = field(type=(LegalActionMovePiecesToPath, type(None)), initial=None)  # LegalActionMovePiecesToPath
    def get_default_action(self, state, submitted_at):
        if self.keep:
            return ActionKeep.get_default_action(self, state, submitted_at)
        return None
    def get_public(self, state):
        return PublicLegalAction(
            player_idx=self.player_idx,
            name=self.name,
            discard=self.discard.get_public(state) if self.discard else None,
            keep=self.keep.get_public(state) if self.keep else None,
            draw=self.draw.get_public(state) if self.draw else None,
            draw_discard=self.draw_discard.get_public(state) if self.draw_discard else None,
            faceup_draw=self.faceup_draw.get_public(state) if self.faceup_draw else None,
            move_pieces_to_path=self.move_pieces_to_path.get_public(state) if self.move_pieces_to_path else None,
        )
    def __todict__(self):
        return {
            "player_idx": self.player_idx,
            "name": self.name,
            "title": self.title,
            "instruction": self.instruction,
            "allotted_seconds": self.allotted_seconds,
            "allotted_since_action_idx": self.allotted_since_action_idx,
            "btn_text": self.btn_text,
            "discard": self.discard.__todict__() if self.discard else None,
            "keep": self.keep.__todict__() if self.keep else None,
            "draw": self.draw.__todict__() if self.draw else None,
            "draw_discard": self.draw_discard.__todict__() if self.draw_discard else None,
            "faceup_draw": self.faceup_draw.__todict__() if self.faceup_draw else None,
            "move_pieces_to_path": self.move_pieces_to_path.__todict__() if self.move_pieces_to_path else None,
        }
    @staticmethod
    def __fromdict__(d):
        return LegalAction(
            player_idx=d["player_idx"],
            name=d["name"],
            title=d.get("title"),  # Handle None case
            instruction=d.get("instruction"),  # Handle None case
            allotted_seconds=d.get("allotted_seconds", 60),  # Handle None case
            allotted_since_action_idx=d.get("allotted_since_action_idx", -1),  # Handle None case
            btn_text=d.get("btn_text"),  # Handle None case
            discard=LegalActionDiscard.__fromdict__(d["discard"]) if d.get("discard") else None,
            keep=LegalActionKeep.__fromdict__(d["keep"]) if d.get("keep") else None,
            draw=LegalActionDraw.__fromdict__(d["draw"]) if d.get("draw") else None,
            draw_discard=LegalActionDrawDiscard.__fromdict__(d["draw_discard"]) if d.get("draw_discard") else None,
            faceup_draw=LegalActionFaceupDraw.__fromdict__(d["faceup_draw"]) if d.get("faceup_draw") else None,
            move_pieces_to_path=LegalActionMovePiecesToPath.__fromdict__(d["move_pieces_to_path"]) if d.get("move_pieces_to_path") else None,
        )


class PublicActionDiscard(PClass):
    deck_idxs = field(type=list)  # List[int]
    def __todict__(self):
        return {
            "deck_idxs": self.deck_idxs,
        }
    @staticmethod
    def __fromdict__(d):
        return PublicActionDiscard(
            deck_idxs=d["deck_idxs"]
        )


class ActionDiscard(PClass):
    card_uuids = field(type=list)  # List[int]
    def get_public(self, state):
        return PublicActionDiscard(
            deck_idxs=[state.carduuid2deckidx[card_uuid] for card_uuid in self.card_uuids]
        )
    def __todict__(self):
        return {
            "card_uuids": self.card_uuids,
        }
    @staticmethod
    def __fromdict__(d):
        return ActionDiscard(
            card_uuids=d["card_uuids"]
        )


class PublicActionKeep(PClass):
    deck_idxs = field(type=list)  # List[int]
    def __todict__(self):
        return {
            "deck_idxs": self.deck_idxs,
        }
    @staticmethod
    def __fromdict__(d):
        return PublicActionKeep(
            deck_idxs=d["deck_idxs"]
        )


class ActionKeep(PClass):
    card_uuids = field(type=list)  # List[int])
    def get_public(self, state):
        return PublicActionKeep(
            deck_idxs=[state.carduuid2deckidx[card_uuid] for card_uuid in self.card_uuids]
        )
    def __todict__(self):
        return {
            "card_uuids": self.card_uuids,
        }
    @staticmethod
    def __fromdict__(d):
        return ActionKeep(
            card_uuids=d["card_uuids"]
        )
    @staticmethod
    def get_default_action(legal_action, state, submitted_at):
        discard_tray = state.players[legal_action.player_idx].discard_tray
        deck_idx = legal_action.keep.deck_id
        card_uuids_matching_deck = [
            card_uuid for card_uuid in discard_tray 
            if state.carduuid2deckidx[card_uuid] == deck_idx
        ]
        actual_min = min(legal_action.keep.min, len(card_uuids_matching_deck))
        actual_max = min(legal_action.keep.max, len(card_uuids_matching_deck))
        rand_num_chosen = state.rng.randint(actual_min, actual_max)
        card_uuids = card_uuids_matching_deck[0:rand_num_chosen]
        return Action2(
            submitted_at=submitted_at,
            legal_action=legal_action,
            keep=ActionKeep(
                card_uuids=card_uuids
            )
        )


class PublicAction(PClass):
    submitted_at = field(type=str)
    player_idx = field(type=int)
    name = field(type=str)
    legal_action = field(type=PublicLegalAction)
    discard = field(type=(PublicActionDiscard, type(None)), initial=None)  # PublicActionDiscard
    keep = field(type=(PublicActionKeep, type(None)), initial=None)  # PublicActionKeep
    move_pieces_to_path = field(type=(PublicActionMovePiecesToPathOptional, type(None)), initial=None)  # PublicActionMovePiecesToPathOptional)
    def __todict__(self):
        return {
            "submitted_at": self.submitted_at,
            "player_idx": self.player_idx,
            "name": self.name,
            "legal_action": self.legal_action.__todict__(),
            "discard": self.discard.__todict__() if self.discard else None,
            "keep": self.keep.__todict__() if self.keep else None,
            "move_pieces_to_path": self.move_pieces_to_path.__todict__() if self.move_pieces_to_path else None,
        }
    @staticmethod
    def __fromdict__(d):
        return PublicAction(
            submitted_at=d["submitted_at"],
            player_idx=d["player_idx"],
            name=d["name"],
            legal_action=PublicLegalAction.__fromdict__(d["legal_action"]),
            discard=PublicActionDiscard.__fromdict__(d["discard"]) if d.get("discard") else None,
            keep=PublicActionKeep.__fromdict__(d["keep"]) if d.get("keep") else None,
            move_pieces_to_path=PublicActionMovePiecesToPathOptional.__fromdict__(d["move_pieces_to_path"]) if d.get("move_pieces_to_path") else None,
        )


class Action2(PClass):
    submitted_at = field(type=str)  # str
    legal_action = field(type=LegalAction) 
    discard = field(type=(ActionDiscard, type(None)), initial=None)  # ActionDiscard
    keep = field(type=(ActionKeep, type(None)), initial=None)  # ActionKeep
    move_pieces_to_path = field(type=(ActionMovePiecesToPathOptional, type(None)), initial=None)  # ActionMovePiecesToPath
    def get_public(self, state):
        return PublicAction(
            submitted_at=self.submitted_at,
            player_idx=self.legal_action.player_idx,
            name=self.legal_action.name,
            legal_action=self.legal_action.get_public(state),
            discard=self.discard.get_public(state) if self.discard else None,
            keep=self.keep.get_public(state) if self.keep else None,
            move_pieces_to_path=self.move_pieces_to_path.get_public(state) if self.move_pieces_to_path else None,
        )
    def __todict__(self):
        return {
            "submitted_at": self.submitted_at,
            "legal_action": self.legal_action.__todict__(),
            "discard": self.discard.__todict__() if self.discard else None,
            "keep": self.keep.__todict__() if self.keep else None,
            "move_pieces_to_path": self.move_pieces_to_path.__todict__() if self.move_pieces_to_path else None,
        }
    @staticmethod
    def __fromdict__(d):
        return Action2(
            submitted_at=d["submitted_at"],
            legal_action=LegalAction.__fromdict__(d["legal_action"]),
            discard=ActionDiscard.__fromdict__(d["discard"]) if d.get("discard") else None,
            keep=ActionKeep.__fromdict__(d["keep"]) if d.get("keep") else None,
            move_pieces_to_path=ActionMovePiecesToPathOptional.__fromdict__(d["move_pieces_to_path"]) if d.get("move_pieces_to_path") else None,
        )


class Deck(PClass):
    idx = field(type=int)
    uuid = field(type=str)
    units = field(type=list)  # List[Card]
    facedown_stack = field(type=list)  # List[str]
    discard = field(type=list)  # List[str]
    faceup_spots = field(type=list)  # List[str]
    def __todict__(self):
        return {
            "idx": self.idx,
            "uuid": self.uuid,
            "units": [unit.__todict__() for unit in self.units],
            "facedown_stack": self.facedown_stack,
            "discard": self.discard,
            "faceup_spots": self.faceup_spots,
        }
    @staticmethod
    def __fromdict__(d):
        return Deck(
            idx=d["idx"],
            uuid=d["uuid"],
            units=[], # TODO: Card.__fromdict__(card) for card in d["cards"]
            facedown_stack=d["facedown_stack"],
            discard=d["discard"],
            faceup_spots=d["faceup_spots"],
        )




class Card(PClass):
    idx = field(type=int)
    uuid = field(type=str)
    dek_card_uuid = field(type=str)
    is_wild = field(type=bool)
    deck_idx = field(type=int)
    resource_uuid = field(type=(str, type(None)), initial=None)
    goal_uuid = field(type=(str, type(None)), initial=None)
    def __todict__(self):
        return {
            "idx": self.idx,
            "uuid": self.uuid,
            "dek_card_uuid": self.dek_card_uuid,
            "is_wild": self.is_wild,
            "deck_idx": self.deck_idx,
            "resource_uuid": self.resource_uuid,
            "goal_uuid": self.goal_uuid,
        }
    @staticmethod
    def __fromdict__(d):
        return Card(
            idx=d["idx"],
            uuid=d["uuid"],
            dek_card_uuid=d["dek_card_uuid"],
            is_wild=d["is_wild"],
            deck_idx=d["deck_idx"],
            resource_uuid=d["resource_uuid"],
            goal_uuid=d["goal_uuid"],
        )


class PieceTemplate(PClass):
    uuid = field(type=str)
    name = field(type=str)
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "name": self.name,
        }
    @staticmethod
    def __fromdict__(d):
        return PieceTemplate(
            uuid=d["uuid"],
            name=d["name"]
        )


class Piece(PClass):
    uuid = field(type=str)
    pile_idx = field(type=int)
    player_idx = field(type=int)
    piece_template_idx = field(type=int)
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "pile_idx": self.pile_idx,
            "player_idx": self.player_idx,
            "piece_template_idx": self.piece_template_idx,
        }
    @staticmethod
    def __fromdict__(d):
        return Piece(
            uuid=d["uuid"],
            pile_idx=d["pile_idx"],
            player_idx=d["player_idx"],
            piece_template_idx=d["piece_template_idx"],
        )
    

class Pile(PClass):
    player_idx = field(type=(int, type(None)), initial=None)
    num_pieces = field(type=int, initial=0)
    pieces = field(type=list)  # List[Piece]
    def __todict__(self):
        return {
            "player_idx": self.player_idx,
            "num_pieces": self.num_pieces,
            "pieces": self.pieces,
        }
    @staticmethod
    def __fromdict__(d):
        return Pile(
            player_idx=d["player_idx"],
            num_pieces=d["num_pieces"],
            pieces=d["pieces"],
        )
    

class Segment2(PClass):
    uuid = field(type=str)
    pieces = field(type=list)  # List[Piece]
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "pieces": self.pieces,
        }
    @staticmethod
    def __fromdict__(d):
        return Segment2(
            uuid=d["uuid"],
            pieces=d["pieces"],
        )


class Path2(PClass):
    idx = field(type=int)
    segments = field(type=list)  # List[Segment]
    def __todict__(self):
        return {
            "idx": self.idx,
            "segments": [segment.__todict__() for segment in self.segments],
        }
    @staticmethod
    def __fromdict__(d):
        return Path2(
            idx=d["idx"],
            segments=[Segment2.__fromdict__(segment) for segment in d["segments"]],
        )


class BiEdge(PClass):
    uuid = field(type=str)
    start_point_uuid = field(type=str)
    end_point_uuid = field(type=str)
    node_1_uuid = field(type=str)
    node_2_uuid = field(type=str)
    node_1_idx = field(type=int)
    node_2_idx = field(type=int)
    paths = field(type=list)  # List[Path2]
    score = field(type=int)
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "start_point_uuid": self.start_point_uuid,
            "end_point_uuid": self.end_point_uuid,
            "node_1_uuid": self.node_1_uuid,
            "node_2_uuid": self.node_2_uuid,
            "node_1_idx": self.node_1_idx,
            "node_2_idx": self.node_2_idx,
            "paths": [path.__todict__() for path in self.paths],
            "score": self.score,
        }
    @staticmethod
    def __fromdict__(d):
        return BiEdge(
            uuid=d["uuid"],
            start_point_uuid=d["start_point_uuid"],
            end_point_uuid=d["end_point_uuid"],
            node_1_uuid=d["node_1_uuid"],
            node_2_uuid=d["node_2_uuid"],
            node_1_idx=d["node_1_idx"],
            node_2_idx=d["node_2_idx"],
            paths=[Path2.__fromdict__(path) for path in d["paths"]],
            score=d["score"],
        )


class Node(PClass):
    idx = field(type=int)
    uuid = field(type=str)
    name = field(type=str)
    pieces = field(type=list)  # List[Piece]
    def __todict__(self):
        return {
            "idx": self.idx,
            "uuid": self.uuid,
            "name": self.name,
            "pieces": self.pieces,
        }
    @staticmethod
    def __fromdict__(d):
        return Node(
            idx=d["idx"],
            uuid=d["uuid"],
            name=d["name"],
            pieces=d["pieces"],
        )
    

class Region(PClass):
    uuid = field(type=str)
    node_uuids = field(type=list)  # List[str]
    pieces = field(type=list)  # List[Piece]
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "node_uuids": self.node_uuids,
            "pieces": self.pieces,
        }
    @staticmethod
    def __fromdict__(d):
        return Region(
            uuid=d["uuid"],
            node_uuids=d["node_uuids"],
            pieces=d["pieces"],
        )


class BonusStatus(PClass):
    bonus_uuid = field(type=str)
    winners = field(type=list)
    def __todict__(self):
        return {
            "bonus_uuid": self.bonus_uuid,
            "winners": self.winners,
        }
    @staticmethod
    def __fromdict__(d):
        return BonusStatus(
            bonus_uuid=d["bonus_uuid"],
            winners=d["winners"],
        )


class State(PClass):
    pieceuuid2piece = field(type=dict)  # Dict[str, Piece]
    carduuid2card = field(type=dict)  # Dict[str, Card]
    final_scores = field(type=(list, type(None)), initial=None)  # Optional[List[int]]
    bonus_statuses = field(type=list)  # List[BonusStatus]
    bonusuuid2bonusidx = field(type=dict)  # Dict[str, int]
    carduuid2deckidx = field(type=dict)  # Dict[str, int]
    starting_decks = field(type=list)  # List[Deck]
    starting_piles = field(type=list)
    history = field(type=list)  # List[Action2]
    player_scores = field(type=list)  # List[PlayerScore2]
    player_graphs = field(type=list)  # List[PlayerGraph]
    goals = field(type=list)  # List[Goal]
    nodes = field(type=list)  # List[Node]
    nodeuuid2idx = field(type=dict)  # Dict[str, int]
    edges = field(type=list)  # List[BiEdge]
    edgeuuid2idx = field(type=dict)  # Dict[str, int]
    edgetuple2uuid = field(type=dict)  # Dict[Tuple[int, int], str]
    regions = field(type=list)  # List[Region]
    legal_actions_2 = field(type=list)  # List[LegalAction]
    piles = field(type=list)  # List[Pile]
    players = field(type=list)  # List[Player]
    player_idxs = field(type=list)  # List[int]
    decks = field(type=list)  # List[Deck]
    game_config = field(type=GameConfig)
    rng = field(type=random.Random)
    terminal = field(type=bool)
    initial_to_play = field(type=list)  # List[int]
    action_history = field(type=list)  # List[Action]
    route_cards = field(type=PVector)  # List[int]
    route_discards = field(type=PVector)  # List[int]
    player_hands = field(type=PVector)  # List[PlayerInfo]
    unit_cards = field(type=PVector)  # List[int]
    faceup_spots = field(type=PVector)  # List[Union{Nothing, int}]
    unit_discards = field(type=PVector)  # List[int]
    most_clusters_player_idxs = field(type=list)  # List[int]
    longest_road_player_idxs = field(type=list)  # List[int]
    last_to_play = field(type=(int, type(None)), initial=None)
    winners = field(type=list)  # List[int]
    # market_refills::Vector{MarketRefill}
    def __todict__(self):
        return {
            "pieceuuid2piece": {k: v.__todict__() for k, v in self.pieceuuid2piece.items()},
            "carduuid2card": {k: v.__todict__() for k, v in self.carduuid2card.items()},
            "final_scores": self.final_scores,
            "bonus_statuses": [status.__todict__() for status in self.bonus_statuses],
            "bonusuuid2bonusidx": self.bonusuuid2bonusidx,
            "carduuid2deckidx": self.carduuid2deckidx,
            "starting_decks": [deck.__todict__() for deck in self.starting_decks],
            "starting_piles": [pile.__todict__() for pile in self.starting_piles],
            "history": [x.__todict__() for x in self.history],
            "player_scores": [x.__todict__() for x in self.player_scores],
            "player_graphs": [x.__todict__() for x in self.player_graphs],
            "goals": [goal.__todict__() for goal in self.goals],
            "nodes": [node.__todict__() for node in self.nodes],
            "nodeuuid2idx": self.nodeuuid2idx,
            "edges": [edge.__todict__() for edge in self.edges],
            "edgeuuid2idx": self.edgeuuid2idx,
            "edgetuple2uuid": [{"k": list(k), "v": v} for k, v in self.edgetuple2uuid.items()],
            "regions": [region.__todict__() for region in self.regions],
            "legal_actions_2": [x.__todict__() for x in self.legal_actions_2],
            "piles": [pile.__todict__() for pile in self.piles],
            "players": [player.__todict__() for player in self.players],
            "player_idxs": self.player_idxs,
            "decks": [deck.__todict__() for deck in self.decks],
            "game_config": self.game_config.__todict__(),
            "rng": rng2json(self.rng),
            "terminal": self.terminal,
            "initial_to_play": self.initial_to_play,
            "action_history": [x.__todict__() for x in self.action_history],
            "route_cards": list(self.route_cards),
            "route_discards": list(self.route_discards),
            "player_hands": [x.__todict__() for x in self.player_hands],
            "unit_cards": list(self.unit_cards),
            "faceup_spots": list(self.faceup_spots),
            "unit_discards": list(self.unit_discards),
            "most_clusters_player_idxs": self.most_clusters_player_idxs,
            "longest_road_player_idxs": self.longest_road_player_idxs,
            "last_to_play": self.last_to_play,
            "winners": self.winners,
        }
    @staticmethod
    def __fromdict__(d):
        return State(
            pieceuuid2piece={k: Piece.__fromdict__(v) for k, v in d["pieceuuid2piece"].items()},
            carduuid2card={k: Card.__fromdict__(v) for k, v in d["carduuid2card"].items()},
            final_scores=d["final_scores"],
            bonus_statuses=[BonusStatus.__fromdict__(x) for x in d["bonus_statuses"]],
            bonusuuid2bonusidx=d["bonusuuid2bonusidx"],
            carduuid2deckidx=d["carduuid2deckidx"],
            starting_decks=[Deck.__fromdict__(x) for x in d["starting_decks"]],
            starting_piles=[Pile.__fromdict__(x) for x in d["starting_piles"]],
            history=[Action2.__fromdict__(x) for x in d["history"]],
            player_scores=[PlayerScore2.__fromdict__(x) for x in d["player_scores"]],
            player_graphs=[PlayerGraph.__fromdict__(x) for x in d["player_graphs"]],
            goals=[FrozenGoal.__fromdict__(goal) for goal in d["goals"]],
            nodes=[Node.__fromdict__(n) for n in d["nodes"]],
            nodeuuid2idx=d["nodeuuid2idx"],
            edges=[BiEdge.__fromdict__(e) for e in d["edges"]],
            edgeuuid2idx=d["edgeuuid2idx"],
            edgetuple2uuid={tuple(item["k"]): item["v"] for item in d["edgetuple2uuid"]},
            regions=[Region.__fromdict__(r) for r in d["regions"]],
            legal_actions_2=[LegalAction.__fromdict__(x) for x in d["legal_actions_2"]],
            piles=[Pile.__fromdict__(p) for p in d["piles"]],
            players=[Player.__fromdict__(p) for p in d["players"]],
            player_idxs=d["player_idxs"],
            decks=[Deck.__fromdict__(deck) for deck in d["decks"]],
            game_config=GameConfig.__fromdict__(d["game_config"]),
            rng=json2rng(d["rng"]),
            terminal=d["terminal"],
            initial_to_play=d["initial_to_play"],
            action_history=[AltAction.__fromdict__(a) for a in d["action_history"]],
            route_cards=pvector(d["route_cards"]),
            route_discards=pvector(d["route_discards"]),
            player_hands=pvector([PlayerInfo.__fromdict__(h) for h in d["player_hands"]]),
            unit_cards=pvector(d["unit_cards"]),
            faceup_spots=pvector(d["faceup_spots"]),
            unit_discards=pvector(d["unit_discards"]),
            most_clusters_player_idxs=d["most_clusters_player_idxs"],
            longest_road_player_idxs=d["longest_road_player_idxs"],
            last_to_play=d.get("last_to_play"),
            winners=d["winners"],
        )


# Implementing the following Julia function:
# getnumroutecards(f::Fig) = length(f.board_config.routes)
@dispatch(Fig)
def getnumroutecards(f):
    return len(f.board_config.routes) if f and f.board_config else 0


# Implementing the following Julia function:
# [x.quantity for x in f.board_config.deck_units] |> sum
@dispatch(Fig)
def gettotaldeckcards(f):
    return sum(x.quantity for x in f.board_config.deck_units) if f and f.board_config else 0
    

# Implementing the following Julia function:
# function shuffledeck(deck_size::Int, seed::Int)
#     shuffledeck(collect(1:deck_size), seed)
# end
@dispatch(int, object)
def shuffledeck(deck_size, rng):
    deck = list(range(1, deck_size + 1))
    return shuffledeck(deck, rng)


# Implementing the following Julia function:
# function shuffledeck(deck::Vector{Int}, seed::Int)
#     shuffle(MersenneTwister(seed), deck)
# end
@dispatch(list, object)
def shuffledeck(deck, rng):
    shuffled_deck = deck.copy()
    rng.shuffle(shuffled_deck)
    return shuffled_deck


class QValueLearningPolicy(PClass):
    qvalue_fn = field()
    epsilon = field(type=float, initial=0.1)  # Epsilon for exploration


class RandoPolicy:
   def __init__(self):
       pass


# Functions  


# Implementing the following GraphQL type:
# type PlayerScore {
# 	breakdown: [ScoreItem]!
# 	total: Int!
# }
class PlayerScore(PClass):
    breakdown = field(type=list)  # List[ScoreItem]
    total = field(type=int)
    def __todict__(self):
        return {
            "breakdown": [x.__todict__() for x in self.breakdown], 
            "total": self.total,
        }
    @staticmethod
    def __fromdict__(d):
        return PlayerScore(
            breakdown=[ScoreItem.__fromdict__(x) for x in d["breakdown"]],
            total=d["total"]
        )


class PublicPlayerScore(PClass):
    items = field(type=list)  # List[ScoreItem2]
    total = field(type=int)
    def __todict__(self):
        return {
            "items": [x.__todict__() for x in self.items], 
            "total": self.total,
        }
    @staticmethod
    def __fromdict__(d):
        return PublicPlayerScore(
            items=[ScoreItem2.__fromdict__(x) for x in d["items"]],
            total=d["total"]
        )


class ScoreItem2(PClass):
    amount = field(type=int)
    description = field(type=(str, type(None)), initial=None)
    def __todict__(self):
        return {
            "amount": self.amount,
            "description": self.description,
        }
    @staticmethod
    def __fromdict__(d):
        return ScoreItem2(
            amount=d["amount"],
            description=d.get("description")  # Handle None case
        )


class PlayerScore2(PClass):
    public_items = field(type=list)  # List[ScoreItem2]
    private_items = field(type=list)  # List[ScoreItem2]
    def __todict__(self):
        return {
            "public_items": [x.__todict__() for x in self.public_items], 
            "private_items": [x.__todict__() for x in self.private_items],
        }
    @staticmethod
    def __fromdict__(d):
        return PlayerScore2(
            public_items=[ScoreItem2.__fromdict__(x) for x in d["public_items"]],
            private_items=[ScoreItem2.__fromdict__(x) for x in d["private_items"]],
        )


# Implementing the following GraphQL type:
# type ScoreItem {
# 	amount: Int!
# 	code_idx: Int!
# 	json: String
# }
class ScoreItem(PClass):
    amount = field(type=int)
    code_idx = field(type=int)
    def __todict__(self):
        return {
            "amount": self.amount, 
            "code_idx": self.code_idx,
        }
    @staticmethod
    def __fromdict__(d):
        return ScoreItem(
            amount=d["amount"],
            code_idx=d["code_idx"]
        )


# Implementing the following GraphQL type:
# type PublicPlayerInfo {
# 	final_score: PlayerScore
# 	longest_road: [Int]!
# 	longest_road_len: Int!
# 	num_pieces: Int!
# 	num_route_cards: Int!
# 	num_unit_cards: Int!
# 	paths: [Int]!
# 	route_statuses: [RouteStatus]
# 	score: Int!
# }
class PublicPlayerInfo(PClass):
    final_score = field(type=(PlayerScore, type(None)), initial=None)  # Union{Nothing, PlayerScore}
    longest_road = field(type=list)  # List[int]
    longest_road_len = field(type=int)
    num_pieces = field(type=int)
    num_route_cards = field(type=int)
    num_new_route_cards = field(type=int)
    num_unit_cards = field(type=int)
    paths = field(type=list)  # List[int]
    points = field(type=list)  # List[UUID]
    tokens = field(type=list)  # List[UUID]
    route_statuses = field(type=list)  # List[RouteStatus]
    score = field(type=int)
    num_point_pieces = field(type=int, initial=0)  # Added to match PlayerInfo
    completed_clusters = field(type=list, initial=[])  # Added to match PlayerInfo
    def __todict__(self):
        return {
            "final_score": self.final_score.__todict__() if self.final_score else None,
            "longest_road": self.longest_road,
            "longest_road_len": self.longest_road_len,
            "num_pieces": self.num_pieces,
            "num_route_cards": self.num_route_cards,
            "num_new_route_cards": self.num_new_route_cards,
            "num_unit_cards": self.num_unit_cards,
            "paths": self.paths,
            "points": self.points,
            "tokens": self.tokens,
            "route_statuses": [x.__todict__() for x in self.route_statuses],
            "score": self.score,
            "num_point_pieces": self.num_point_pieces,
            "completed_clusters": self.completed_clusters,
        }
    @staticmethod
    def __fromdict__(d):
        return PublicPlayerInfo(
            final_score=PlayerScore.__fromdict__(d["final_score"]) if d.get("final_score") else None,
            longest_road=d["longest_road"],
            longest_road_len=d["longest_road_len"],
            num_pieces=d["num_pieces"],
            num_route_cards=d["num_route_cards"],
            num_new_route_cards=d["num_new_route_cards"],
            num_unit_cards=d["num_unit_cards"],
            paths=d["paths"],
            points=d["points"],
            tokens=d["tokens"],
            route_statuses=[RouteStatus.__fromdict__(x) for x in d["route_statuses"]],
            score=d["score"],
            num_point_pieces=d.get("num_point_pieces", 0),
            completed_clusters=d.get("completed_clusters", []),
        )


class AllottedTime(PClass):
    seconds = field(type=int)
    since_action_idx = field(type=int)
    def __todict__(self):
        return {
            "seconds": self.seconds,
            "since_action_idx": self.since_action_idx,
        }
    @staticmethod
    def __fromdict__(d):
        return AllottedTime(
            seconds=d["seconds"],
            since_action_idx=d["since_action_idx"],
        )


class PublicState(PClass):
    game_started_at = field(type=str)
    allotted_times = field(type=list)
    all_pieces = field(type=list)  # List[Piece]
    to_play_2 = field(type=list)  # List[int]
    bonus_statuses = field(type=list)  # List[BonusStatus]
    starting_decks = field(type=list)  # List[Deck]
    starting_piles = field(type=list)  # List[Pile]
    history = field(type=list)  # List[PublicAction]
    player_scores = field(type=list)  # List[PublicPlayerScore]
    player_graphs = field(type=list)  # List[PlayerGraph]
    goals = field(type=list)  # List[Goal]
    nodes = field(type=list)  # List[Node]
    edges = field(type=list)  # List[BiEdge]
    regions = field(type=list)
    decks = field(type=list)  # List[PublicDeck]
    piles = field(type=list)  # List[Pile]
    player_idxs = field(type=list)  # List[int]
    game_idx = field(type=int)
    initial_to_play = field(type=list)  # List[int]
    action_history = field(type=list) # List[AltAction]
    to_play = field(type=list)  # List[int]
    unit_discards = field(type=list)  # List[int]
    num_route_cards = field(type=int)
    num_route_discards = field(type=int)
    num_unit_cards = field(type=int)
    num_unit_discards = field(type=int)
    faceup_spots = field(type=list)  # List[Union{Nothing, int}]
    most_clusters_player_idxs = field(type=list)
    players = field(type=list)  # List[PublicPlayer]
    player_hands = field(type=list)  # List[PublicPlayerInfo]
    last_to_play = field(type=(int, type(None)), initial=None)
    longest_road_player_idxs = field(type=list)
    winners = field(type=list)
    terminal = field(type=bool)
    captured_points = field(type=list)  # List[CapturedPoint]
    captured_segments = field(type=list)  # List[CapturedSegment]
    def __todict__(self):
        return {
            "game_started_at": self.game_started_at,
            "allotted_times": [allotted_time.__todict__() if allotted_time else None for allotted_time in self.allotted_times], # List[AllottedTime|None]
            "all_pieces": [piece.__todict__() for piece in self.all_pieces],
            "to_play_2": self.to_play_2,
            "bonus_statuses": [bs.__todict__() for bs in self.bonus_statuses],
            "starting_decks": [deck.__todict__() for deck in self.starting_decks],
            "starting_piles": [pile.__todict__() for pile in self.starting_piles],
            "history": [x.__todict__() for x in self.history],
            "player_scores": [x.__todict__() for x in self.player_scores],
            "player_graphs": [x.__todict__() for x in self.player_graphs],
            "goals": [goal.__todict__() for goal in self.goals],
            "nodes": [node.__todict__() for node in self.nodes],
            "edges": [edge.__todict__() for edge in self.edges],
            "regions": [region.__todict__() for region in self.regions],
            "decks": [deck.__todict__() for deck in self.decks],
            "piles": [pile.__todict__() for pile in self.piles],
            "player_idxs": self.player_idxs,
            "game_idx": self.game_idx,
            "initial_to_play": self.initial_to_play,
            "action_history": [x.__todict__() for x in self.action_history],
            "to_play": self.to_play,
            "unit_discards": self.unit_discards,
            "num_route_cards": self.num_route_cards,
            "num_route_discards": self.num_route_discards,
            "num_unit_cards": self.num_unit_cards,
            "num_unit_discards": self.num_unit_discards,
            "faceup_spots": self.faceup_spots,
            "most_clusters_player_idxs": self.most_clusters_player_idxs,
            "players": [x.__todict__() for x in self.players],
            "player_hands": [x.__todict__() for x in self.player_hands],
            "last_to_play": self.last_to_play,
            "longest_road_player_idxs": self.longest_road_player_idxs,
            "winners": self.winners,
            "terminal": self.terminal,
            "captured_points": [x.__todict__() for x in self.captured_points],
            "captured_segments": [x.__todict__() for x in self.captured_segments],
        }
    @staticmethod
    def __fromdict__(d):
        return PublicState(
            game_started_at=d["game_started_at"],
            allotted_times=[AllottedTime.__fromdict__(x) if x else None for x in d["allotted_times"]], # List[AllottedTime|None]
            all_pieces=[Piece.__fromdict__(x) for x in d["all_pieces"]],
            to_play_2=d["to_play_2"],
            bonus_statuses=[BonusStatus.__fromdict__(x) for x in d["bonus_statuses"]],
            starting_decks=[Deck.__fromdict__(x) for x in d["starting_decks"]],
            starting_piles=[Pile.__fromdict__(x) for x in d["starting_piles"]],
            history=[PublicAction.__fromdict__(x) for x in d["history"]],
            player_scores=[PublicPlayerScore.__fromdict__(x) for x in d["player_scores"]],
            player_graphs=[PlayerGraph.__fromdict__(x) for x in d["player_graphs"]],
            goals=[FrozenGoal.__fromdict__(goal) for goal in d["goals"]],
            nodes=[Node.__fromdict__(n) for n in d["nodes"]],
            edges=[BiEdge.__fromdict__(e) for e in d["edges"]],
            regions=[Region.__fromdict__(r) for r in d["regions"]],
            decks=[PublicDeck.__fromdict__(deck) for deck in d["decks"]],
            piles=[Pile.__fromdict__(x) for x in d["piles"]],
            player_idxs=d["player_idxs"],
            game_idx=d["game_idx"],
            initial_to_play=d["initial_to_play"],
            action_history=[AltAction.__fromdict__(x) for x in d["action_history"]],
            to_play=d["to_play"],
            unit_discards=d["unit_discards"],
            num_route_cards=d["num_route_cards"],
            num_route_discards=d["num_route_discards"],
            num_unit_cards=d["num_unit_cards"],
            num_unit_discards=d["num_unit_discards"],
            faceup_spots=d["faceup_spots"],
            most_clusters_player_idxs=d["most_clusters_player_idxs"],
            players=[PublicPlayer.__fromdict__(x) for x in d["players"]],
            player_hands=[PublicPlayerInfo.__fromdict__(x) for x in d["player_hands"]],
            last_to_play=d.get("last_to_play"),
            longest_road_player_idxs=d["longest_road_player_idxs"],
            winners=d["winners"],
            terminal=d["terminal"],
            captured_points=[CapturedPoint.__fromdict__(x) for x in d["captured_points"]],
            captured_segments=[CapturedSegment.__fromdict__(x) for x in d["captured_segments"]],
        )
    # fig::Fig
    # captured_segments::Vector{CapturedSegment}
    # captured_points::Vector{CapturedPoint}
    # market_refills::Vector{MarketRefill}


class PlayerState(PClass):
    public = field(type=PublicState)
    private = field(type=PrivateState)
    def __todict__(self):
        return {
            "public": self.public.__todict__(),
            "private": self.private.__todict__()
        }
    @staticmethod
    def __fromdict__(d):
        return PlayerState(
            public=PublicState.__fromdict__(d["public"]),
            private=PrivateState.__fromdict__(d["private"])
        )


def autoplay(seed, fig, num_players, policy, log=False):
    game_config = initgameconfig(str(uuid4()), "2025-01-01 00:00:00", fig, num_players, seed)
    s = getinitialstate(game_config)
    actions = []
    try:

        while not s.terminal:
            if log:
                printstate(s)
            a = getnextaction(s, policy)
            if log:
                printaction(a, getstateidx(s))
            s = getnextstate(s, a)
            actions.append(a)
        
        if (log):
            printstate(s)
        
    except Exception as e:
        logging.error(f"Something went wrong: {str(e)}", exc_info=True)
    finally:
        return (game_config, actions, s)


def get_regions(board_config):
    return [] # TODO: None for now (need to modify BoardConfig to include regions)


def get_nodes(board_config):
    if board_config and board_config.points:
        return [
            Node(idx=idx, uuid=node.uuid, name=f"{idx}", pieces=[]) 
            for idx, node in enumerate(board_config.points)
        ]
    return []


def get_edges(board_config, nodeuuid2idx):
    edges = []
    

    for link_idx, link in enumerate(board_config.links):
        node_1_idx=nodeuuid2idx[link.c1]
        node_2_idx=nodeuuid2idx[link.c2]
        matching_board_paths = [p for p in board_config.board_paths if p.link_num == link.num]

        paths = []
        for matching_board_path in matching_board_paths:
            path_idx = matching_board_path.num - 1
            segments = [
                Segment2(uuid=s.uuid, pieces=[]) for s in matching_board_path.path.segments
            ]
            path = Path2(idx=path_idx, segments=segments)
            paths.append(path)
        
        if len(paths) == 0:
            print(f"len(board_config.board_paths) = {len(board_config.board_paths)}")
            print("len(board_config.links) =", len(board_config.links))
            raise ValueError(f"No paths found for link {link.uuid} with nodes {link.c1} and {link.c2} and link number {link.num}")

        edges.append(
            BiEdge(
                uuid=link.uuid, 
                start_point_uuid=link.c1, 
                end_point_uuid=link.c2,
                node_1_uuid=link.c1, 
                node_2_uuid=link.c2, 
                node_1_idx=node_1_idx, 
                node_2_idx=node_2_idx, 
                paths=paths, 
                score=link.score
            )
        )

    return edges


def generate_pieces(piece_template, player_idx):
    piece_template_rng = getrng(piece_template.seed + player_idx)
    return [
        Piece(
            uuid=str(generate_uuid_with_rng(piece_template_rng)),
            piece_template_idx=piece_template.idx,
            pile_idx=player_idx,
            player_idx=player_idx
        ) for _ in range(piece_template.quantity)
    ]


def generate_cards(dek):
    cards = []
    idx = 0
    rng = getrng(dek.seed)
    for dek_card in dek.dek_cards:
        for _ in range(dek_card.quantity):
            card = Card(
                idx=idx,
                dek_card_uuid=dek_card.uuid,
                uuid=str(generate_uuid_with_rng(rng)),
                deck_idx=dek.idx,
                is_wild=dek_card.is_wild,
                resource_uuid=dek_card.resource_uuid,
                goal_uuid=dek_card.goal_uuid,
            )
            cards.append(card)
            idx += 1

    return cards


@dispatch(GameConfig)
def getinitialstate(game_config):
    fig = game_config.fig
    rng = getrng(game_config.seed)
    route_deck = shuffledeck(getnumroutecards(fig), rng)
    unit_deck = shuffledeck(gettotaldeckcards(fig), rng)
    route_deck_idx, unit_deck_idx = 0, 0
    player_hands = []
    initial_num_route_choices = getsettingvalue(fig, "initial_num_route_choices")
    num_initial_unit_cards = getsettingvalue(fig, "num_initial_unit_cards")
    num_segment_pieces_per_player = getsettingvalue(fig, "num_segment_pieces_per_player")
    num_point_pieces_per_player = getsettingvalue(fig, "num_point_pieces_per_player")


    for player_idx in range(game_config.num_players):
        player_hand = PlayerInfo(
            fig=fig,
            player_idx=player_idx,
            new_route_cards=pvector(route_deck[route_deck_idx:(route_deck_idx+(initial_num_route_choices))]),
            route_cards=pvector([]),
            unit_cards=pvector(unit_deck[unit_deck_idx:(unit_deck_idx + num_initial_unit_cards)]),
            completed_routes=[],
            completed_clusters=[],
            paths=[],
            points=[],
            tokens=[],
            num_pieces=num_segment_pieces_per_player,
            num_point_pieces=num_point_pieces_per_player,
            longest_road=[],
            longest_road_len=0,
            final_score=None,
        )
        player_hands.append(player_hand)
        route_deck_idx += initial_num_route_choices
        unit_deck_idx += num_initial_unit_cards

    faceup_spots = getfaceupspots(fig, unit_deck, unit_deck_idx)
    unit_deck_idx += 5
    # Implementing the following Julia function:
    # unit_cards = unit_deck[unit_deck_idx:end]
    unit_cards = unit_deck[unit_deck_idx:] if unit_deck_idx < len(unit_deck) else []
    route_cards = route_deck[route_deck_idx:]

    if getsettingvalue(fig, 'action_route_discard'):
        initial_to_play = list(range(game_config.num_players))
    else:
        initial_to_play = [getfirstplayeridx(rng, game_config.num_players)]

    board_config = fig.board_config
    deck_0_rng = getrng(1234321)
    deck_1_rng = getrng(8738758)
    nodes = get_nodes(board_config)

    pieceuuid2piece = {}
    piles = []
    for piece_template in board_config.piece_templates:
        if piece_template.has_player:
            for player_idx in range(game_config.num_players):
                pieces = generate_pieces(piece_template, player_idx)
                for piece in pieces:
                    pieceuuid2piece[piece.uuid] = piece
                pile = Pile(
                    player_idx=player_idx,
                    num_pieces=piece_template.quantity,
                    pieces=[piece.uuid for piece in pieces],
                )
                piles.append(pile)

    carduuid2card = {}
    carduuid2deckidx = {}
    decks = []
    for dek in board_config.deks:
        cards = generate_cards(dek)
        for card in cards:
            carduuid2card[card.uuid] = card
            carduuid2deckidx[card.uuid] = dek.idx
        deck_obj = Deck(
            uuid=dek.uuid,
            idx=dek.idx,
            units=[],
            faceup_spots=[],
            discard=[],
            facedown_stack=[card.uuid for card in cards],
        )
        decks.append(deck_obj)

    nodeuuid2idx = {node.uuid: idx for idx, node in enumerate(board_config.points)}
    edges = get_edges(board_config, nodeuuid2idx)
    edgeuuid2idx = {edge.uuid: idx for idx, edge in enumerate(edges)}
    edgetuple2uuid = {}
    for edge in edges:
        node_1_idx = nodeuuid2idx[edge.node_1_uuid]
        node_2_idx = nodeuuid2idx[edge.node_2_uuid]
        edge_tuple = (min(node_1_idx, node_2_idx), max(node_1_idx, node_2_idx))
        edgetuple2uuid[edge_tuple] = edge.uuid

    bonuses = game_config.fig.board_config.bonuses
    bonusuuid2bonusidx = {bonus.uuid: idx for idx, bonus in enumerate(bonuses)}
    bonus_statuses = [BonusStatus(bonus_uuid=bonus.uuid, winners=[]) for bonus in bonuses]

    state = State(
        pieceuuid2piece=pieceuuid2piece,
        carduuid2card=carduuid2card,
        final_scores=None,
        bonus_statuses=bonus_statuses,
        bonusuuid2bonusidx=bonusuuid2bonusidx,
        carduuid2deckidx=carduuid2deckidx,
        starting_decks=[
            Deck.__fromdict__(x.__todict__()) for x in decks
        ],
        starting_piles=[
            Pile.__fromdict__(x.__todict__()) for x in piles
        ],
        history=[],
        player_scores=[PlayerScore2(public_items=[], private_items=[]) for _ in range(game_config.num_players)],
        player_graphs=[
            PlayerGraph(
                player_idx=player_idx, 
                neighbors=[[] for _ in range(len(nodes))]
            ) for player_idx in range(game_config.num_players)
        ],
        goals = board_config.goals,
        nodes = nodes,
        nodeuuid2idx = nodeuuid2idx,
        edges = edges,
        edgeuuid2idx = edgeuuid2idx,
        edgetuple2uuid = edgetuple2uuid,
        regions = get_regions(board_config),
        legal_actions_2=[],
        piles=piles,
        players=[Player(idx=idx, pieces=[], cards=[], discard_tray=[]) for idx in range(game_config.num_players)],
        player_idxs=list(range(game_config.num_players)),
        decks=decks,
        game_config=game_config,
        initial_to_play=initial_to_play,
        rng=rng,
        action_history=[],
        route_cards=pvector(route_cards),
        route_discards=pvector([]),
        player_hands=pvector(player_hands),
        unit_cards=pvector(unit_cards),
        unit_discards=pvector([]),
        faceup_spots=pvector(faceup_spots),
        most_clusters_player_idxs=[],
        longest_road_player_idxs=[],
        last_to_play=None,
        winners=[],
        terminal=False,
    )

    state = run_state_hooks(state, INITIALIZATION_HOOKS, True)
    return state


def run_state_hooks(state, hooks, log=False):
    return reduce(
        lambda s, h: run_state_hook(s, h, log), 
        hooks, 
        state
    )


def run_accept_action_hooks(state, action, hooks, log=False):
    # Just like "run_state_action_hooks", but returns immediately returns True if any hook returns True, otherwise returns False
    for hook in hooks:
        if run_state_action_hook(state, action, hook, log):
            return True
    return False


def run_state_action_hooks(state, action, hooks, log=False):
    return reduce(
        lambda s, h: run_state_action_hook(s, action, h, log), 
        hooks, 
        state
    )


def score_public_items(game, player_idx):
    items = []
    for edge in game.edges:
        for path in edge.paths:
            if len(path.segments) > 0:
                first_segment = path.segments[0]
                if first_segment.pieces and len(first_segment.pieces) > 0:
                    first_piece = game.pieceuuid2piece[first_segment.pieces[0]]
                    if first_piece.player_idx == player_idx:
                        items.append(
                            ScoreItem2(amount=edge.score, description="Player {} owns edge {}".format(player_idx, edge.uuid))
                        )
    for bonus_status in game.bonus_statuses:
        bonus_idx = game.bonusuuid2bonusidx.get(bonus_status.bonus_uuid)
        bonus = game.game_config.fig.board_config.bonuses[bonus_idx] if bonus_idx is not None else None
        if bonus:
            if player_idx in bonus_status.winners:
                items.append(
                    ScoreItem2(amount=bonus.score, description="Player {} wins bonus {}".format(player_idx, bonus.code))
                )
    return items


def score_private_items(game, player_idx):
    items = []
    goaluuid2goal = {goal.uuid: goal for goal in game.goals}
    goal_completions = get_goal_completions(game, player_idx)
    complete_goal_uuids = [gc.goal_uuid for gc in goal_completions if gc.complete]
    incomplete_goal_uuids = [gc.goal_uuid for gc in goal_completions if not gc.complete]
    for complete_goal_uuid in complete_goal_uuids:
        goal = goaluuid2goal[complete_goal_uuid]
        items.append(
            ScoreItem2(amount=goal.score, description="Player {} completed goal {}".format(player_idx, complete_goal_uuid))
        )
    for incomplete_goal_uuid in incomplete_goal_uuids:
        goal = goaluuid2goal[incomplete_goal_uuid]
        items.append(
            ScoreItem2(amount=(-1*goal.score), description="Player {} incomplete goal {}".format(player_idx, incomplete_goal_uuid))
        )
    return items


def handle_last_to_play(game):
    if game.last_to_play is None:
        # If any player can less than 3 pieces, the game is terminal
        for player in game.players:
            if len(player.pieces) < 3:
                return game.set(last_to_play=player.idx)
    elif game.last_to_play == game.history[-1].legal_action.player_idx:
        if not game.legal_actions_2:
            return game.set(terminal=True)
    return game


def handle_calc_winners(game):
    if game.terminal:
        players_with_highest_score = []
        highest_score = -1000
        final_scores = []
        for player_idx in range(len(game.players)):
            player_score = game.player_scores[player_idx]
            final_score = getpublicplayerscore(game, player_score).total
            final_scores.append(final_score)
            if final_score > highest_score:
                highest_score = final_score
                players_with_highest_score = [player_idx]
            elif final_score == highest_score:
                players_with_highest_score.append(player_idx)
        return game.set(
            winners=players_with_highest_score,
            final_scores=final_scores,
        )

    return game


def default_handle_terminal(game):
    game = handle_last_to_play(game)
    game = handle_calc_winners(game)
    return game


def calc_bonus_status(game, bonus):
    if not bonus:
        return None
    if bonus.code == "longest-road":
        return get_bonus_status_longest_road(game, bonus)
    return None


def get_bonus_status_longest_road(game, bonus):
    longest_road = 0
    winners = []

    for player_idx in range(game.game_config.num_players):
        road_length = get_longest_path_length(game, player_idx)
        if road_length > longest_road:
            longest_road = road_length
            winners = [player_idx]
        elif road_length == longest_road and road_length > 0:
            winners.append(player_idx)

    return BonusStatus(
        bonus_uuid=bonus.uuid,
        winners=winners,
    )


def handle_bonus_statuses(game):
    bonus_statuses = [
        calc_bonus_status(game, bonus)
        for bonus in game.game_config.fig.board_config.bonuses
    ]
    # Remove all None bonus statuses
    bonus_statuses = [bs for bs in bonus_statuses if bs is not None]
    return game.set(bonus_statuses=bonus_statuses)


def default_handle_scoring(game):
    game = handle_bonus_statuses(game)
    player_scores = [
        PlayerScore2(
            public_items=score_public_items(game, player_idx), 
            private_items=score_private_items(game, player_idx),
        ) for player_idx in range(len(game.players))
    ]
    return game.set(player_scores=player_scores)


def default_handle_action(game, action):
    if action.legal_action.discard:
        return handle_discard_action(game, action)
    if action.legal_action.keep:
        return handle_keep_action(game, action)
    if action.legal_action.move_pieces_to_path:
        game = handle_move_pieces_to_path_action(game, action)
        return handle_after_move_pieces_to_path_action(game, action)
    if action.legal_action.faceup_draw:
        return handle_faceup_draw_action(game, action)
    if action.legal_action.draw:
        return handle_draw_action(game, action)
    if action.legal_action.draw_discard:
        return handle_draw_discard_action(game, action)

    return game


def default_after_accept_action(game, action):
    # Remove all actions for matching player of action
    if not game or not action or not action.legal_action:
        return game
    player_idx = action.legal_action.player_idx
    if player_idx < 0 or player_idx >= len(game.players):
        return game
    new_legal_actions = [
        la for la in game.legal_actions_2 if la.player_idx != player_idx
    ]
    history = game.history + [action]
    return game.set(
        legal_actions_2=new_legal_actions, 
        history=history,
    )


def get_path_by_idx(game, path_idx):
    if not game or path_idx < 0 or path_idx >= len(game.game_config.fig.board_config.board_paths):
        return None
    
    for edge in game.edges:
        if len(edge.paths) == 0:
            raise ValueError(f"Edge {edge.uuid} has no paths")
        for path in edge.paths:
            if path.idx == path_idx:
                return path
    
    return None


def handle_draw_action(game, action):
    if not game or not action or not action.legal_action or not action.legal_action.draw:
        return game
    legal_action = action.legal_action
    draw = legal_action.draw
    player = game.players[legal_action.player_idx]
    deck = game.decks[draw.deck_idx]
    
    if len(deck.facedown_stack) == 0:
        return game  # No cards to draw

    for _ in range(draw.quantity):
        drawn_card = deck.facedown_stack.pop()
        player.cards.append(drawn_card)
        if len(deck.facedown_stack) == 0:
            shuffled_discards = list(deck.discard)
            game.rng.shuffle(shuffled_discards)
            deck = deck.set(
                facedown_stack = shuffled_discards,
                discard = []
            )
            game = set_deck(game, deck.idx, deck)

    game = game.set(
        players=game.players,
    )

    # TODO: extract this out to user-defined function/hook
    game = append_follow_up_draw_legal_actions(game, action)

    return game


def handle_draw_discard_action(game, action):
    if not game or not action or not action.legal_action or not action.legal_action.draw_discard:
        return game
    legal_action = action.legal_action
    draw_discard = legal_action.draw_discard
    player = game.players[legal_action.player_idx]
    deck = game.decks[draw_discard.deck_idx]
    
    if len(deck.facedown_stack) == 0:
        return game  # No cards to draw

    for _ in range(draw_discard.quantity):
        drawn_card = deck.facedown_stack.pop()
        player.discard_tray.append(drawn_card)
    
    game = append_to_legal_actions(
        game,
        LegalAction(
            player_idx=player.idx,
            name="GOAL-KEEP",
            instruction="Your move. Please select the routes you want to keep.",
            allotted_seconds=120,
            allotted_since_action_idx=(len(game.history) - 1),
            keep=LegalActionKeep(
                deck_idx=draw_discard.deck_idx,
                min=draw_discard.min,
                max=draw_discard.max,
            )
        )
    )

    return game.set(
        players=game.players,
        decks=game.decks,
    )


def append_follow_up_draw_legal_actions(game, action):
    legal_action = action.legal_action
    if len(game.history) >= 2:
        last_action = game.history[-2]
        if (last_action.legal_action.player_idx != legal_action.player_idx) or last_action.legal_action.name == "INITIAL-GOAL-KEEP":
            game = append_to_legal_actions(
                game,
                LegalAction(
                    player_idx=legal_action.player_idx,
                    name="DRAW",
                    instruction="draw a unit",
                    allotted_seconds=60,
                    allotted_since_action_idx=(len(game.history) - 1),
                    draw=LegalActionDraw(
                        deck_idx=0,
                        quantity=1,
                    )
                )
            )
            for card_uuid in game.decks[0].faceup_spots:
                if not game.carduuid2card[card_uuid].is_wild:
                    game = append_to_legal_actions(
                        game,
                        LegalAction(
                            player_idx=legal_action.player_idx,
                            name="FACEUP-DRAW",
                            instruction="draw a faceup unit",
                            allotted_seconds=60,
                            allotted_since_action_idx=(len(game.history) - 1),
                            faceup_draw=LegalActionFaceupDraw(
                                deck_idx=0,
                                card_uuid=card_uuid,
                            )
                        )
                    )
    return game


def get_num_faceup_wilds(game, deck_idx):
    deck = game.decks[deck_idx]
    non_empty_spots = [spot for spot in deck.faceup_spots if spot]
    if not non_empty_spots:
        return 0
    return sum(1 for card_uuid in non_empty_spots if game.carduuid2card[card_uuid].is_wild)


def ensure_faceup_spots_valid(game):
    for deck in game.decks:
        max_iters = 5
        i = 0
        while i < max_iters and get_num_faceup_wilds(game, deck.idx) >= 3:
            game = discardfaceup_shuffle_flip(game, deck.idx)
            i += 1
    return game


def discardfaceup_shuffle_flip(game, deck_idx):
    deck = game.decks[deck_idx]
    num_faceup_spots = len(deck.faceup_spots)
    for faceup_spot in deck.faceup_spots:
        if faceup_spot:
            deck.discard.append(faceup_spot)
    deck = deck.set(faceup_spots=[])
    while len(deck.discard) > 0:
        card = deck.discard.pop()
        deck.facedown_stack.append(card)
    deck = shuffle(game.rng, deck)
    game = set_deck(game, deck.idx, deck)
    game = flip_cards(game, deck.idx, num_faceup_spots)
    return game


def handle_faceup_draw_action(game, action):
    if not game or not action or not action.legal_action or not action.legal_action.faceup_draw:
        return game
    legal_action = action.legal_action
    faceup_draw = legal_action.faceup_draw
    player = game.players[legal_action.player_idx]
    deck = game.decks[faceup_draw.deck_idx]
    # find the faceup spot idx with uuid "faceup_draw.card_uuid"
    spot_idx = next((i for i, card_uuid in enumerate(deck.faceup_spots) if card_uuid == faceup_draw.card_uuid), None)
    drawn_card = deck.faceup_spots[spot_idx] if spot_idx is not None else None
    player.cards.append(drawn_card)
    if len(deck.facedown_stack) > 0 and spot_idx is not None:
        deck.faceup_spots[spot_idx] = deck.facedown_stack.pop()

    game = ensure_faceup_spots_valid(game)

    # Prevent an extra draw if last draw was a face-wild-draw
    if not game.carduuid2card[drawn_card].is_wild:
        # TODO: extract this out to user-defined function/hook
        game = append_follow_up_draw_legal_actions(game, action)

    return game.set(
        players=game.players,
        decks=game.decks,
    )


def handle_after_move_pieces_to_path_action(game, action):
    game = handle_move_bonus_cards(game, action)
    return game


def handle_move_bonus_cards(game, action):
    return handle_move_longest_path_card(game, action)


# Take a random walk on the player's graph. A node can be visiting more than once, but an edge cannot be visited more than once.
# Example graph: PlayerGraph(player_idx=0, neighbors=[[], [], [], [], [], [], [], [], [], [], [30]
def random_player_graph_walk(game, player_idx):
    player_graph = game.player_graphs[player_idx]
    nodes_indices_with_neighbors = [i for i, neighbors in enumerate(player_graph.neighbors) if neighbors]
    
    if not nodes_indices_with_neighbors:
        return None
    
    rng = random.Random()
    random_start_node_idx = rng.choice(nodes_indices_with_neighbors)

    def choose_next_node(visited_nodes, visited_edges):
        current_node_idx = visited_nodes[-1]
        neighbors = player_graph.neighbors[current_node_idx]
        if not neighbors:
            return None
        
        shuffled_neighbors = neighbors.copy()
        rng.shuffle(shuffled_neighbors)
        
        for neighbor in shuffled_neighbors:
            edge = (min(current_node_idx, neighbor), max(current_node_idx, neighbor))
            if edge not in visited_edges:
                return neighbor
        
        return None

    def walk(visited_nodes, visited_edges):
        next_node = choose_next_node(visited_nodes, visited_edges)
        if next_node is None:
            return (visited_nodes, visited_edges)
        next_edge = (min(visited_nodes[-1], next_node), max(visited_nodes[-1], next_node))
        return walk(
            visited_nodes + [next_node], 
            set(list(visited_edges) + [next_edge])
        )

    return walk([random_start_node_idx], set([]))


def find_player_with_longest_path(game):
    longest_path_player_idx = None
    longest_path_length = 0

    for player_idx in range(game.game_config.num_players):
        path_length = get_longest_path_length(game, player_idx)
        if path_length > longest_path_length:
            longest_path_length = path_length
            longest_path_player_idx = player_idx

    if longest_path_player_idx is None:
        return None
    
    return game.players[longest_path_player_idx]


def calc_path_len_from_edges(game, edge_tuples):
    if edge_tuples is None:
        return 0
    edge_lens = []
    for edge_tuple in edge_tuples:
        edge_uuid = game.edgetuple2uuid.get(edge_tuple)
        edge_idx = game.edgeuuid2idx.get(edge_uuid)
        if edge_idx is not None:
            edge = game.edges[edge_idx]
            if edge and edge.paths:
                first_path = edge.paths[0]
                edge_len = len(first_path.segments)
                edge_lens.append(edge_len)

    return sum(edge_lens)


def get_longest_path_length(game, player_idx):
    longest_path_length = 0
    num_iters_since_change = 0

    for _ in range(1000):
        walk = random_player_graph_walk(game, player_idx)
        if not walk:
            return 0
        path_len = calc_path_len_from_edges(game, walk[1])
        if path_len > longest_path_length:
            longest_path_length = path_len
            num_iters_since_change = 0
        else:
            num_iters_since_change += 1
        # If we haven't found a longer path in 500 iterations, return
        if num_iters_since_change > 500:
            return longest_path_length

    print("longest_path_length: ", longest_path_length)
    return longest_path_length


def handle_move_longest_path_card(game, action):
    player = find_player_with_longest_path(game)

    if not game or not player:
        return game

    longest_path_card = None

    if len(game.decks) > 2:
        longest_path_deck = game.decks[2]
        if longest_path_deck.facedown_stack:
            # Move the longest path card to the player's hand
            longest_path_card = longest_path_deck.facedown_stack.pop()
        else:
            # Search for the longest path card in each player's cards
            player_with_card = find_player_with_longest_path_card(game)
            if player_with_card:
                # Find the index of the card from the player's cards, then pop it
                card_idx = next((i for i, card_uuid in enumerate(player_with_card.cards) if game.carduuid2card[card_uuid].deck_idx == 2), None)
                if card_idx is not None:
                    longest_path_card = player_with_card.cards.pop(card_idx)


    if longest_path_card:
        player.cards.append(longest_path_card)

    return game.set(
        players=game.players,
        decks=game.decks,
    )


def find_player_with_longest_path_card(game):
    for player in game.players:
        if any(game.carduuid2card[card_uuid].deck_idx == 2 for card_uuid in player.cards):
            return player
    return None


def handle_move_pieces_to_path_action(game, action):
    if not game or not action or not action.legal_action or not action.legal_action.move_pieces_to_path:
        return game
    
    legal_action = action.legal_action
    move_pieces_to_path = legal_action.move_pieces_to_path
    default = move_pieces_to_path.default
    override = action.move_pieces_to_path
    if override:
        default = default.set(piece_uuids=override.piece_uuids)
        default = default.set(card_uuids=override.card_uuids)

    player = game.players[legal_action.player_idx]
    if not player or not player.pieces:
        return game

    path_idx = move_pieces_to_path.path_idx
    path = get_path_by_idx(game, path_idx)

    if path is None or not path.segments:
        return game

    for piece_uuid, segment in zip(default.piece_uuids, path.segments):
        # Find the piece in the player's pieces
        piece_idx = next((i for i, player_piece_uuid in enumerate(player.pieces) if player_piece_uuid == piece_uuid), None)
        if piece_idx is not None:
            # Remove the piece from player's pieces
            piece = player.pieces.pop(piece_idx)
            segment.pieces.append(piece)

    for card_uuid in default.card_uuids:
        # Find the card in the player's cards
        card_idx = next((i for i, player_card_uuid in enumerate(player.cards) if player_card_uuid == card_uuid), None)
        if card_idx is not None:
            # Remove the card from player's cards
            card_uuid = player.cards.pop(card_idx)
            # add to discard
            game.decks[game.carduuid2card[card_uuid].deck_idx].discard.append(card_uuid)

    game = game.set(players=game.players)
    game = game.set(edges=game.edges)
    game = game.set(player_graphs=calc_player_graphs(game)) # 

    return game


def calc_player_graph(game, player_idx):
    nodes = game.nodes
    node2neighbors = {node.idx: set() for node in nodes}

    for edge in game.edges:
        for path in edge.paths:
            for segment in path.segments:
                if segment.pieces and segment.pieces[0] and game.pieceuuid2piece[segment.pieces[0]].player_idx == player_idx:
                    # print(f"[path_idx {path.idx}] edge.start_point_uuid {edge.start_point_uuid} ({edge.node_1_idx}) connected to edge.end_point_uuid {edge.end_point_uuid} ({edge.node_2_idx}) player_idx: {player_idx}")
                    node2neighbors[edge.node_1_idx].add(edge.node_2_idx)
                    node2neighbors[edge.node_2_idx].add(edge.node_1_idx)
    
    return PlayerGraph(
        player_idx=player_idx, 
        neighbors=[
            list(node2neighbors.get(node_idx, set())) 
            for node_idx in range(len(nodes))
        ]
    )


def calc_player_graphs(game):
    game_config = game.game_config
    return [
        calc_player_graph(game, player_idx) 
        for player_idx in range(game_config.num_players)
    ]


# Does the opposite of handle_discard_action, i.e., it keeps the cards in the discard tray (the other cards are discarded)
def handle_keep_action(game, action):
    if not game or not action or not action.legal_action.keep:
        return game

    deck_idx = action.legal_action.keep.deck_idx
    if deck_idx < 0 or deck_idx >= len(game.decks):
        return game

    deck = game.decks[deck_idx]
    if not deck:
        return game

    player = game.players[action.legal_action.player_idx]
    if not player:
        return game

    # Keep the specified cards in the discard tray
    kept_cards = [card_uuid for card_uuid in player.discard_tray if card_uuid in action.keep.card_uuids]
    non_kept_cards = [card_uuid for card_uuid in player.discard_tray if card_uuid not in action.keep.card_uuids]


    # Discard the non-kept cards to the deck's discard pile
    deck.discard.extend(non_kept_cards)
    
    # Clear the discard tray and add the kept cards back
    player.cards.extend([c for c in kept_cards if c is not None])

    player.discard_tray.clear()
    return game.set(decks=game.decks, players=game.players)


def handle_discard_action(game, action):
    print("****************************** handle_discard_action 1", action)
    if not game or not action or not action.legal_action.discard:
        return game

    print("****************************** handle_discard_action 2", action)

    deck_idx = action.legal_action.discard.deck_idx
    if deck_idx < 0 or deck_idx >= len(game.decks):
        return game

    print("****************************** handle_discard_action 3", deck_idx)

    deck = game.decks[deck_idx]
    print("****************************** handle_discard_action 3.5", deck)
    if not deck:
        return game

    print("****************************** handle_discard_action 4")

    player = game.players[action.legal_action.player_idx]
    if not player:
        return game

    # Keep the specified cards in the discard tray
    non_kept_cards = [card_uuid for card_uuid in player.discard_tray if card_uuid in action.discard.card_uuids]
    kept_cards = [card_uuid for card_uuid in player.discard_tray if card_uuid not in action.discard.card_uuids]

    print("****************************** handle_discard_action 5", kept_cards)
    print("****************************** handle_discard_action 6", non_kept_cards)

    # Discard the non-kept cards to the deck's discard pile
    deck.discard.extend(non_kept_cards)
    
    # Clear the discard tray and add the kept cards back
    player.cards.extend([c for c in kept_cards if c is not None])

    player.discard_tray.clear()
    print("****************************** handle_discard_action 10 kept_cards: ", kept_cards)

    return game.set(decks=game.decks, players=game.players)


def shuffle_all_decks(game):
    if not game or not game.decks:
        return game

    for i in range(len(game.decks)):
        game = shuffle_deck(game, i)

    return game


def set_deck(game, deck_idx, deck):
    new_decks = game.decks[:deck_idx] + [deck] + game.decks[deck_idx + 1:]
    return game.set(decks=new_decks)


def shuffle(rng, deck):
    shuffled_cards = list(deck.facedown_stack)
    rng.shuffle(shuffled_cards)
    return deck.set(facedown_stack=shuffled_cards)


def shuffle_deck(game, deck_idx):
    if not game or not game.decks or deck_idx < 0 or deck_idx >= len(game.decks):
        return game
    
    deck = game.decks[deck_idx]
    if not deck or not deck.facedown_stack:
        return game

    shuffled_deck = shuffle(game.rng, deck)
    game = set_deck(game, deck_idx, shuffled_deck)
    return game


def shuffle_player_order(game):
    if not game or not game.player_idxs:
        return game
    
    rng = game.rng
    shuffled_idxs = list(game.player_idxs)
    rng.shuffle(shuffled_idxs)
    
    return game.set(player_idxs=shuffled_idxs)


def flip_cards(game, deck_idx, num_cards):
    if not game or deck_idx < 0 or deck_idx >= len(game.decks):
        return game
    
    deck = game.decks[deck_idx]
    if not deck or not deck.facedown_stack:
        return game

    # Flip the top num_cards from the facedown_stack to the faceup_spots
    for _ in range(num_cards):
        if deck.facedown_stack:
            card = deck.facedown_stack.pop()
            deck.faceup_spots.append(card)

    return game.set(decks=game.decks)


def distribute_all_piles(game):
    if not game or not game.piles:
        return game

    for pile in game.piles:
        player_idx = pile.player_idx
        if player_idx < 0 or player_idx >= len(game.players):
            continue
        
        player = game.players[player_idx]
        player.pieces.extend(pile.pieces)
        pile.pieces.clear()  # Clear the pile after distribution

    return game.set(players=game.players, piles=game.piles)


def deal_cards_to_each_player_discard_tray(game, deck_idx, num_cards):
    if not game or deck_idx < 0 or deck_idx >= len(game.decks):
        return game

    deck = game.decks[deck_idx]
    if not deck or not deck.facedown_stack:
        return game

    for player in game.players:
        # Deal cards to the player's discard tray
        for _ in range(num_cards):
            if deck.facedown_stack:
                card = deck.facedown_stack.pop()
                player.discard_tray.append(card)

    return game.set(players=game.players, decks=game.decks)


def deal_cards_to_each_player(game, deck_idx, num_cards):
    if not game or deck_idx < 0 or deck_idx >= len(game.decks):
        return game

    deck = game.decks[deck_idx]
    if not deck or not deck.facedown_stack:
        return game

    for player in game.players:
        player_hand = player.cards
        # Deal cards to the player's hand
        for _ in range(num_cards):
            if deck.facedown_stack:
                card = deck.facedown_stack.pop()
                player_hand.append(card)

    return game.set(players=game.players, decks=game.decks)


def append_all_to_legal_actions(game, legal_actions):
    if not game or not legal_actions:
        return game

    for legal_action in legal_actions:
        game = append_to_legal_actions(game, legal_action)

    return game


def append_to_legal_actions(game, legal_action):
    if not game:
        return game
    
    game.legal_actions_2.append(
        legal_action
    )
    
    return game.set(legal_actions_2=game.legal_actions_2)


def default_accept_action(game, action):
    # Returns true if action.legal_action is found in game.legal_actions_2
    # The comparision is by value, not by reference
    if not game or not action:
        return False
    
    if not action.legal_action:
        return False
    
    # Check if "action.move_pieces_to_path" is not None
    if action.move_pieces_to_path: 
        return is_move_pieces_to_path_action_legal(game, action)

    return action.legal_action in game.legal_actions_2


def is_move_pieces_to_path_action_legal(game, action):
    # print("******************************1234 is_move_pieces_to_path_action_legal 1")
    player_idx = action.legal_action.player_idx
    proposed_cards_uuids = action.move_pieces_to_path.card_uuids
    path_idx = action.legal_action.move_pieces_to_path.path_idx
    path = game.game_config.fig.board_config.board_paths[path_idx]
    proposed_cards = [card_uuid for card_uuid in game.players[player_idx].cards if card_uuid in proposed_cards_uuids]
    proposed_pieces = [piece_uuid for piece_uuid in game.players[player_idx].pieces if piece_uuid in action.move_pieces_to_path.piece_uuids]
    remaining_segments = path.path.segments

    # print("******************************1234 is_move_pieces_to_path_action_legal 1b: ", proposed_cards)
    # print("******************************1234 is_move_pieces_to_path_action_legal 1c: ", proposed_pieces)
    # print("******************************1234 is_move_pieces_to_path_action_legal 1d: ", len(remaining_segments))
    
    card_fulfillment, piece_fulfillment = get_path_fulfillment_from_resources(
        game,
        proposed_cards,
        proposed_pieces,
        remaining_segments,
    )

    # print("******************************1234 is_move_pieces_to_path_action_legal 2a", card_fulfillment)
    # print("******************************1234 is_move_pieces_to_path_action_legal 2b", piece_fulfillment)

    if card_fulfillment is None or piece_fulfillment is None:
        return False

    # print("******************************1234 is_move_pieces_to_path_action_legal 3")
    # print("******************************1234 is_move_pieces_to_path_action_legal piece_fulfillment: ", piece_fulfillment)
    # print("******************************1234 is_move_pieces_to_path_action_legal proposed_pieces: ", proposed_pieces)

    return (
        len(card_fulfillment) == len(proposed_cards_uuids) and
        len(piece_fulfillment) == len(proposed_pieces)
    )


def append_default_legal_actions_for_initial_player(game, action, log=False):
    # print("****************************************** Inside append_default_legal_actions_for_initial_player")

    # Clone HOOK_NAMESPACE
    namespace = HOOK_NAMESPACE.copy()

    try:
        # Execute the code string
        exec(DEFAULT_LEGAL_ACTIONS_HOOK, namespace)

        # Retrieve the handler function
        handler_func = namespace.get('handler')
        
        if handler_func is None or not callable(handler_func):
            raise ValueError("No callable function named 'handler' found in the code")
        
        # Call the handler function
        result = handler_func(game, game.player_idxs[0])
        if log:
            pass
            # print(f"****************************** Running initialization hook 3: {hook.uuid} {result.player_idxs}")
            # print(f"****************************** Result of handler(5, 3): {result}")
        return result

    except SyntaxError as e:
        logging.error(f"Syntax error in initialization hook --TODO--: {str(e)}", exc_info=True)
        return game
    except Exception as e:
        logging.error(f"Error in initialization hook --TODO--: {str(e)}", exc_info=True)
        return game


def append_default_legal_actions_for_next_player(game, action, log=False):

    # Clone HOOK_NAMESPACE
    namespace = HOOK_NAMESPACE.copy()

    try:
        # Execute the code string
        exec(DEFAULT_LEGAL_ACTIONS_HOOK, namespace)

        # Retrieve the handler function
        handler_func = namespace.get('handler')
        
        if handler_func is None or not callable(handler_func):
            raise ValueError("No callable function named 'handler' found in the code")
        
        # Call the handler function
        last_player_idx = action.legal_action.player_idx
        last_player_shuffled_idx = game.player_idxs.index(last_player_idx)
        next_player_shuffled_idx = (last_player_shuffled_idx + 1) % len(game.player_idxs)
        result = handler_func(game, game.player_idxs[next_player_shuffled_idx])
        if log:
            pass
            # print(f"****************************** Running initialization hook 3: {hook.uuid} {result.player_idxs}")
            # print(f"****************************** Result of handler(5, 3): {result}")
        return result

    except SyntaxError as e:
        logging.error(f"Syntax error in initialization hook --TODO--: {str(e)}", exc_info=True)
        return game
    except Exception as e:
        logging.error(f"Error in initialization hook --TODO--: {str(e)}", exc_info=True)
        return game


def get_total_path_count(game):
    return sum(len(edge.paths) for edge in game.edges)


def get_legal_actions_for_path(game, player_idx, path_idx):
    if path_idx < 0 or path_idx >= get_total_path_count(game):
        return []
    
    if not is_path_open_to_player(game, path_idx, player_idx):
        return []
    
    # TODO check if player has enough pieces to claim the path
    player_pieces = game.players[player_idx].pieces

    legal_actions = []
    default = get_sample_actionclaimpath(game, player_idx, path_idx)
    if default:
        legal_actions.append(
            LegalAction(
                player_idx=player_idx,
                name="CLAIM-PATH",
                title="Select resources to claim path",
                instruction="claim a path",
                allotted_seconds=60,
                allotted_since_action_idx=(len(game.history) - 1),
                btn_text="Claim path",
                move_pieces_to_path=LegalActionMovePiecesToPath(
                    path_idx=path_idx,
                    default=default
                )
            )
        )
        return legal_actions
    return []


def get_legal_actions_for_paths(game, player_idx):
    legal_actions = []
    
    for path in game.game_config.fig.board_config.board_paths:
        path_idx = path.num - 1
        legal_actions_for_path = get_legal_actions_for_path(game, player_idx, path_idx)
        if legal_actions_for_path:
            legal_actions.extend(legal_actions_for_path)
        # else:
        #     print(f"Path {path_idx} is not claimable by player {player_idx}")
    
    return legal_actions


def is_path_open_to_player(game, path_idx, player_idx):
    # TODO check if player has enough pieces to claim the path

    if not game or path_idx < 0 or path_idx >= get_total_path_count(game):
        return False
    
    # Check if any segment of the path has pieces from any player
    path = get_path_by_idx(game, path_idx)
    if path.segments[0].pieces:
        return False

    # Check if the player has enough pieces to claim the path
    player_pieces = game.players[player_idx].pieces
    if len(player_pieces) < len(path.segments):
        return False
    
    return True


HOOK_NAMESPACE = {
    'shuffle_all_decks': shuffle_all_decks,
    'shuffle_player_order': shuffle_player_order,
    'deal_cards_to_each_player': deal_cards_to_each_player,
    'deal_cards_to_each_player_discard_tray': deal_cards_to_each_player_discard_tray,
    'distribute_all_piles': distribute_all_piles,
    'flip_cards': flip_cards,
    'LegalActionDiscard': LegalActionDiscard,
    'LegalActionKeep': LegalActionKeep,
    'score_public_items': score_public_items,
    'score_private_items': score_private_items,
    'default_handle_scoring': default_handle_scoring,
    'default_handle_terminal': default_handle_terminal,
    'default_handle_action': default_handle_action,
    'handle_discard_action': handle_discard_action,
    'handle_keep_action': handle_keep_action,
    'handle_move_pieces_to_path_action': handle_move_pieces_to_path_action,
    'handle_after_move_pieces_to_path_action': handle_after_move_pieces_to_path_action,
    'handle_move_bonus_cards': handle_move_bonus_cards,
    'handle_move_longest_path_card': handle_move_longest_path_card,
    'find_player_with_longest_path_card': find_player_with_longest_path_card,
    'default_after_accept_action': default_after_accept_action,
    'default_accept_action': default_accept_action,
    'append_default_legal_actions_for_initial_player': append_default_legal_actions_for_initial_player,
    'append_default_legal_actions_for_next_player': append_default_legal_actions_for_next_player,
    'LegalAction': LegalAction,
    'append_to_legal_actions': append_to_legal_actions,
    'append_all_to_legal_actions': append_all_to_legal_actions,
    'LegalActionDraw': LegalActionDraw,
    'LegalActionDrawDiscard': LegalActionDrawDiscard,
    'LegalActionFaceupDraw': LegalActionFaceupDraw,
    'LegalActionMovePiecesToPath': LegalActionMovePiecesToPath,
    'get_legal_actions_for_paths': get_legal_actions_for_paths,
    'get_legal_actions_for_path': get_legal_actions_for_path,
    'is_path_open_to_player': is_path_open_to_player,
    'ActionMovePiecesToPath': ActionMovePiecesToPathOptional,
}


def get_wild_unit_uuids(game):
    wild_unit_uuids = []
    for card in game.carduuid2card.values():
        if card.is_wild:
            wild_unit_uuids.append(card.resource_uuid)
    return wild_unit_uuids


def match_strict_wild(game, fulfillment, cards, segments):
    new_fulfillment = fulfillment.copy()
    new_cards = cards.copy()
    wild_unit_uuids = get_wild_unit_uuids(game)
    new_segments = []

    for segment in segments:
        if segment.unit_uuid and segment.unit_uuid in wild_unit_uuids:
            first_matching_idx = next((i for i, card_uuid in enumerate(new_cards) if game.carduuid2card[card_uuid].resource_uuid == segment.unit_uuid), None)
            if first_matching_idx is not None:
                new_fulfillment.append(new_cards.pop(first_matching_idx))
            else:
                new_segments.append(segment)
        else:
            new_segments.append(segment)

    return new_fulfillment, new_cards, new_segments


def match_non_wild_non_empty(game, fulfillment, cards, segments, log=False):
    new_fulfillment = fulfillment.copy()
    new_cards = cards.copy()
    wild_unit_uuids = get_wild_unit_uuids(game)
    new_segments = []

    for segment in segments:
        first_strict_matching_idx = next((i for i, card_uuid in enumerate(new_cards) if game.carduuid2card[card_uuid].resource_uuid == segment.unit_uuid), None)
        first_wild_matching_idx = next((i for i, card_uuid in enumerate(new_cards) if game.carduuid2card[card_uuid].resource_uuid in wild_unit_uuids), None)
        first_matching_idx = first_strict_matching_idx if first_strict_matching_idx is not None else first_wild_matching_idx
        if first_matching_idx is not None:
            new_fulfillment.append(new_cards.pop(first_matching_idx))
        else:
            new_segments.append(segment)
    
    return new_fulfillment, new_cards, new_segments

    


def match_empty(game, fulfillment, cards, segments):
    num_empty_segments = sum(1 for segment in segments if segment.unit_uuid is None)
    if num_empty_segments == 0:
        return fulfillment, cards, segments
    
    tuples = get_uniform_sets(game, cards, num_empty_segments)
    # print(f"****************************************** len(cards): {len(cards)}")
    # print(f"****************************************** num_empty_segments: {num_empty_segments}")
    # print(f"Found {len(tuples)} tuples for empty segments: {tuples}")
    if len(tuples) == 0:
        return fulfillment, cards, segments
    
    new_fulfillment = fulfillment.copy()

    new_segments = []
    for segment in segments:
        if segment.unit_uuid:
            new_segments.append(segment)

    first_tuple = tuples[0][:num_empty_segments]
    # print(f"Using first tuple for empty segments: {first_tuple}")
    new_cards = list(set(cards) - set(first_tuple))
    new_fulfillment.extend(first_tuple)
    return new_fulfillment, new_cards, new_segments


def get_uniform_sets(game, cards, min_length):
    wilds = [card_uuid for card_uuid in cards if game.carduuid2card[card_uuid].is_wild]
    non_wilds = [card_uuid for card_uuid in cards if not game.carduuid2card[card_uuid].is_wild]
    # print("********************* cards: ", cards)
    # print("********************* wilds: ", wilds)
    # print("********************* non_wilds: ", non_wilds)
    unit_uuid_2_cards = {}
    for card_uuid in non_wilds:
        card = game.carduuid2card[card_uuid]
        if card.resource_uuid not in unit_uuid_2_cards:
            unit_uuid_2_cards[card.resource_uuid] = []
        unit_uuid_2_cards[card.resource_uuid].append(card_uuid)
    
    uniform_sets_no_wilds = [
        card_uuids for card_uuids in unit_uuid_2_cards.values() if len(card_uuids) >= min_length
    ]
    # print("********************* uniform_sets_no_wilds: ", uniform_sets_no_wilds)
    # print("********************* length: ", min_length)
    # print("********************* unit_uuid_2_cards.values(): ", unit_uuid_2_cards.values())

    uniform_sets_with_wilds = []
    for num_wilds in range(0, len(wilds)+1):
        uniform_set = wilds[:num_wilds]
        if len(uniform_set) >= min_length:
            uniform_sets_with_wilds.append(uniform_set)
        for unit_uuid, cards in unit_uuid_2_cards.items():
            uniform_set = cards + wilds[:num_wilds]
            if len(uniform_set) >= min_length:
                uniform_sets_with_wilds.append(uniform_set)

    # Sort the uniform sets by their length, smallest first
    uniform_sets_no_wilds.sort(key=len)
    uniform_sets_with_wilds.sort(key=len)
    # print("********************* uniform_sets_no_wilds 2: ", uniform_sets_no_wilds)
    sorted = uniform_sets_no_wilds + uniform_sets_with_wilds
    # print("********************* sorted : ", sorted)
    # Filter out sets that are smaller than the required length
    return sorted


def does_fulfill_path(game, player_idx, path_idx, fulfillment):
    return False


def get_sample_actionclaimpath(game, player_idx, path_idx):
    card_fulfillment, piece_fulfillment = get_sample_path_fulfillment(game, player_idx, path_idx)
    if not card_fulfillment or not piece_fulfillment:
        return None

    return ActionMovePiecesToPathOptional(
        piece_uuids=[piece_uuid for piece_uuid in piece_fulfillment],
        card_uuids=card_fulfillment,
    )


def get_sample_path_fulfillment(game, player_idx, path_idx):
    log = path_idx == 3 and player_idx == 1
    path = game.game_config.fig.board_config.board_paths[path_idx]
    remaining_card_uuids = [card_uuid for card_uuid in game.players[player_idx].cards if game.carduuid2card[card_uuid].deck_idx == 0]
    remaining_pieces = [
        piece_uuid 
        for piece_uuid in game.players[player_idx].pieces 
        if game.pieceuuid2piece[piece_uuid].piece_template_idx == 0
    ]
    remaining_segments = path.path.segments
    return get_path_fulfillment_from_resources(
        game,
        remaining_card_uuids,
        remaining_pieces,
        remaining_segments,
        log,
    )


def get_path_fulfillment_from_resources(game, remaining_card_uuids, remaining_pieces, remaining_segments, log=False):

    if len(remaining_pieces) < len(remaining_segments):
        print("Not enough pieces to fulfill the path segments")
        return None, None
    
    piece_fulfillment = remaining_pieces[:len(remaining_segments)]

    card_fulfillment = []
    card_fulfillment, remaining_card_uuids, remaining_segments = match_strict_wild(game, card_fulfillment, remaining_card_uuids, remaining_segments)

    if len(remaining_segments) == 0:
        return card_fulfillment, piece_fulfillment
    # Probably don't need this check, but we should unit test
    # elif len(get_wild_segments(remaining_segments)) > 0:
    #     return None

    card_fulfillment, remaining_card_uuids, remaining_segments = match_non_wild_non_empty(game, card_fulfillment, remaining_card_uuids, remaining_segments, log)
    if len(remaining_segments) == 0:
        return card_fulfillment, piece_fulfillment
    # Probably don't need this check, but we should unit test
    # elif len(get_non_wild_non_empty_segments(remaining_segments)) > 0:
    #     return None

    card_fulfillment, remaining_card_uuids, remaining_segments = match_empty(game, card_fulfillment, remaining_card_uuids, remaining_segments)
    if len(remaining_segments) == 0:
        return card_fulfillment, piece_fulfillment

    # print("get_path_fulfillment_from_resources (None, None) because remaining_segments is not empty: ", remaining_segments)
    return None, None


def run_state_action_hook(state, action, hook, log=False):

    # Clone HOOK_NAMESPACE
    namespace = HOOK_NAMESPACE.copy()

    try:
        # Execute the code string
        exec(hook.code, namespace)

        # Retrieve the handler function
        handler_func = namespace.get('handler')
        
        if handler_func is None or not callable(handler_func):
            raise ValueError("No callable function named 'handler' found in the code")
        
        # Call the handler function
        result = handler_func(state, action)
        if log:
            pass
            # print(f"****************************** Running initialization hook 3: {hook.uuid} {result.player_idxs}")
            # print(f"****************************** Result of handler(5, 3): {result}")
        return result

    except SyntaxError as e:
        logging.error(f"Syntax error in initialization hook {hook.uuid}: {str(e)}", exc_info=True)
        return state
    except Exception as e:
        logging.error(f"Error in initialization hook {hook.uuid}: {str(e)}", exc_info=True)
        return state


def run_state_hook(state, hook, log=False):

    namespace = HOOK_NAMESPACE.copy()

    try:
        # Execute the code string
        exec(hook.code, namespace)
        
        # Retrieve the handler function
        handler_func = namespace.get('handler')
        
        if handler_func is None or not callable(handler_func):
            raise ValueError("No callable function named 'handler' found in the code")
        
        # Call the handler function
        result = handler_func(state)
        # if log:
        #     print(f"****************************** Running initialization hook 3: {hook.uuid} {result.player_idxs}")
            # print(f"****************************** Result of handler(5, 3): {result}")
        return result

    except SyntaxError as e:
        logging.error(f"Syntax error in initialization hook {hook.uuid}: {str(e)}", exc_info=True)
        return state
    except Exception as e:
        logging.error(f"Error in initialization hook {hook.uuid}: {str(e)}", exc_info=True)
        return state


# Implementing the following Julia function:
# function getfaceupspots(f, unit_deck, unit_deck_idx)
#     num_faceup_spots = getsettingvalue(f, :num_faceup_spots)
#     unit_deck[unit_deck_idx:(unit_deck_idx+(num_faceup_spots - 1))]
# end
def getfaceupspots(f, unit_deck, unit_deck_idx):
    num_faceup_spots = getsettingvalue(f, 'num_faceup_spots')
    if num_faceup_spots is None:
        raise ValueError("Setting 'num_faceup_spots' not found in board config.")
    return unit_deck[unit_deck_idx:(unit_deck_idx + num_faceup_spots)] if unit_deck_idx < len(unit_deck) else []


@dispatch(GameConfig, list, bool)
def getstate(game_config, actions, log):
    return reduce(lambda state, action: getnextstate(state, action, log), actions, getinitialstate(game_config))


@dispatch(State, AltAction, NoAction)
def getnextstate(s, action, action_type):
    return s


# Implementing the following Julia function:
# getpath(f::Fig, num::Int) = f.board_config.board_paths[num]
def getpath(f, num):
    if f and f.board_config and num < len(f.board_config.board_paths):
        return f.board_config.board_paths[num]
    raise ValueError(f"Path number {num} not found in board config.")


# Implementing the following Julia function:
# function getnextstate(s::State, a::Action, ::Val{:CLAIM_PATH})
#     player_hand_idx = findfirst(p -> p.player_idx == a.player_idx, s.player_hands)
#     player_hand = s.player_hands[player_hand_idx]
#     num_path_pieces = getpath(s.fig, a.path_idx).path.segments |> length
#     @reset player_hand.num_pieces = player_hand.num_pieces - num_path_pieces
#     new_unit_cards, new_discards = removecombo(player_hand, a.unit_combo)
#     @reset s.unit_discards = [s.unit_discards..., new_discards...]
#     @reset player_hand.unit_cards = new_unit_cards
#     @reset player_hand.paths = [player_hand.paths..., a.path_idx]
#     @reset player_hand.completed_routes = getcompletedroutes(s.fig, player_hand)
#     longest_road, longest_road_len = getlongestroad(s.fig, player_hand)
#     @reset player_hand.longest_road = longest_road
#     @reset player_hand.longest_road_len = longest_road_len
#     @reset s.player_hands = [p.player_idx == a.player_idx ? player_hand : p for p in s.player_hands]
#     @reset s.longest_road_player_idxs = getlongestroadplayeridxs(s.player_hands)
#     @reset s.most_clusters_player_idxs = getmostclustersplayeridxs(s.player_hands)
#     s
# end
@dispatch(State, AltAction, MovePiecesToPathAction)
def getnextstate(s, action, action_type):
    player_hand_idx = next((i for i, p in enumerate(s.player_hands) if p.player_idx == action.player_idx), None)
    if player_hand_idx is None:
        raise ValueError(f"Player index {action.player_idx} not found in player hands.")
    
    player_hand = s.player_hands[player_hand_idx]
    num_path_pieces = len(getpath(s.game_config.fig, action.path_idx).path.segments)
    # @reset player_hand.num_pieces = player_hand.num_pieces - num_path_pieces
    player_hand = player_hand.set(num_pieces=player_hand.num_pieces - num_path_pieces)

    # new_unit_cards, new_discards = removecombo(player_hand, a.unit_combo)
    new_unit_cards, new_discards = pvector([]), pvector([])
    if action.unit_combo:
        new_unit_cards, new_discards = removecombo(player_hand, action.unit_combo)
    # @reset s.unit_discards = [s.unit_discards..., new_discards...]
    s = s.set(unit_discards=s.unit_discards.extend(new_discards))
    # @reset player_hand.unit_cards = new_unit_cards
    player_hand = player_hand.set(unit_cards=new_unit_cards)
    # @reset player_hand.paths = [player_hand.paths..., a.path_idx]
    player_hand = player_hand.set(paths=player_hand.paths + [action.path_idx])
    # @reset player_hand.completed_routes = getcompletedroutes(s.fig, player_hand)

    if len(s.game_config.fig.board_config.routes) > 0:
        player_hand = player_hand.set(completed_routes=getcompletedroutes(s.game_config.fig, player_hand))

    ###longest_road, longest_road_len = getlongestroad(s.game_config.fig, player_hand)
    # @reset player_hand.longest_road = longest_road
    ###player_hand = player_hand.set(longest_road=longest_road)
    # @reset player_hand.longest_road_len = longest_road_len
    ###player_hand = player_hand.set(longest_road_len=longest_road_len)
    
    # Implementing the following Julia function:
    # @reset s.player_hands = [p.player_idx == a.player_idx ? player_hand : p for p in s.player_hands]
    s = s.transform(
        ('player_hands', player_hand_idx),
        player_hand.set(player_idx=player_hand.player_idx),
    )

    # @reset s.longest_road_player_idxs = getlongestroadplayeridxs(s.player_hands)
    ###s = s.set(longest_road_player_idxs=getlongestroadplayeridxs(s.player_hands))
    # @reset s.most_clusters_player_idxs = getmostclustersplayeridxs(s.player_hands)
    s = s.set(most_clusters_player_idxs=getmostclustersplayeridxs(s.player_hands))
    return s


def getlinkadjmat(fig, paths):
    path2edgeidx = {}
    edgeidx2edge = {}
    for frozen_path in fig.board_config.board_paths:
        edge_num = frozen_path.link_num
        path_num = frozen_path.num
        path2edgeidx[path_num - 1] = edge_num - 1
        edgeidx2edge[edge_num - 1] = (frozen_path.start_point_num-1, frozen_path.end_point_num-1)

    num_nodes = len(fig.board_config.points)
    adj_mat = np.eye(num_nodes, dtype=int)

    # print("path2edgeidx: ", path2edgeidx)
    # print("\nedgeidx2edge: ", edgeidx2edge)

    for path_idx in paths:
        edge_idx = path2edgeidx[path_idx]
        src, dst = edgeidx2edge[edge_idx]
        adj_mat[src, dst] = 1
        adj_mat[dst, src] = 1

    return adj_mat


def getcompletedroutes(fig, player_hand, log=False):
    adj_mat = getlinkadjmat(fig, player_hand.paths)

    if False:
        print("\nadj_mat:")
        print(adj_mat)

    route_nums = player_hand.route_cards
    routes = fig.board_config.routes
    num_points = len(fig.board_config.points)

    # print("route_nums: ", route_nums)

    visited_nodes = np.column_stack([
        np.eye(1, num_points, routes[route_num - 1].start_num, dtype=int).flatten()
        for route_num in route_nums
    ])

    target_nodes = np.column_stack([
        np.eye(1, num_points, routes[route_num - 1].end_num, dtype=int).flatten()
        for route_num in route_nums
    ])

    if False:
        print("\nvisited_nodes:")
        print(visited_nodes)
        print("\ntarget_nodes:")
        print(target_nodes)

    for _ in range(len(player_hand.paths)):
        visited_nodes = (adj_mat @ visited_nodes) > 0

    res = visited_nodes & target_nodes

    if log:
        print("\nres:")
        print(res)

    bools = np.any(res, axis=0)
    completed = [route_num for route_num, completed_bool in zip(route_nums, bools) if completed_bool]

    return completed



# Implementing the following Julia function:
# function getnextstate(s::State, a::Action, ::Val{:CLAIM_POINT})
#     player_hand_idx = findfirst(p -> p.player_idx == a.player_idx, s.player_hands)
#     player_hand = s.player_hands[player_hand_idx]
#     @reset player_hand.num_point_pieces = player_hand.num_point_pieces - 1
#     new_unit_cards, new_discards = removecombo(player_hand, a.unit_combo)
#     @reset s.unit_discards = [s.unit_discards..., new_discards...]
#     @reset player_hand.unit_cards = new_unit_cards
#     @reset player_hand.points = [player_hand.points..., a.point_uuid]
#     @reset player_hand.completed_clusters = getcompletedclusters(s.fig, player_hand)
#     @reset s.player_hands = [p.player_idx == a.player_idx ? player_hand : p for p in s.player_hands]
#     @reset s.most_clusters_player_idxs = getmostclustersplayeridxs(s.player_hands)
#     s
# end
@dispatch(State, AltAction, ClaimPointAction)
def getnextstate(s, action, action_type):
    player_hand_idx = next((i for i, p in enumerate(s.player_hands) if p.player_idx == action.player_idx), None)
    if player_hand_idx is None:
        raise ValueError(f"Player index {action.player_idx} not found in player hands.")
    
    player_hand = s.player_hands[player_hand_idx]
    # @reset player_hand.num_point_pieces = player_hand.num_point_pieces - 1
    player_hand = player_hand.set(num_point_pieces=player_hand.num_point_pieces - 1)

    # new_unit_cards, new_discards = removecombo(player_hand, a.unit_combo)
    new_unit_cards, new_discards = pvector([]), pvector([])
    if action.unit_combo:
        new_unit_cards, new_discards = removecombo(player_hand, action.unit_combo)
    # @reset s.unit_discards = [s.unit_discards..., new_discards...]
    s = s.set(unit_discards=s.unit_discards.extend(new_discards))
    # @reset player_hand.unit_cards = new_unit_cards
    player_hand = player_hand.set(unit_cards=new_unit_cards)
    # @reset player_hand.points = [player_hand.points..., a.point_uuid]
    player_hand = player_hand.set(points=player_hand.points + [action.point_uuid])
    # @reset player_hand.completed_clusters = getcompletedclusters(s.fig, player_hand)
    player_hand = player_hand.set(completed_clusters=getcompletedclusters(s.game_config.fig, player_hand))
    # @reset s.player_hands = [p.player_idx == a.player_idx ? player_hand : p for p in s.player_hands]
    s = s.transform(
        ('player_hands', player_hand_idx),
        player_hand.set(player_idx=player_hand.player_idx),
    )
    # @reset s.most_clusters_player_idxs = getmostclustersplayeridxs(s.player_hands)
    s = s.set(most_clusters_player_idxs=getmostclustersplayeridxs(s.player_hands))
    
    return s


# Implementing the following Julia function:
# function getmostclustersplayeridxs(player_hands::Vector{PlayerInfo})
#     most_clusters = maximum([length(p.completed_clusters) for p in player_hands])
#     if iszero(most_clusters)
#         return Int[]
#     end
#     [p.player_idx for p in player_hands if length(p.completed_clusters) == most_clusters]
# end
def getmostclustersplayeridxs(player_hands):
    most_clusters = max(len(p.completed_clusters) for p in player_hands)
    if most_clusters == 0:
        return []
    return [p.player_idx for p in player_hands if len(p.completed_clusters) == most_clusters]


# Implementing the following Julia function:
# function getcompletedclusters(fig::Fig, player_hand::PlayerInfo; log=false)
#     (; clusters) = fig.board_config
#     completed = filter(clusters) do cluster
#         for point in cluster.points
#             if !in(point, player_hand.points)
#                 return false
#             end
#         end
#         true
#     end
#     if isempty(completed)
#         return UUID[]
#     end
#     [x.uuid for x in completed]
# end
def getcompletedclusters(fig, player_hand, log=False):
    clusters = fig.board_config.clusters
    completed = [
        cluster
        for cluster in clusters
        if all(point in player_hand.points for point in cluster.points)
    ]
    if not completed:
        return []
    return [x.uuid for x in completed]

# Implementing the following Julia function:
# function removecombo(player_hand::PlayerInfo, combo::String)
#     (; unit_cards) = player_hand
#     unit_cards_to_remove = parse.(Int, split(combo, "-"))
#     new_unit_cards = filter(x->!in(x, unit_cards_to_remove), unit_cards)
#     new_discards = unit_cards_to_remove
#     new_unit_cards, new_discards
# end
def removecombo(player_hand, combo):
    if not combo:
        return player_hand.unit_cards, []
    unit_cards_to_remove = list(map(int, combo.split("-")))
    new_unit_cards = pvector([x for x in player_hand.unit_cards if x not in unit_cards_to_remove])
    new_discards = pvector([x for x in unit_cards_to_remove if x in player_hand.unit_cards])
    if len(new_discards) != len(unit_cards_to_remove):
        raise ValueError(f"Discarded cards {new_discards} do not match combo {combo} (from {player_hand.unit_cards})")
    return new_unit_cards, new_discards


@dispatch(State, AltAction, DrawUnitFaceupAction)
def getnextstate(s, action, action_type):
    pass
# Implementing the following Julia function:
# function getnextstate(s::State, a::Action, ::Val{:DRAW_UNIT_FACEUP})
#     player_hand_idx = findfirst(p -> p.player_idx == a.player_idx, s.player_hands)
#     player_hand = s.player_hands[player_hand_idx]
#     player_new_unit_idx = s.faceup_spots[a.draw_faceup_spot_num]

#     if isempty(s.unit_cards)
#         # TODO: do we need to reshuffle the unit discards?
#         @reset s.faceup_spots[a.draw_faceup_spot_num] = nothing
#     else
#         @reset s.faceup_spots[a.draw_faceup_spot_num] = s.unit_cards[end]
#         @reset s.unit_cards = s.unit_cards[1:end-1]
#     end

#     s = recycleunitdiscardsifneeded(s)
#     @reset s.player_hands[player_hand_idx].unit_cards = [player_hand.unit_cards..., player_new_unit_idx]
#     num_market_refills = 0

#     num_faceup_spots = getsettingvalue(s.fig, :num_faceup_spots)

#     s
# end
    player_hand_idx = next((i for i, p in enumerate(s.player_hands) if p.player_idx == action.player_idx), None)
    if player_hand_idx is None:
        raise ValueError(f"Player index {action.player_idx} not found in player hands.")
    player_hand = s.player_hands[player_hand_idx]
    player_new_unit_idx = s.faceup_spots[action.draw_faceup_spot_num-1]

    if not s.unit_cards:
        # TODO: do we need to reshuffle the unit discards?
        # @reset s.faceup_spots[a.draw_faceup_spot_num] = nothing
        s = s.set(
            faceup_spots = s.faceup_spots.set(action.draw_faceup_spot_num-1, None)
        )
    else:
        # Implementing the following Julia code:
        # @reset s.faceup_spots[a.draw_faceup_spot_num] = s.unit_cards[end]
        # @reset s.unit_cards = s.unit_cards[1:end-1]
        s = s.set(
            faceup_spots = s.faceup_spots.set(action.draw_faceup_spot_num-1, s.unit_cards[-1])
        )
        s = s.set(unit_cards = s.unit_cards[:-1])
    
    # s = recycleunitdiscardsifneeded(s)
    unit_cards = player_hand.unit_cards
    s = s.transform(
        ('player_hands', player_hand_idx),
        player_hand.set(unit_cards=unit_cards.append(player_new_unit_idx)),
    )
    num_market_refills = 0
    num_faceup_spots = getsettingvalue(s.game_config.fig, 'num_faceup_spots')
    return s


# Implementing the following Julia function:
# function getsettingvalue(f::Fig, setting_name::Symbol)
#     for setting in f.board_config.settings
#         if Symbol(setting.name) === setting_name
#             return JSON3.read(setting.value_json)
#         end
#     end
#     nothing
# end
@dispatch(Fig, str)
def getsettingvalue(f, setting_name):
    for setting in f.board_config.settings:
        if setting.name == setting_name:
            return json.loads(setting.value_json)
    return None

@dispatch(State, str)
def getsettingvalue(s, setting_name):
    return getsettingvalue(s.game_config.fig, setting_name)


@dispatch(State, AltAction, DrawUnitDeckAction)
def getnextstate(s, action, action_type):
# Implementing the following Julia function:
# function getnextstate(s::State, a::Action, ::Val{:DRAW_UNIT_DECK})
#     player_hand_idx = findfirst(p -> p.player_idx == a.player_idx, s.player_hands)
#     player_hand = s.player_hands[player_hand_idx]
#     @assert anyunitcardsleft(s) "Unit and discard decks are empty. Action illegal!"
#     s = recycleunitdiscardsifneeded(s)
#     drawn_card = s.unit_cards[end]
#     @reset s.unit_cards = s.unit_cards[1:end-1]
#     @reset s.player_hands[player_hand_idx].unit_cards = [player_hand.unit_cards..., drawn_card]
#     s = recycleunitdiscardsifneeded(s)
#     s
# end
    player_hand_idx = next((i for i, p in enumerate(s.player_hands) if p.player_idx == action.player_idx), None)
    if player_hand_idx is None:
        raise ValueError(f"Player index {action.player_idx} not found in player hands.")
    
    ## if not anyunitcardsleft(s):
    ##     raise ValueError("Unit and discard decks are empty. Action illegal!")
    ## s = recycleunitdiscardsifneeded(s)
    drawn_card = s.unit_cards[-1]
    s = s.set(unit_cards = s.unit_cards[:-1])
    
    # @reset s.player_hands[player_hand_idx].unit_cards = [player_hand.unit_cards..., drawn_card]
    player_hand = s.player_hands[player_hand_idx]
    unit_cards = player_hand.unit_cards
    s = s.transform(
        ('player_hands', player_hand_idx), 
        player_hand.set(unit_cards=unit_cards.append(drawn_card)),
    )

    ## s = recycleunitdiscardsifneeded(s)
    return s


@dispatch(State, AltAction)
def getnextstateold(s, action):
    action_type = getactiontype(action.action_name)
    next = getnextstate(s, action, action_type)
    next = next.set(action_history=(next.action_history + [action]))
    return next


# Implementing the following Julia function:
# function isactionlegal(s::State, a::Action)
#     action_specs = getlegalactions(s)
#     for action_spec in action_specs
#         if istospec(action_spec, a)
#             return true
#         else
#             # println("Action is not to spec~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", a, action_spec)
#         end
#     end
#     false
# end
def isactionlegal(s, a):
    action_specs = getlegalactionspecs(s)
    for action_spec in action_specs:
        if istospec(action_spec, a):
            return True
        else:
            # println("Action is not to spec~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", a, action_spec)
            pass
    return False


def isactionlegal2(s, a):
    return run_accept_action_hooks(s, a, ACCEPT_ACTION_HOOKS, False)


def istospec(action_spec, a):
    if action_spec.action_name != a.action_name:
        # print(f"istospec: action_spec.action_name != a.action_name: {action_spec.action_name} != {a.action_name}")
        return False
    if action_spec.player_idx != a.player_idx:
        # print(f"istospec: action_spec.player_idx != a.player_idx: {action_spec.player_idx} != {a.player_idx}")
        return False
    # TODO: properly implement
    return True


@dispatch(State, AltAction)
def getnextstate(s, action):
    return getnextstate(s, action, False)


# Implementing the following Julia function:
# function getnextstate(s::State, a::Action)
#     if !isactionlegal(s, a)
#         println("Action is not legal~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", a)
#         return nothing
#     end
#     next = getnextstate(s, a, Val(Symbol(a.action_name)))

#     if next.last_to_play == a.player_idx
#         @reset next.terminal = true
#         next = calcwinners(next)
#     elseif isnothing(next.last_to_play)
#         player_hand = next.player_hands[a.player_idx]
#         if getsettingvalue(s.fig, :terminal_two_or_less_pieces) && player_hand.num_pieces <= 2
#             @reset next.last_to_play = a.player_idx
#         elseif getsettingvalue(s.fig, :terminal_first_cluster) && length(player_hand.completed_clusters) > 0
#             @reset next.last_to_play = a.player_idx
#             @reset next.terminal = true
#             next = calcwinners(next)
#         elseif (
#             getsettingvalue(s.fig, :terminal_no_available_points) 
#             && length(getunavailablepoints(next)) == length(next.fig.board_config.points)
#         )
#             @reset next.last_to_play = a.player_idx
#             @reset next.terminal = true
#             next = calcwinners(next)
#         end
#     end

#     @reset next.action_history = [next.action_history..., a]
#     assertallcardsaccountedfor(next)
#     next
# end
@dispatch(State, AltAction, bool)
def getnextstate(s, action, log):
    if log:
        printstate(s)
        print("(Potential action)")
        printaction(action, getstateidx(s))

    if not isactionlegal(s, action):
        print("Action is not legal~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", action)
        return None
    next = getnextstate(s, action, getactiontype(action.action_name))

    if next.last_to_play == action.player_idx:
        next = next.set(terminal=True)
        next = calcwinners(next)
    elif next.last_to_play is None:
        player_hand = next.player_hands[action.player_idx]
        terminal_two_or_less_pieces = getsettingvalue(s.game_config.fig, 'terminal_two_or_less_pieces')
        terminal_first_cluster = getsettingvalue(s.game_config.fig, 'terminal_first_cluster')
        terminal_no_available_points = getsettingvalue(s.game_config.fig, 'terminal_no_available_points')
        if terminal_two_or_less_pieces and player_hand.num_pieces <= 2:
            next = next.set(last_to_play=action.player_idx)
        elif terminal_first_cluster and len(player_hand.completed_clusters) > 0:
            next = next.set(last_to_play=action.player_idx, terminal=True)
            next = calcwinners(next)
        elif (
            terminal_no_available_points
            and len(getunavailablepoints(next)) == len(next.game_config.fig.board_config.points)
        ):
            next = next.set(last_to_play=action.player_idx, terminal=True)
            next = calcwinners(next)

    next = next.set(action_history=(next.action_history + [action]))
    assertallcardsaccountedfor(next)

    return next


def getnextstate2(s, a, log=False):
    s = run_state_action_hooks(s, a, AFTER_ACCEPT_ACTION_HOOKS, log)
    s = run_state_action_hooks(s, a, HANDLE_ACTION_HOOKS, log)
    s = run_state_hooks(s, HANDLE_SCORING_HOOKS, log)
    s = run_state_hooks(s, HANDLE_TERMINAL_HOOKS, log)
    if not s.legal_actions_2:
        s = run_state_action_hooks(s, a, EMPTY_LEGAL_ACTIONS_HOOKS, log)
    return s

@dispatch(State, AltAction, RouteDiscardAction)
def getnextstate(s, action, action_type):
# Implementing the following Julia function:
# function getnextstate(s::State, a::Action, ::Val{:ROUTE_DISCARD})
#     player_hand = s.player_hands[a.player_idx]
#     route_card_hand_nums = collect(a.return_route_cards)
#     return_route_card_nums = player_hand.new_route_cards[route_card_hand_nums]
#     chosen = setdiff(Set(player_hand.new_route_cards), Set(return_route_card_nums))
#     existing_route_cards = player_hand.route_cards
#     @reset s.player_hands[a.player_idx].route_cards = [existing_route_cards..., chosen...]
#     @reset s.route_discards = [s.route_discards..., return_route_card_nums...]
#     @reset s.player_hands[a.player_idx].new_route_cards = []
#     s
# end
    player_hand_idx = next((i for i, p in enumerate(s.player_hands) if p.player_idx == action.player_idx), None)
    if player_hand_idx is None:
        raise ValueError(f"Player index {action.player_idx} not found in player hands.")
    
    player_hand = s.player_hands[player_hand_idx]
    route_card_hand_idxs = list(action.return_route_cards)
    return_route_card_nums = [player_hand.new_route_cards[i] for i in route_card_hand_idxs]
    chosen = set(list(player_hand.new_route_cards)) - set(return_route_card_nums)
    
    print(f"new_route_cards: {list(player_hand.new_route_cards)}")
    print(f"return_route_card_nums: {return_route_card_nums}")
    print(f"Chosen route cards: {chosen}")
    
    # @reset s.player_hands[a.player_idx].route_cards = [existing_route_cards..., chosen...]
    print(f"Existing route cards: {list(player_hand.route_cards)}")
    player_hand = player_hand.set(route_cards=player_hand.route_cards + pvector(list(chosen)))
    print(f"New route cards: {list(player_hand.route_cards)}")
    # @reset s.route_discards = [s.route_discards..., return_route_card_nums...]
    s = s.set(route_discards=s.route_discards + return_route_card_nums)
    # @reset s.player_hands[a.player_idx].new_route_cards = []
    player_hand = player_hand.set(new_route_cards=pvector([]))
    print(f"New route cards: {list(player_hand.route_cards)}")

    s = s.transform(('player_hands', player_hand_idx), player_hand)

    return s


@dispatch(State, QValueLearningPolicy)
def getnextaction(s, policy):
    player_idx = gettoplay(s)[0]
    legal_action_specs = getlegalactionspecsforplayer(s, player_idx, None, None)
    legal_actions = get_all_legal_actions(s, player_idx, legal_action_specs)
    
    if s.rng.random() <= policy.epsilon:
        random_action = legal_actions[s.rng.randint(0, len(legal_actions) - 1)]
        return random_action
    
    q_values = policy.qvalue_fn(s, legal_actions)
    argmax_idx = max(range(len(q_values)), key=lambda i: q_values[i])

    return legal_actions[argmax_idx]


def get_all_legal_actions(s, player_idx, legal_action_specs):
    legal_actions = []
    
    for action_spec in legal_action_specs:
        if action_spec.action_name == "ROUTE_DISCARD":
            legal_actions.append(
                AltAction(
                    action_name="ROUTE_DISCARD", 
                    player_idx=player_idx,
                    return_route_cards=[0],  # Placeholder, should be filled with actual logic
                )
            )
        
        elif action_spec.action_name == "DRAW_UNIT_FACEUP":
            draw_faceup_spot_num = 1  # Placeholder, should be filled with actual logic
            legal_actions.append(
                AltAction(
                    action_name="DRAW_UNIT_FACEUP", 
                    player_idx=player_idx,
                    draw_faceup_unit_card_num=s.faceup_spots[draw_faceup_spot_num-1],
                    draw_faceup_spot_num=draw_faceup_spot_num,
                )
            )
        
        elif action_spec.action_name == "DRAW_UNIT_DECK":
            legal_actions.append(
                AltAction(
                    action_name="DRAW_UNIT_DECK", 
                    player_idx=player_idx,
                )
            )
        
        elif action_spec.action_name == "CLAIM_POINT":
            for point in action_spec.points:
                legal_actions.append(
                    AltAction(
                        action_name="CLAIM_POINT",
                        player_idx=player_idx,
                        point_uuid=str(point.point_uuid),
                        unit_combo=point.default_combo,  # Placeholder, should be filled with actual logic
                    )
                )

    return legal_actions


@dispatch(State, RandoPolicy)
def getnextaction(s, policy):
    player_idx = gettoplay(s)[0]
    legal_actions = getlegalactionspecsforplayer(s, player_idx, None, None)
    action_spec = legal_actions[s.rng.randint(0, len(legal_actions) - 1)]

    if action_spec.action_name == "ROUTE_DISCARD":
        return AltAction(
            action_name="ROUTE_DISCARD", 
            player_idx=player_idx,
            return_route_cards=[0],
        )
    
    if action_spec.action_name == "DRAW_UNIT_FACEUP":
        draw_faceup_spot_num = 1
        return AltAction(
            action_name="DRAW_UNIT_FACEUP", 
            player_idx=player_idx,
            draw_faceup_unit_card_num=s.faceup_spots[draw_faceup_spot_num-1],
            draw_faceup_spot_num=draw_faceup_spot_num,
        )

    if action_spec.action_name == "DRAW_UNIT_DECK":
        return AltAction(
            action_name="DRAW_UNIT_DECK", 
            player_idx=player_idx,
        )
    
    if action_spec.action_name == "CLAIM_POINT":
        point = action_spec.points[s.rng.randint(0, len(action_spec.points) - 1)]
        return AltAction(
            action_name="CLAIM_POINT",
            player_idx=player_idx,
            point_uuid=str(point.point_uuid),
            unit_combo=point.default_combo,
        )
    
    return None


@dispatch(State, int)
def getplayerstate(s, player_idx):
    return PlayerState(
        public=getpublicstate(s), 
        private=getprivatestate(s, player_idx),
    )


def getpublicplayerscore(s, player_score):
    print("*****************321 player_score: ", player_score)
    if s.terminal:
        # Join the arrays of public and private items
        items = player_score.public_items + player_score.private_items
    else:
        # Just public items
        items = player_score.public_items
    total = sum(item.amount for item in items)
    return PublicPlayerScore(
        items=items,
        total=total,
    )


def getprivateplayerscore(s, player_score):
    items = player_score.private_items
    total = sum(item.amount for item in items)
    return PrivatePlayerScore(
        items=items,
        total=total,
    )


def getpublictoplay(s):
    player_idxs = [legal_action.player_idx for legal_action in s.legal_actions_2]
    # filter out duplicates
    return list(set(player_idxs))


def get_max_allotted_times(s):
    return [
        get_player_max_allotted_time(s, player_idx) 
        for player_idx in range(s.game_config.num_players)
    ]


def get_player_max_allotted_time(s, player_idx):
    max_alotted_seconds = 0
    since_action_idx_of_max = -1
    for legal_action in s.legal_actions_2:
        if legal_action.player_idx == player_idx:
            if legal_action.allotted_seconds > max_alotted_seconds:
                max_alotted_seconds = legal_action.allotted_seconds
                since_action_idx_of_max = legal_action.allotted_since_action_idx
    if max_alotted_seconds:
        return AllottedTime(
            seconds=max_alotted_seconds,
            since_action_idx=since_action_idx_of_max,
        )
    return None


@dispatch(State)
def getpublicstate(s):
    return PublicState(
        game_started_at=s.game_config.started_at,
        allotted_times=get_max_allotted_times(s),
        all_pieces=list(s.pieceuuid2piece.values()),
        to_play_2=getpublictoplay(s),
        bonus_statuses=s.bonus_statuses,
        starting_decks=s.starting_decks,
        starting_piles=s.starting_piles,
        history=[action.get_public(s) for action in s.history],
        player_scores=[getpublicplayerscore(s, player_score) for player_score in s.player_scores],
        player_graphs=s.player_graphs,
        goals=s.goals,
        nodes=s.nodes,
        edges=s.edges,
        regions=s.regions,
        decks=[getpublicdeck(s, deck) for deck in s.decks],
        piles=s.piles,
        player_idxs=s.player_idxs,
        game_idx=len(s.action_history),
        initial_to_play=s.initial_to_play,
        action_history=s.action_history,
        to_play=gettoplay(s),
        unit_discards=list(s.unit_discards),
        num_route_cards=len(s.route_cards),
        num_route_discards=len(s.route_discards),
        num_unit_cards=len(s.unit_cards),
        num_unit_discards=len(s.unit_discards),
        faceup_spots=list(s.faceup_spots),
        most_clusters_player_idxs=s.most_clusters_player_idxs,
        players=[getpublicplayer(s, p) for p in s.players],
        player_hands=[getpublicplayerinfo(s, p) for p in s.player_hands],
        last_to_play=s.last_to_play,
        longest_road_player_idxs=s.longest_road_player_idxs,
        winners=s.winners,
        terminal=s.terminal,
        captured_points=getcapturedpoints(s),
        captured_segments=getcapturedsegments(s),
    )


@dispatch(State, Deck)
def getpublicdeck(s, d):
    return PublicDeck(
        idx=d.idx,
        uuid=d.uuid,
        units=d.units,
        facedown_stack_len=len(d.facedown_stack),
        discard_len=len(d.discard),
        faceup_spots=d.faceup_spots,
    )


@dispatch(State, Player)
def getpublicplayer(s, p):
    deck_counts = [0 for _ in s.game_config.fig.board_config.deks]
    for card in p.cards:
        deck_counts[s.carduuid2card[card].deck_idx] += 1
    piece_template_counts = [0 for _ in s.game_config.fig.board_config.piece_templates]
    for piece_uuid in p.pieces:
        piece_template_counts[s.pieceuuid2piece[piece_uuid].piece_template_idx] += 1
    return PublicPlayer(
        idx=p.idx,
        pieces=p.pieces,
        deck_counts=deck_counts,
        piece_template_counts=piece_template_counts,
    )


@dispatch(State, PlayerInfo)
def getpublicplayerinfo(s, p):
    # if s.terminal
    #     route_statuses = getroutestatuses(p)
    # else
    #     route_statuses = []
    # end
    return PublicPlayerInfo(
        final_score=p.final_score,
        longest_road=p.longest_road,
        longest_road_len=p.longest_road_len,
        num_pieces=p.num_pieces,
        num_route_cards=len(p.route_cards),
        num_new_route_cards=len(p.new_route_cards),
        num_unit_cards=len(p.unit_cards),
        paths=p.paths,
        points=p.points,
        tokens=p.tokens,
        route_statuses=[], # TODO: implement!
        score=getpublicscore(s, p.player_idx),
        num_point_pieces=p.num_point_pieces,
        completed_clusters=p.completed_clusters,
    )


# Implementing the following Julia function:
# function getpublicscore(s::State, player_idx::Int)
#     addends = Int[]
    
#     if getsettingvalue(s, :path_scoring)
#         (; path_scores) = s.fig
#         path_lens = getplayerpathlens(s, player_idx)
#         if isempty(path_lens)
#             return 0
#         end
#         push!(addends, sum(map(len -> path_scores[len], path_lens)))
#     end

#     if getsettingvalue(s, :cluster_scoring)
#         (; clusters) = s.fig.board_config
#         uuid2cluster = Dict((x.uuid, x) for x in clusters)
#         (; completed_clusters) = s.player_hands[player_idx]
#         cluster_scores = map(completed_clusters) do cluster_uuid
#             uuid2cluster[cluster_uuid].score
#         end
#         if !isempty(cluster_scores)
#             push!(addends, sum(cluster_scores))
#         end
#     end

#     sum(addends)
# end
def getpublicscore(s, player_idx):
    addends = []
    if getsettingvalue(s, 'path_scoring'):
        path_lens = getplayerpathlens(s, player_idx)
        if not path_lens:
            return 0
        addends.append(sum(s.game_config.fig.path_scores[len] for len in path_lens))
    
    if getsettingvalue(s, 'cluster_scoring'):
        clusters = s.game_config.fig.board_config.clusters
        uuid2cluster = {x.uuid: x for x in clusters}
        completed_clusters = s.player_hands[player_idx].completed_clusters
        cluster_scores = [uuid2cluster[cluster_uuid].score for cluster_uuid in completed_clusters]
        if cluster_scores:
            addends.append(sum(cluster_scores))
    
    return sum(addends)


# Implementing the following Julia function:
# function getplayerpathlens(s::State, player_idx::Int)
#     getpathlens(s)[getplayerpathidxs(s, player_idx)]
# end
def getplayerpathlens(s, player_idx):
    path_lens = getpathlens(s)
    player_path_idxs = getplayerpathidxs(s, player_idx)
    return [path_lens[idx] for idx in player_path_idxs]


# Implementing the following Julia function:
# getpathlens(s::State) = length.(getfield.(getfield.(s.fig.board_config.board_paths, :path), :segments))
def getpathlens(s):
    return [len(p.path.segments) for p in s.game_config.fig.board_config.board_paths]

# Implementing the following Julia function:
# function getplayerpathidxs(s::State, player_idx::Int)
#     s.player_hands[player_idx].paths
# end
def getplayerpathidxs(s, player_idx):
    return s.player_hands[player_idx].paths


# Implementing the following Julia function:
# getlastaction(s::State) = isempty(s.actions) ? nothing : s.actions[end]
def getlastaction(s):
    if not s.action_history:
        return None
    return s.action_history[-1]


# Function implements the following Julia function:
# function getlastactionkey(s)
#     last_action = getlastaction(s)
#     if isnothing(last_action)
#         return nothing
#     end
#     Val(Symbol(last_action.action_name))
# end
@dispatch(State)
def getlastactiontype(s):
    last_action = getlastaction(s)
    if last_action is None:
        return NoAction()
    return getactiontype(last_action.action_name)


def getactiontype(action_name):
    match action_name:
        case "ROUTE_DISCARD":
            return RouteDiscardAction()
        case "DRAW_UNIT_DECK":
            return DrawUnitDeckAction()
        case "DRAW_UNIT_FACEUP":
            return DrawUnitFaceupAction()
        case "CLAIM_POINT":
            return ClaimPointAction()
        case "CLAIM_PATH":
            return MovePiecesToPathAction()
    
    return NoAction()


# Function implements the following Julia function:
# getlastplayeridxplus1(s) = mod1(getlastaction(s).player_idx + 1, s.game_config.num_players)
def getlastplayeridxplus1(s):
    last_action = getlastaction(s)
    if last_action is None:
        return 0
    return (last_action.player_idx + 1) % s.game_config.num_players


@dispatch(State)
def gettoplay(s):
    return gettoplay(s, getlastactiontype(s))


@dispatch(State, object)
def gettoplay(s, last_action_type):
    return [getlastplayeridxplus1(s)]


# Implementing the following Julia function:
@dispatch(State, NoAction)
# function gettoplay(s::State, last_action_key::Nothing)
#     if getsettingvalue(s, :action_route_discard)
#         return collect(1:s.game_config.num_players)
#     end
#     [getfirstplayeridx(s.game)]
# end
def gettoplay(s, last_action_type):
    return s.initial_to_play


def getrng(seed):
    rng = random.Random()
    rng.seed(seed)
    return rng


# Implementing the following Julia function:
# getfirstplayeridx(g::Game) = rand(getrng(g), 1:g.num_players)
def getfirstplayeridx(rng, num_players):
    return rng.randint(0, num_players-1)


@dispatch(State, int)
def get_legal_actions(s, player_idx):
    return [a for a in s.legal_actions_2 if a.player_idx == player_idx]


def get_goal_completions(s, player_idx):
    # print("len(get_goals(s, player_idx)): ", len(get_goals(s, player_idx)))
    # print("len(s.history): ", len(s.history))
    # print("player.cards: ", len(s.players[player_idx].cards))
    return [
        GoalCompletion(
            goal_uuid=goal.uuid,
            complete=is_goal_complete(s, goal, player_idx),
        )
        for goal in get_goals(s, player_idx)
    ]


def is_goal_complete(s, goal, player_idx):
    graph = s.player_graphs[player_idx].neighbors
    nodeuuid2idx = {node.uuid: node.idx for node in s.nodes}
    node_idxs = [nodeuuid2idx[node_uuid] for node_uuid in goal.node_uuids]
    if goal.uuid == "d9ef7d75-63d4-4ceb-adce-f889db3c75f0":
        print("goal.uuid: ", goal.uuid)
        print("goal.node_uuids: ", goal.node_uuids)
        print(f"player: {player_idx} goal: ", goal.uuid)
        print("graph: ", graph)
        print("node_idxs: ", node_idxs)
        print("are_nodes_connected(graph, node_idxs): ", are_nodes_connected(graph, node_idxs))
        for node in s.nodes:
            print(f"node: {node}")
    return are_nodes_connected(
        graph,
        node_idxs,
    )


def are_nodes_connected(graph, node_set):
    if len(node_set) == 0:
        raise ValueError("Node set cannot be empty")
    if len(node_set) <= 1:
        return True  # Trivial cases
    
    node_set = set(node_set)  # For faster lookups
    start = next(iter(node_set))  # Pick any starting node
    
    visited = set()
    queue = deque([start])
    visited.add(start)
    
    while queue:
        current = queue.popleft()
        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    # Check if all nodes in the set were visited
    return all(node in visited for node in node_set)


def get_player_graph(s, player_idx):
    nodes = {node.idx: [] for node in s.nodes}
    return nodes


def get_goals(s, player_idx):
    player = s.players[player_idx]
    goaluuid2goal = {goal.uuid: goal for goal in s.goals}
    goal_uuids = [s.carduuid2card[card_uuid].goal_uuid for card_uuid in player.cards if s.carduuid2card[card_uuid].goal_uuid]
    return [
        goaluuid2goal[goal_uuid] for goal_uuid in goal_uuids if goal_uuid in goaluuid2goal
    ]

# @dispatch(AltState, RouteDiscardAction)
# def gettoplay(s, action_type):
#     return [1]


# @dispatch(AltState, DrawUnitDeckAction)
# def gettoplay(s, action_type):
#     return [2]

# Implementing the following Julia function:
# function getlegalactions(s::State, player_idx::Int)
#     # Causal function chain: gettoplay => getlegalactions =>  isterminal
#     if s.terminal
#         return []
#     end
#     if !in(player_idx, gettoplay(s))
#         return []
#     end
#     getlegalactionsforplayer(s::State, player_idx, getrepeatplayerkey(s, player_idx), getlastactionkey(s))
# end
@dispatch(State, int)
def getlegalactionspecs(s, player_idx):
    # Causal function chain: gettoplay => getlegalactions =>  isterminal
    if s.terminal:
        return []
    if player_idx not in gettoplay(s):
        return []
    return getlegalactionspecsforplayer(s, player_idx, getrepeatplayerbooltype(s, player_idx), getlastactiontype(s))

# Implementing the following Julia function:
# function getrepeatplayerkey(s::State, player_idx)
#     last_action = getlastaction(s)
#     if isnothing(last_action)
#         return Val(false)
#     end
#     Val(player_idx == last_action.player_idx)
# end
def getrepeatplayerbooltype(s, player_idx):
    last_action = getlastaction(s)
    if last_action is None:
        return getbooltype(False)
    return getbooltype(player_idx == last_action.player_idx)


def combinations(a, n=None):
    if n is None:
        return chain.from_iterable(itertools_combinations(a, r) for r in range(len(a) + 1))
    return itertools_combinations(a, n)


# def combinations(a, n=None):
#     """
#     Generate combinations from a sequence a.

#     If n is specified, generate all combinations of n elements from a.
#     If n is not specified, generate combinations of all sizes, from 0 to len(a).

#     The function returns an iterator. To collect all combinations into a list,
#     use list(combinations(a, n)).

#     Note: a should be a sequence with a defined length, such as a list or tuple.
#     """
#     if n is None:
#         return itertools.chain.from_iterable(itertools.combinations(a, k) for k in range(len(a)+1))
#     else:
#         return itertools.combinations(a, n)


###
# Causal function chain is:
# gettoplay => getlegalactions => isterminal
#
# So, gettoplay() determines getlegalactions().
# Moreover, if there are no "legal_actions" for "to_play",
# then the state is "terminal".
###

# Implementing the following Julia function:
# function getrouteoptionsets(s::State, player_idx, min_required)
#     num_choices = length(s.player_hands[player_idx].new_route_cards)
#     max_return_size = num_choices - min_required
#     set = collect(1:num_choices)
#     OptionSet.(
#         Set{Int}.(
#             reduce(
#                 vcat,
#                 [collect(combinations(set, n)) for n in 0:max_return_size],
#             )
#         )
#     )
# end
def getrouteoptionsets(s, player_idx, min_required):
    num_choices = len(s.player_hands[player_idx].new_route_cards)
    max_return_size = num_choices - min_required
    choice_set = list(range(num_choices))
    all_combinations = [
        set(comb)
        for n in range(max_return_size + 1)
        for comb in combinations(choice_set, n)
    ]
    return [OptionSet(option_idxs=comb) for comb in all_combinations]



# Implementing the following Julia function:
# function getlegalactionsforplayer(s::State, player_idx, repeat_player, last_action)
#     min_initial_routes = getsettingvalue(s.fig, :min_initial_routes)
#     min_chosen_routes = getsettingvalue(s.fig, :min_chosen_routes)

#     # Initial Route Card Discard
#     if getsettingvalue(s, :action_route_discard) && length(s.action_history) < s.game_config.num_players
#         return [
#             ActionSpec(
#                 player_idx=player_idx, 
#                 action_name=ROUTE_DISCARD,
#                 return_route_option_sets=getrouteoptionsets(s, player_idx, min_initial_routes),
#             )
#         ]
#     end

#     action_specs = ActionSpec[]
#     if getsettingvalue(s, :action_draw_unit_faceup) && !isempty(getvalidspotnums(s))
#         push!(
#             action_specs, 
#             ActionSpec(
#                 player_idx=player_idx, 
#                 action_name=DRAW_UNIT_FACEUP,
#                 draw_faceup_spots=Dict((spot_num, s.faceup_spots[spot_num]) for spot_num in getvalidspotnums(s)),
#             )
#         )
#     end

#     if getsettingvalue(s, :action_draw_route) && (length(s.route_cards) + length(s.route_discards)) >= min_chosen_routes
#         push!(action_specs, ActionSpec(s.fig, player_idx, :DRAW_ROUTE))
#     end

#     if getsettingvalue(s, :action_draw_unit_deck) && (!isempty(s.unit_cards) || !isempty(s.unit_discards))
#         push!(action_specs, ActionSpec(s.fig, player_idx, :DRAW_UNIT_DECK))
#     end

#     if getsettingvalue(s, :action_claim_path)
#         append!(action_specs, getclaimpathactionspecs(s, player_idx))
#     end

#     if getsettingvalue(s.fig, :action_claim_point)
#         append!(action_specs, getclaimpointactionspecs(s, player_idx))
#     end

#     action_specs
# end
@dispatch(State, int, object, object)
def getlegalactionspecsforplayer(s, player_idx, repeat_player, last_action):
    min_initial_routes = getsettingvalue(s, 'min_initial_routes')
    min_chosen_routes = getsettingvalue(s, 'min_chosen_routes')

    # Initial Route Card Discard
    if getsettingvalue(s, 'action_route_discard') and len(s.action_history) < s.game_config.num_players:
        return [
            ActionSpec(
                player_idx=player_idx,
                action_name="ROUTE_DISCARD",
                return_route_option_sets = getrouteoptionsets(s, player_idx, min_initial_routes),
                draw_faceup_spots={},
                points = [],
                paths = [],
            )
        ]

    action_specs = []
    if getsettingvalue(s, 'action_draw_unit_faceup') and s.faceup_spots:
        
        # Convert this Julia to Python:
        # Julia:
        # draw_faceup_spots = Dict((spot_num, s.faceup_spots[spot_num]) for spot_num in getvalidspotnums(s))
        # Python:
        draw_faceup_spots = {spot_num: s.faceup_spots[spot_num-1] for spot_num in getvalidspotnums(s)}
        
        action_specs.append(
            ActionSpec(
                player_idx=player_idx,
                action_name="DRAW_UNIT_FACEUP",
                return_route_option_sets = [],
                draw_faceup_spots=draw_faceup_spots,
                points = [],
                paths = [],
            )
        )

    if getsettingvalue(s, 'action_draw_route') and (len(s.route_cards) + len(s.route_discards)) >= min_chosen_routes:
        action_specs.append(
            AltAction(
                player_idx=player_idx, 
                action_name="DRAW_ROUTE",
                return_route_option_sets = [],
                draw_faceup_spots={},
                points = [],
                paths = [],
            )
        )

    if getsettingvalue(s, 'action_draw_unit_deck') and (s.unit_cards or s.unit_discards):
        action_specs.append(
            ActionSpec(
                player_idx=player_idx, 
                action_name="DRAW_UNIT_DECK",
                return_route_option_sets = [],
                draw_faceup_spots={},
                points = [],
                paths = [],
            )
        )

    if getsettingvalue(s, 'action_claim_path'):
        action_specs.extend(getclaimpathactionspecs(s, player_idx))
        pass

    if getsettingvalue(s, 'action_claim_point'):
        action_specs.extend(getclaimpointactionspecs(s, player_idx))

    return action_specs


# Implementing the following Julia function:
# function getclaimpointactionspecs(s::State, player_idx::Int; log=false)
#     action_specs = ActionSpec[]
#     available_point_statuses = getavailablepoints(s, player_idx)
#     points = map(available_point_statuses) do available_point_status
#         (; uuid, sample_fulfillment) = available_point_status
#         fulfillment_sorted = sample_fulfillment
#         sample_fulfillment = [x.unit_card_num for x in fulfillment_sorted]
#         fulfillment_str = join(sample_fulfillment, "-")
#         PointCombos(uuid, fulfillment_str, sample_fulfillment)
#     end
#     if !isempty(points)
#         push!(
#             action_specs,
#             ActionSpec(
#                 action_name=CLAIM_POINT,
#                 player_idx=player_idx,
#                 points=points,
#             )
#         )
#     end
#     action_specs
# end
def getclaimpointactionspecs(s, player_idx, log=False):
    action_specs = []
    available_point_statuses = getavailablepoints(s, player_idx)
    
    #     points = map(available_point_statuses) do available_point_status
    #         (; uuid, sample_fulfillment) = available_point_status
    #         fulfillment_sorted = sample_fulfillment
    #         sample_fulfillment = [x.unit_card_num for x in fulfillment_sorted]
    #         fulfillment_str = join(sample_fulfillment, "-")
    #         PointCombos(uuid, fulfillment_str, sample_fulfillment)
    #     end

    def process_point_status(available_point_status):
        uuid = available_point_status['uuid']
        sample_fulfillment = available_point_status['sample_fulfillment']
        fulfillment_sorted = sample_fulfillment
        sample_fulfillment = [x['unit_card_num'] for x in fulfillment_sorted]
        fulfillment_str = '-'.join(map(str, sample_fulfillment))
        return PointCombos(
            point_uuid=uuid,
            default_combo=fulfillment_str,
            sample_fulfillment=sample_fulfillment
        )

    point_combos = list(map(process_point_status, available_point_statuses))
    
    if point_combos:
        action_specs.append(
            ActionSpec(
                player_idx=player_idx,
                action_name="CLAIM_POINT",
                return_route_option_sets = [],
                draw_faceup_spots = {},
                points=point_combos,
                paths = [],
            )
        )
    
    return action_specs


# Implementing the following Julia function:
# function getclaimpathactionspecs(s::State, player_idx::Int; log=false)
#     action_specs = ActionSpec[]
#     available_path_statuses = getavailablepaths(s, player_idx)
#     paths = map(available_path_statuses) do available_path_status
#         (; num, sample_fulfillment) = available_path_status
#         fulfillment_sorted = Base.sort(sample_fulfillment; by=x -> x.segment_num)
#         sample_fulfillment = [x.unit_card_num for x in fulfillment_sorted]
#         fulfillment_str = join(sample_fulfillment, "-")
#         PathCombos(num, fulfillment_str, sample_fulfillment)
#     end
#     if !isempty(paths)
#         push!(
#             action_specs,
#             ActionSpec(
#                 action_name=CLAIM_PATH,
#                 player_idx=player_idx,
#                 paths=paths,
#             )
#         )
#     end
#     action_specs
# end
def getclaimpathactionspecs(s, player_idx, log=False):
    action_specs = []
    available_path_statuses = getavailablepathstatuses(s, player_idx)
    
    def process_path_status(available_path_status):
        num = available_path_status.num
        sample_fulfillment = available_path_status.sample_fulfillment
        fulfillment_sorted = sorted(sample_fulfillment, key=lambda x: x.segment_num)
        sample_fulfillment = [x.unit_card_num for x in fulfillment_sorted]
        fulfillment_str = '-'.join(map(str, sample_fulfillment))
        return PathCombos(
            path_idx=(num-1),
            default_combo=fulfillment_str,
            sample_fulfillment=sample_fulfillment
        )

    paths = list(map(process_path_status, available_path_statuses))
    
    if paths:
        action_specs.append(
            ActionSpec(
                player_idx=player_idx,
                action_name="CLAIM_PATH",
                return_route_option_sets = [],
                draw_faceup_spots={},
                points=[],
                paths=paths,
            )
        )
    
    return action_specs


# Implementing the following Julia function:
# function getavailablepaths(s::State, player_num::Int)
#     balance = s.player_hands[player_num].unit_cards
#     path_statuses = map(getpotentialpathnums(s, player_num)) do path_num
#         getpathstatus(s, player_num, path_num)
#     end
#     filter(x -> x.fulfillable, path_statuses)
# end
def getavailablepathstatuses(s, player_num):
    balance = s.player_hands[player_num].unit_cards
    path_statuses = [
        getpathstatus(s, player_num, path_idx)
        for path_idx in getpotentialpathidxs(s, player_num)
    ]
    return list(filter(lambda x: x.fulfillable, path_statuses))


# Implementing the following Julia function:
# function getpotentialpathnums(s::State, player_num::Int)
#     num_pieces = s.player_hands[player_num].num_pieces
#     setdiff(
#         Set(getpathidxs(s.fig, num_pieces)),
#         Set(getunavailablepaths(s, player_num)),
#     ) |> collect
# end
def getpotentialpathidxs(s, player_num):
    num_pieces = s.player_hands[player_num-1].num_pieces
    return list(
        set(getpathidxs(s.game_config.fig, num_pieces)) - set(getunavailablepathidxs(s, player_num))
    )
    # return list(set(getpathidxs(s.fig, num_pieces)) - set(getunavailablepaths(s, player_num)))


# Implementing the following Julia function:
# function getpathidxs(f::Fig, max_pieces::Int)
#     [p.num for p in f.board_config.board_paths if length(p.path.segments) <= max_pieces]
# end
def getpathidxs(fig, max_pieces):
    return [
        (p.num - 1)
        for p in fig.board_config.board_paths
        if len(p.path.segments) <= max_pieces
    ]


# Implementing the following Julia function:
# function getunavailablepaths(s::State, player_idx::Int)
#     link2paths = Dict()
#     path2link = Dict()

#     for board_path in s.fig.board_config.board_paths
#         (; link_num) = board_path
#         if !haskey(link2paths, link_num)
#             link2paths[link_num] = []
#         end
#         push!(link2paths[link_num], board_path.num)
#         path2link[board_path.num] = link_num
#     end

#     multipath_links = [board_link.num for board_link in getmultipathlinks(s.fig)]

#     # TODO: this is fig-specific game logic 
#     # and should be factored out.
#     if s.game.num_players < 4
#         blocking_hands = s.player_hands
#     else
#         blocking_hands = [s.player_hands[player_idx]]
#     end

#     unavailable_links = []
#     for hand in blocking_hands
#         for path_idx in hand.paths
#             link_idx = path2link[path_idx]
#             if in(link_idx, multipath_links)
#                 push!(unavailable_links, link_idx)
#             end
#         end
#     end

#     unavailable_paths = getclaimedpathidxs(s)
#     for link_idx in unavailable_links
#         for peer in link2paths[link_idx]
#             push!(unavailable_paths, peer)
#         end
#     end

#     unavailable_paths |> unique
# end
def getunavailablepathidxs(s, player_idx):
    link2paths = {}
    path2link = {}

    for board_path in s.game_config.fig.board_config.board_paths:
        link_idx = board_path.link_num - 1
        if link_idx not in link2paths:
            link2paths[link_idx] = []
        link2paths[link_idx].append(board_path.num-1)
        path2link[board_path.num-1] = link_idx

    multipath_links = [(board_link.num-1) for board_link in getmultipathlinks(s.game_config.fig)]

    if s.game_config.num_players < 4:
        blocking_hands = s.player_hands
    else:
        blocking_hands = [s.player_hands[player_idx]]

    unavailable_links = []
    for hand in blocking_hands:
        for path_idx in hand.paths:
            link_idx = path2link[path_idx]
            if link_idx in multipath_links:
                unavailable_links.append(link_idx)

    unavailable_paths = getclaimedpathidxs(s)
    for link_idx in unavailable_links:
        unavailable_paths.extend(link2paths[link_idx])

    return list(set(unavailable_paths))


# Implementing the following Julia function:
# function getmultipathlinks(f::Fig)
#     filter(
#         frozen_link->frozen_link.width > 1,
#         f.board_config.links,
#     )
# end
def getmultipathlinks(fig):
    return [
        frozen_link
        for frozen_link in fig.board_config.links
        if frozen_link.width > 1
    ]


# Implementing the following Julia function:
# function prioritysort(fig::Fig, segments::Vector)
#     (; board_config) = fig
#     (; deck_units) = board_config
#     unituuid2deckunit = Dict(x.unit_uuid => x for x in deck_units)
#     to_sort = [OrderedSegment(n, segment) for (n, segment) in enumerate(segments)]
#     function lt(a, b)
#         segment_a = a.segment
#         segment_b = b.segment
#         deck_unit_a = isnothing(segment_a.unit_uuid) ? nothing : unituuid2deckunit[segment_a.unit_uuid]
#         deck_unit_b = isnothing(segment_b.unit_uuid) ? nothing : unituuid2deckunit[segment_b.unit_uuid]
#         if isnothing(deck_unit_a) && isnothing(deck_unit_b)
#             return a.path_segment_num < b.path_segment_num
#         elseif isnothing(deck_unit_a) && !isnothing(deck_unit_b)
#             return true
#         elseif !isnothing(deck_unit_a) && isnothing(deck_unit_b)
#             return false
#         elseif deck_unit_a.is_wild && deck_unit_b.is_wild
#             return a.path_segment_num < b.path_segment_num
#         elseif deck_unit_a.is_wild && !deck_unit_b.is_wild
#             return false
#         elseif !deck_unit_a.is_wild && deck_unit_b.is_wild
#             return true
#         end
#         a.path_segment_num < b.path_segment_num
#     end
#     Base.sort(to_sort; lt=lt, rev=true)
# end
def prioritysort(fig, segments):
    board_config = fig.board_config
    deck_units = board_config.deck_units
    unituuid2deckunit = {x.unit_uuid: x for x in deck_units}
    to_sort = [OrderedSegment(path_segment_num=n, segment=segment) for n, segment in enumerate(segments)]
    
    def lt(a, b):
        segment_a = a.segment
        segment_b = b.segment
        deck_unit_a = unituuid2deckunit.get(segment_a.unit_uuid) if segment_a.unit_uuid else None
        deck_unit_b = unituuid2deckunit.get(segment_b.unit_uuid) if segment_b.unit_uuid else None
        
        if deck_unit_a is None and deck_unit_b is None:
            return a.path_segment_num < b.path_segment_num
        elif deck_unit_a is None and deck_unit_b is not None:
            return True
        elif deck_unit_a is not None and deck_unit_b is None:
            return False
        elif deck_unit_a.is_wild and deck_unit_b.is_wild:
            return a.path_segment_num < b.path_segment_num
        elif deck_unit_a.is_wild and not deck_unit_b.is_wild:
            return False
        elif not deck_unit_a.is_wild and deck_unit_b.is_wild:
            return True
        
        return a.path_segment_num < b.path_segment_num
    
    return sorted(to_sort, key=cmp_to_key(lt), reverse=True)


# Implementing the following Julia function:
# getwildunituuids(f::Fig) = [x.unit_uuid for x in f.board_config.deck_units if x.is_wild]
def getwildunituuids(fig):
    return [x.unit_uuid for x in fig.board_config.deck_units if x.is_wild]

# Implementing the following Julia function:
# getnonwildunituuids(f::Fig) = [x.unit_uuid for x in f.board_config.deck_units if !x.is_wild]
def getnonwildunituuids(fig):
    return [x.unit_uuid for x in fig.board_config.deck_units if not x.is_wild]


# Implementing the following Julia function:
# function getunituuid(f::Fig, card_num::Int)
#     from = 1
#     for deck_unit in f.board_config.deck_units
#         (; quantity, unit_uuid) = deck_unit
#         to = from + quantity - 1
#         if from <= card_num <= to
#             return unit_uuid
#         end
#         from += quantity
#     end
#     throw(ErrorException("unit_uuid not found for card_num $card_num"))
# end
def getunituuid(fig, card_num):
    from_idx = 1
    for deck_unit in fig.board_config.deck_units:
        quantity = deck_unit.quantity
        unit_uuid = deck_unit.unit_uuid
        to = from_idx + quantity - 1
        if from_idx <= card_num <= to:
            return unit_uuid
        from_idx += quantity
    raise ValueError(f"unit_uuid not found for card_num {card_num}")


# Implementing the following Julia function:
# function getclaimedpathidxs(s::State)
#     claimed = []
#     for player_hand in s.player_hands
#         append!(claimed, player_hand.paths)
#     end
#     claimed
# end
def getclaimedpathidxs(s):
    claimed = []
    for player_hand in s.player_hands:
        claimed.extend(player_hand.paths)
    return claimed


# Implementing the following Julia function:
# function getpathstatus(s::State, player_idx, path_num)
#     balance = s.player_hands[player_idx].unit_cards
#     (; fig) = s
#     (; board_config) = fig
#     (; deck_units, board_paths) = board_config
#     unituuid2deckunit = Dict(x.unit_uuid => x for x in deck_units)
#     path = board_paths[path_num]
#     ordered_segments = prioritysort(fig, path.path.segments)
#     fulfillment = OrderedFullfillment[]
#     wild_unit_uuids = getwildunituuids(fig)
#     # @show wild_unit_uuids
#     non_wild_unit_uuids = getnonwildunituuids(fig)
#     # @show non_wild_unit_uuids

#     # @show balance

#     balance_unituuid2deckcardnums = Dict()
#     for deck_card_num in balance
#         unit_uuid = getunituuid(fig, deck_card_num)
#         if !haskey(balance_unituuid2deckcardnums, unit_uuid)
#             balance_unituuid2deckcardnums[unit_uuid] = []
#         end
#         push!(balance_unituuid2deckcardnums[unit_uuid], deck_card_num)
#     end

#     # @show balance_unituuid2deckcardnums

#     function hasexactunitmatch(unit_uuid)
#         (
#             haskey(balance_unituuid2deckcardnums, unit_uuid) &&
#             length(balance_unituuid2deckcardnums[unit_uuid]) > 0
#         )
#     end

#     function anywildsleft()
#         for wild_unit_uuid in wild_unit_uuids
#             if haskey(balance_unituuid2deckcardnums, wild_unit_uuid)
#                 if !isempty(balance_unituuid2deckcardnums[wild_unit_uuid])
#                     return true
#                 end
#             end
#         end
#         false
#     end

#     function gettotalwildcount()
#         count = 0
#         for wild_unit_uuid in wild_unit_uuids
#             if haskey(balance_unituuid2deckcardnums, wild_unit_uuid)
#                 count += length(balance_unituuid2deckcardnums[wild_unit_uuid])
#             end
#         end
#         count
#     end

#     function popawildcard!()
#         for wild_unit_uuid in wild_unit_uuids
#             if haskey(balance_unituuid2deckcardnums, wild_unit_uuid)
#                 if !isempty(balance_unituuid2deckcardnums[wild_unit_uuid])
#                     return pop!(balance_unituuid2deckcardnums[wild_unit_uuid])
#                 end
#             end
#         end
#         nothing
#     end

#     function getnonemptywildstack()
#         for wild_unit_uuid in wild_unit_uuids
#             if haskey(balance_unituuid2deckcardnums, wild_unit_uuid)
#                 if !isempty(balance_unituuid2deckcardnums[wild_unit_uuid])
#                     return balance_unituuid2deckcardnums[wild_unit_uuid]
#                 end
#             end
#         end
#         nothing
#     end

#     function getlargestnonwildstack()
#         largest_non_wild_unit_uuid = nothing
#         largest_found = 0
#         for non_wild_unit_uuid in non_wild_unit_uuids
#             if haskey(balance_unituuid2deckcardnums, non_wild_unit_uuid)
#                 curr_length = length(balance_unituuid2deckcardnums[non_wild_unit_uuid])
#                 if curr_length > largest_found
#                     largest_found = curr_length
#                     largest_non_wild_unit_uuid = non_wild_unit_uuid
#                 end
#             end
#         end
#         if !isnothing(largest_non_wild_unit_uuid)
#             return balance_unituuid2deckcardnums[largest_non_wild_unit_uuid]
#         end
#         nothing
#     end

#     for ordered_segment in ordered_segments
#         target_segment = ordered_segment.segment
#         segment_num = ordered_segment.path_segment_num
#         (; unit_uuid) = target_segment
#         # @show unit_uuid
#         # @show keys(unituuid2deckunit)
#         target_unit = isnothing(unit_uuid) ? nothing : unituuid2deckunit[unit_uuid]
#         # @show target_unit

#         if isnothing(target_unit)
#             # do nothing (this is a blank segment)
#         elseif target_unit.is_wild
#             if hasexactunitmatch(unit_uuid)
#                 popped = pop!(balance_unituuid2deckcardnums[unit_uuid])
#                 push!(fulfillment, OrderedFullfillment(segment_num, popped))
#             end
#         else
#             # @show 3
#             if hasexactunitmatch(unit_uuid)
#                 # @show 4
#                 popped = pop!(balance_unituuid2deckcardnums[unit_uuid])
#                 push!(fulfillment, OrderedFullfillment(segment_num, popped))
#             elseif anywildsleft()
#                 # @show 5
#                 non_empty_wild_stack = getnonemptywildstack()
#                 popped = pop!(non_empty_wild_stack)
#                 push!(fulfillment, OrderedFullfillment(segment_num, popped))
#             end
#         end
#     end

#     blank_remaining_segments = filter(
#         ordered_segment -> isblank(ordered_segment.segment.unit_uuid),
#         ordered_segments,
#     )
#     # @show blank_remaining_segments
#     largest_non_wild_stack = getlargestnonwildstack()
#     # @show largest_non_wild_stack
#     for blank_remaining_segment in blank_remaining_segments
#         if !isnothing(largest_non_wild_stack) && !isempty(largest_non_wild_stack)
#             popped = pop!(largest_non_wild_stack)
#             push!(fulfillment, OrderedFullfillment(blank_remaining_segment.path_segment_num, popped))
#         elseif gettotalwildcount() > 0
#             popped = popawildcard!()
#             push!(fulfillment, OrderedFullfillment(blank_remaining_segment.path_segment_num, popped))
#         end
#     end

#     # @show fulfillment
#     deepq_edges = map(ordered_segments) do ordered_segment
#         (; path_segment_num) = ordered_segment
#         (; segment) = ordered_segment
#         fullfillable_by_me = in(path_segment_num, [x.segment_num for x in fulfillment])
#         captured_by_me = in(path_num, s.player_hands[player_idx].paths)
#         captured_by_other = !captured_by_me && in(path_num, getclaimedpathidxs(s))
#         available_to_me = !(captured_by_me || captured_by_other) && fullfillable_by_me
#         status = "Other"
#         if captured_by_me
#             status = "CapturedByMe"
#         elseif captured_by_other
#             status = "CapturedByOther"
#         elseif available_to_me
#             status = "AvailableToMe" 
#         end
#         SegmentStatus(
#             path_num,
#             path_segment_num,
#             captured_by_me,
#             captured_by_other,
#             available_to_me,
#             status,
#             segment,
#         )
#     end

#     fulfillable = Base.all([x.available_to_me for x in deepq_edges])
#     PathStatus(path_num, fulfillable, deepq_edges, fulfillment)
# end
def getpathstatus(s, player_idx, path_idx):
    path_num = path_idx + 1
    balance = s.player_hands[player_idx].unit_cards
    fig = s.game_config.fig
    board_config = fig.board_config
    deck_units = board_config.deck_units
    board_paths = board_config.board_paths
    unituuid2deckunit = {x.unit_uuid: x for x in deck_units}
    path = board_paths[path_idx]
    ordered_segments = prioritysort(fig, path.path.segments)
    fulfillment = []
    wild_unit_uuids = getwildunituuids(fig)
    non_wild_unit_uuids = getnonwildunituuids(fig)

    balance_unituuid2deckcardnums = {}

    for deck_card_num in balance:
        unit_uuid = getunituuid(fig, deck_card_num)
        if unit_uuid not in balance_unituuid2deckcardnums:
            balance_unituuid2deckcardnums[unit_uuid] = []
        balance_unituuid2deckcardnums[unit_uuid].append(deck_card_num)

    def hasexactunitmatch(unit_uuid):
        # print("unit_uuid: ", unit_uuid)
        # print("balance_unituuid2deckcardnums: ", balance_unituuid2deckcardnums)
        print("")
        return (
            unit_uuid in balance_unituuid2deckcardnums and
            len(balance_unituuid2deckcardnums[unit_uuid]) > 0
        )

    def anywildsleft():
        for wild_unit_uuid in wild_unit_uuids:
            if wild_unit_uuid in balance_unituuid2deckcardnums:
                if balance_unituuid2deckcardnums[wild_unit_uuid]:
                    return True
        return False

    def gettotalwildcount():
        count = 0
        for wild_unit_uuid in wild_unit_uuids:
            if wild_unit_uuid in balance_unituuid2deckcardnums:
                count += len(balance_unituuid2deckcardnums[wild_unit_uuid])
        return count

    def popawildcard():
        for wild_unit_uuid in wild_unit_uuids:
            if wild_unit_uuid in balance_unituuid2deckcardnums:
                if balance_unituuid2deckcardnums[wild_unit_uuid]:
                    return balance_unituuid2deckcardnums[wild_unit_uuid].pop()
        return None

    def getnonemptywildstack():
        for wild_unit_uuid in wild_unit_uuids:
            if wild_unit_uuid in balance_unituuid2deckcardnums:
                if balance_unituuid2deckcardnums[wild_unit_uuid]:
                    return balance_unituuid2deckcardnums[wild_unit_uuid]
        return None

    def getlargestnonwildstack():
        largest_non_wild_unit_uuid = None
        largest_found = 0
        for non_wild_unit_uuid in non_wild_unit_uuids:
            if non_wild_unit_uuid in balance_unituuid2deckcardnums:
                curr_length = len(balance_unituuid2deckcardnums[non_wild_unit_uuid])
                if curr_length > largest_found:
                    largest_found = curr_length
                    largest_non_wild_unit_uuid = non_wild_unit_uuid
        if largest_non_wild_unit_uuid is not None:
            return balance_unituuid2deckcardnums[largest_non_wild_unit_uuid]
        return None
    
    for ordered_segment in ordered_segments:
        target_segment = ordered_segment.segment
        segment_num = ordered_segment.path_segment_num
        unit_uuid = target_segment.unit_uuid
        target_unit = None if unit_uuid is None else unituuid2deckunit[unit_uuid]

        if target_unit is None:
            # do nothing (this is a blank segment)
            pass
        elif target_unit.is_wild:
            if hasexactunitmatch(unit_uuid):
                popped = balance_unituuid2deckcardnums[unit_uuid].pop()
                fulfillment.append(OrderedFullfillment(segment_num=segment_num, unit_card_num=popped))
        else:
            # print("anywildsleft(): ", anywildsleft())
            if hasexactunitmatch(unit_uuid):
                popped = balance_unituuid2deckcardnums[unit_uuid].pop()
                fulfillment.append(OrderedFullfillment(segment_num=segment_num, unit_card_num=popped))
            elif anywildsleft():
                non_empty_wild_stack = getnonemptywildstack()
                popped = non_empty_wild_stack.pop()
                fulfillment.append(OrderedFullfillment(segment_num=segment_num, unit_card_num=popped))
            # @show 5
    
    blank_remaining_segments = list(filter(
        lambda ordered_segment: ordered_segment.segment.unit_uuid is None,
        ordered_segments,
    ))

    largest_non_wild_stack = getlargestnonwildstack()

    for blank_remaining_segment in blank_remaining_segments:
        if largest_non_wild_stack is not None and largest_non_wild_stack:
            popped = largest_non_wild_stack.pop()
            fulfillment.append(OrderedFullfillment(segment_num=blank_remaining_segment.path_segment_num, unit_card_num=popped))
        elif gettotalwildcount() > 0:
            popped = popawildcard()
            fulfillment.append(OrderedFullfillment(segment_num=blank_remaining_segment.path_segment_num, unit_card_num=popped))
    
    # Implementing the following Julia code:
    # deepq_edges = map(ordered_segments) do ordered_segment
    #     (; path_segment_num) = ordered_segment
    #     (; segment) = ordered_segment
    #     fullfillable_by_me = in(path_segment_num, [x.segment_num for x in fulfillment])
    #     captured_by_me = in(path_num, s.player_hands[player_idx].paths)
    #     captured_by_other = !captured_by_me && in(path_num, getclaimedpathidxs(s))
    #     available_to_me = !(captured_by_me || captured_by_other) && fullfillable_by_me
    #     status = "Other"
    #     if captured_by_me
    #         status = "CapturedByMe"
    #     elseif captured_by_other
    #         status = "CapturedByOther"
    #     elseif available_to_me
    #         status = "AvailableToMe" 
    #     end
    #     SegmentStatus(
    #         path_num,
    #         path_segment_num,
    #         captured_by_me,
    #         captured_by_other,
    #         available_to_me,
    #         status,
    #         segment,
    #     )
    # end
    # fulfillable = Base.all([x.available_to_me for x in deepq_edges])
    # PathStatus(path_num, fulfillable, deepq_edges, fulfillment)
    deepq_edges = []
    for ordered_segment in ordered_segments:
        path_segment_num = ordered_segment.path_segment_num
        segment = ordered_segment.segment
        fullfillable_by_me = path_segment_num in [x.segment_num for x in fulfillment]
        captured_by_me = path_idx in s.player_hands[player_idx].paths
        captured_by_other = not captured_by_me and path_idx in getclaimedpathidxs(s)
        available_to_me = not (captured_by_me or captured_by_other) and fullfillable_by_me
        status = "Other"
        if captured_by_me:
            status = "CapturedByMe"
        elif captured_by_other:
            status = "CapturedByOther"
        elif available_to_me:
            status = "AvailableToMe"
        
        deepq_edges.append(
            SegmentStatus(
                path_idx=path_idx,
                path_num=path_num,
                path_segment_num=path_segment_num,
                captured_by_me=captured_by_me,
                captured_by_other=captured_by_other,
                available_to_me=available_to_me,
                status=status,
                segment=segment
            )
        )
    
    fulfillable = all([x.available_to_me for x in deepq_edges])
    return PathStatus(
        idx=path_idx,
        num=path_num,
        fulfillable=fulfillable,
        segment_statuses=deepq_edges,
        sample_fulfillment=fulfillment
    )


# Implementing the following Julia function:
# function getavailablepoints(s::State, player_num::Int)
#     point_statuses = map(getpotentialpointuuids(s, player_num)) do point_uuid
#         getpointstatus(s, player_num, point_uuid)
#     end
#     sort(filter(x -> x.fulfillable, point_statuses); by=x -> x.uuid)
# end
def getavailablepoints(s, player_num):
    point_statuses = [
        getpointstatus(s, player_num, point_uuid)
        for point_uuid in getpotentialpointuuids(s, player_num)
    ]
    return sorted(
        filter(lambda x: x['fulfillable'], point_statuses),
        key=lambda x: x['uuid']
    )

# Implementing the following Julia function:
# function getpointstatus(s::State, player_idx::Int, point_uuid::UUID)
#     balance = s.player_hands[player_idx].unit_cards
#     fulfillment = OrderedPointFullfillment[]
#     if !isempty(balance)
#         push!(fulfillment, OrderedPointFullfillment(balance[1]))
#     end
#     PointStatus(point_uuid, true, fulfillment)
# end
def getpointstatus(s, player_idx, point_uuid):
    balance = s.player_hands[player_idx].unit_cards
    fulfillment = []
    if balance:
        fulfillment.append({'unit_card_num': balance[0]})
    return {
        'uuid': point_uuid,
        'fulfillable': True,
        'sample_fulfillment': fulfillment
    }

# Implementing the following Julia function:
# function getpotentialpointuuids(s::State, player_num::Int)
#     (; num_point_pieces) = s.player_hands[player_num]
#     setdiff(
#         Set(getnodeuuids(s.fig, num_point_pieces)),
#         Set(getunavailablepoints(s)),
#     ) |> collect
# end
def getpotentialpointuuids(s, player_num):
    num_point_pieces = s.player_hands[player_num].num_point_pieces
    return list(
        set(getnodeuuids(s.game_config.fig, num_point_pieces)) -
        set(getunavailablepoints(s))
    )

# Implementing the following Julia function:
# function getnodeuuids(f::Fig, remaining_pieces::Int)
#     point_capture_unit_count = getsettingvalue(f, :point_capture_unit_count)
#     if point_capture_unit_count <= remaining_pieces
#         return [p.uuid for p in f.board_config.points]
#     end
#     []
# end
def getnodeuuids(f, remaining_pieces):
    point_capture_unit_count = getsettingvalue(f, 'point_capture_unit_count')
    # print(f"f.board_config: ", f.board_config)
    # print(f"f.board_config: ", f.board_config.points)
    if point_capture_unit_count <= remaining_pieces:
        return [p.uuid for p in f.board_config.points]
    return []


# Implementing the following Julia function:
# function getunavailablepoints(s::State)
#     unavailable_points = []
#     for hand in s.player_hands
#         for point_uuid in hand.points
#             push!(unavailable_points, point_uuid)
#         end
#     end
#     unavailable_points
# end
def getunavailablepoints(s):
    unavailable_points = []
    for hand in s.player_hands:
        for point_uuid in hand.points:
            unavailable_points.append(point_uuid)
    return unavailable_points


def getstateidx(s):
    return len(s.action_history)



# Implementing the following Julia function:
# function calcfinalscores(s::State)
#     if !s.terminal
#         return s
#     end
#     @reset s.player_hands = calcfinalscore.(s, s.player_hands)
#     s
# end
@dispatch(State)
def calcfinalscores(s):
    if not s.terminal:
        return s
    return s.set(player_hands=pvector([calcfinalscore(s, h) for h in s.player_hands]))


# Implementing the following Julia function:
# function calcfinalscore(s::State, hand::PlayerInfo)
#     (; total, breakdown) = getprivatescore(s, hand)
#     @reset hand.final_score = PlayerScore(total, breakdown)
#     hand
# end
@dispatch(State, PlayerInfo)
def calcfinalscore(s, hand):
    total, breakdown = getprivatescore(s, hand)
    return hand.set(final_score=PlayerScore(total=total, breakdown=breakdown))


# Implementing the following Julia function:
# function calcwinners(s::State)
#     if !s.terminal
#         return s
#     end
#     s = calcfinalscores(s)
#     player_scores = [p.final_score for p in s.player_hands]
#     max_score = maximum([p.total for p in player_scores])
#     @reset s.winners = [h.player_idx for h in s.player_hands if h.final_score.total == max_score]
#     s
# end
@dispatch(State)
def calcwinners(s):
    if not s.terminal:
        return s
    s = calcfinalscores(s)
    player_scores = [p.final_score for p in s.player_hands]
    max_score = max([p.total for p in player_scores])
    winners = [h.player_idx for h in s.player_hands if h.final_score.total == max_score]
    return s.set(winners=winners)


def printplayer(s, player_idx):
    hand = s.player_hands[player_idx]
    legal_actions = getlegalactionspecs(s, player_idx)
    print(f"~~~~~~~~~~~~ P{player_idx} ~~~~~~~~~~~~")
    print(f"private score:     {getprivatescore(s, hand)}")
    print(f"public score:       {getpublicscore(s, player_idx)}")
    print(f"completed clusters: {list(str(c) for c in hand.completed_clusters)}")
    print(f"units:              {list(hand.unit_cards)}")
    if getsettingvalue(s, "route_scoring"):
        print(f"routes:            {list(hand.route_cards)} choices:{list(hand.new_route_cards)}")
    print(f"captured points:    {list(str(p) for p in hand.points)}")
    print(f"legal actions:      {list(a.action_name for a in legal_actions)}")


def printstate(s):
    state_idx = getstateidx(s)
    print(f"*************** State {state_idx} ***************")
    print(f"Most clusters:   {list(s.most_clusters_player_idxs)}")
    print(f"Last to play:    {s.last_to_play}")
    print(f"Winners:         {list(s.winners)}")
    print(f"Route Deck:      {list(s.route_cards)}")
    print(f"Route Disc:      {list(s.route_discards)}")
    print(f"Unit Deck:       ...{list(s.unit_cards[60:])}")
    print(f"Unit Disc:       {list(s.unit_discards)}")
    print(f"FaceUp:          {list(s.faceup_spots)}")
    print(f"ToPlay:          {gettoplay(s)}")
    print(f"Terminal:        {s.terminal}")
    
    for i in range(s.game_config.num_players):
        printplayer(s, i)
    print(f"****************************************\n")


def printaction(a, i):
    print(f"\n\n*************** Action {i} ***************")
    print(f"{a}")
    print(f"****************************************\n\n\n")


# Implementing the following Julia function:
# function getprivatescore(s::State, hand::PlayerInfo; bonus=true)
#     player_idx = hand.player_idx
#     breakdown = []

#     # Path scores
#     if getsettingvalue(s, :path_scoring)
#         (; path_scores) = s.fig
#         for len in getplayerpathlens(s, player_idx)
#             push!(
#                 breakdown, 
#                 ScoreItem(
#                     code_idx=getscorecodeidx(s.fig, :PATH),
#                     amount=path_scores[len],
#                 )
#             )
#         end
#     end
    
#     # Bonus: most clusters
#     if getsettingvalue(s, :most_clusters_bonus)
#         bonus_most_clusters_score = getsettingvalue(s.fig, :bonus_most_clusters_score)
#         if in(player_idx, s.most_clusters_player_idxs)
#             push!(
#                 breakdown, 
#                 ScoreItem(
#                     code_idx=getscorecodeidx(s.fig, :MOST_CLUSTERS),
#                     amount=bonus_most_clusters_score,
#                 )
#             )
#         end
#     end

#     # Longest road
#     if !getsettingvalue(s, :disable_longest_path_bonus)
#         longest_path_score = getsettingvalue(s.fig, :longest_path_score)
#         if in(player_idx, s.longest_road_player_idxs)
#             push!(
#                 breakdown, 
#                 ScoreItem(
#                     code_idx=getscorecodeidx(s.fig, :LONGEST_ROAD),
#                     amount=longest_path_score,
#                 )
#             )
#         end
#     end
    
#     # Completed routes
#     if getsettingvalue(s, :route_scoring)
#         hand = s.player_hands[player_idx]
#         (; board_config) = s.fig
#         (; routes) = board_config
#         for route_idx in hand.route_cards
#             route_score = routes[route_idx].score
#             amount = in(route_idx, hand.completed_routes) ? route_score : -1*route_score
#             push!(
#                 breakdown, 
#                 ScoreItem(
#                     code_idx=getscorecodeidx(s.fig, :ROUTE),
#                     amount=amount
#                 )
#             )
#         end
#     end

#     # Completed clusters
#     if getsettingvalue(s, :cluster_scoring)
#         (; clusters) = s.fig.board_config
#         uuid2cluster = Dict((x.uuid, x) for x in clusters)
#         (; completed_clusters) = s.player_hands[player_idx]
#         cluster_scores = map(completed_clusters) do cluster_uuid
#             uuid2cluster[cluster_uuid].score
#         end
#         if !isempty(cluster_scores)
#             push!(breakdown, 
#                 ScoreItem(
#                     code_idx=getscorecodeidx(s.fig, :CLUSTER),
#                     amount=sum(cluster_scores)
#                 )
#             )
#         end
#     end

#     amounts = [item.amount for item in breakdown]
#     total = sum(amounts; init=0)
#     (
#         total=total,
#         breakdown=breakdown,
#     )
# end
@dispatch(State, PlayerInfo)
def getprivatescore(s, hand):
    player_idx = hand.player_idx
    breakdown = []

    # Path scores
    if getsettingvalue(s, 'path_scoring'):
        path_scores = s.game_config.fig.path_scores
        for len in getplayerpathlens(s, player_idx):
            breakdown.append(ScoreItem(
                code_idx=getscorecodeidx(s.game_config.fig, 'PATH'),
                amount=path_scores[len],
            ))

    # Bonus: most clusters
    if getsettingvalue(s, 'most_clusters_bonus'):
        bonus_most_clusters_score = getsettingvalue(s.game_config.fig, 'bonus_most_clusters_score')
        if player_idx in s.most_clusters_player_idxs:
            breakdown.append(ScoreItem(
                code_idx=getscorecodeidx(s.game_config.fig, 'MOST_CLUSTERS'),
                amount=bonus_most_clusters_score,
            ))

    # Longest road
    if not getsettingvalue(s, 'disable_longest_path_bonus'):
        longest_path_score = getsettingvalue(s.game_config.fig, 'longest_path_score')
        if player_idx in s.longest_road_player_idxs:
            breakdown.append(ScoreItem(
                code_idx=getscorecodeidx(s.game_config.fig, 'LONGEST_ROAD'),
                amount=longest_path_score,
            ))

    # Completed routes
    if False and getsettingvalue(s, 'route_scoring'):
        routes = s.game_config.fig.board_config.routes
        for route_idx in hand.route_cards:
            route_score = routes[route_idx].score
            amount = route_score if route_idx in hand.completed_routes else -1 * route_score
            breakdown.append(ScoreItem(
                code_idx=getscorecodeidx(s.game_config.fig, 'ROUTE'),
                amount=amount
            ))

    # Completed clusters
    if getsettingvalue(s, 'cluster_scoring'):
        clusters = s.game_config.fig.board_config.clusters
        uuid2cluster = {x.uuid: x for x in clusters}
        completed_clusters = hand.completed_clusters
        cluster_scores = [uuid2cluster[cluster_uuid].score for cluster_uuid in completed_clusters]
        if cluster_scores:
            breakdown.append(ScoreItem(
                code_idx=getscorecodeidx(s.game_config.fig, 'CLUSTER'),
                amount=sum(cluster_scores)
            ))

    amounts = [item.amount for item in breakdown]
    total = sum(amounts)
    return total, breakdown


# Implementing the following Julia function:
# getprivatescore(s::State, player_idx::Int; bonus=true) = getprivatescore(s, s.player_hands[player_idx]; bonus=bonus)
@dispatch(State, int)
def getprivatescore(s, player_idx):
    return getprivatescore(s, s.player_hands[player_idx])


# Implementing the following Julia function:
# function getscorecodeidx(f::Fig, score_code::Symbol)
#     findfirst(
#         isequal(string(score_code)),
#         getscorecodes(f),
#     )
# end
def getscorecodeidx(f, score_code):
    return getscorecodes(f).index(score_code)


# Implementing the following Julia function:
# function getscorecodes(f::Fig)
#     score_codes = ["PATH", "ROUTE", "CLUSTER"]
#     disable_longest_path_bonus = getsettingvalue(f, :disable_longest_path_bonus)
#     if !disable_longest_path_bonus
#         push!(score_codes, "LONGEST_ROAD", "MOST_CLUSTERS")
#     end
#     score_codes
# end
# # TODO: this list needs to be remove, totally unnecessary.
def getscorecodes(f):
    score_codes = ["PATH", "ROUTE", "CLUSTER"]
    disable_longest_path_bonus = getsettingvalue(f, 'disable_longest_path_bonus')
    if not disable_longest_path_bonus:
        score_codes.extend(["LONGEST_ROAD", "MOST_CLUSTERS"])
    return score_codes


# Implementing the following Julia function:
# function assertunitcardsaccountedfor(s::State) 
#     total_num_unit_cards = gettotaldeckcards(s.fig)
#     total_found = getunitcardstotalfound(s)
#     @assert total_num_unit_cards == total_found "Unit cards not accounted for. $(total_num_unit_cards) != $(total_found)"
# end
def assertunitcardsaccountedfor(s):
    total_num_unit_cards = gettotaldeckcards(s.game_config.fig)
    total_found = getunitcardstotalfound(s)
    assert total_num_unit_cards == total_found, f"Unit cards not accounted for. {total_num_unit_cards} != {total_found}"


# Implementing the following Julia function:
# function getunitcardstotalfound(s::State)
#     num_player_unit_cards = sum(gettotalnumunitcards.(s.player_hands))
#     total_found = sum([
#         num_player_unit_cards,
#         length(s.unit_discards),
#         length(s.unit_cards),
#         length(getvalidspotnums(s)),
#     ])
#     total_found
# end
def getunitcardstotalfound(s):
    num_player_unit_cards = sum(gettotalnumunitcards(p) for p in s.player_hands)
    total_found = sum([
        num_player_unit_cards,
        len(s.unit_discards),
        len(s.unit_cards),
        len(getvalidspotnums(s)),
    ])
    return total_found


# Implementing the following Julia function:
# gettotalnumunitcards(player_hand::PlayerInfo) = length(player_hand.unit_cards)
def gettotalnumunitcards(player_hand):
    return len(player_hand.unit_cards)


# Implementing the following Julia function:
# function getvalidspotnums(s::State)
#     filter(n -> !isnothing(s.faceup_spots[n]), 1:length(s.faceup_spots))
# end
def getvalidspotnums(s):
    return [n for n in range(1, len(s.faceup_spots) + 1) if s.faceup_spots[n-1] is not None]


# Implementing the following Julia function:
# function assertroutecardsaccountedfor(s::State)
#     total_num_route_cards = getnumroutecards(s.fig)
#     num_player_route_cards = sum(gettotalnumroutecards.(s.player_hands))
#     total_found = sum([
#         num_player_route_cards, 
#         length(s.route_discards), 
#         length(s.route_cards),
#     ])
#     @assert total_num_route_cards == total_found "Route cards not accounted for. $(total_num_route_cards) != $(total_found)"
# end
def assertroutecardsaccountedfor(s):
    total_num_route_cards = getnumroutecards(s.game_config.fig)
    num_player_route_cards = sum(gettotalnumroutecards(p) for p in s.player_hands)
    total_found = sum([
        num_player_route_cards, 
        len(s.route_discards), 
        len(s.route_cards),
    ])
    assert total_num_route_cards == total_found, f"Route cards not accounted for. {total_num_route_cards} != {total_found}"


# Implementing the following Julia function:
# gettotalnumroutecards(player_hand::PlayerInfo) = length(player_hand.route_cards) + length(player_hand.new_route_cards)
def gettotalnumroutecards(player_hand):
    return len(player_hand.route_cards) + len(player_hand.new_route_cards)


# Implementing the following Julia function:
# function assertallcardsaccountedfor(s::State)
#     assertroutecardsaccountedfor(s)
#     assertunitcardsaccountedfor(s)
# end
def assertallcardsaccountedfor(s):
    assertroutecardsaccountedfor(s)
    assertunitcardsaccountedfor(s)


# Implementing the following Julia function:
# function getlegalactions(s::State)
#     getlegalactions(s, gettoplay(s))
# end
@dispatch(State)
def getlegalactionspecs(s):
    return getlegalactionspecs(s, gettoplay(s))


# Implementing the following Julia function:
# function getlegalactions(s::State, player_idxs::Vector{Int})
#     legal_actions = []
#     for player_idx in player_idxs
#         append!(legal_actions, getlegalactions(s, player_idx))
#     end
#     legal_actions
# end
@dispatch(State, list)
def getlegalactionspecs(s, player_idxs):
    legal_actions = []
    for player_idx in player_idxs:
        legal_actions.extend(getlegalactionspecs(s, player_idx))
    return legal_actions


# Implementing the following Julia function:
# function getcapturedsegments(s::State)
#     (; fig) = s
#     (; board_config) = fig
#     public_player_hands = PublicPlayerInfo.(s, s.player_hands)
#     (; board_paths) = board_config
#     captured_segments = CapturedSegment[]
#     for (player_num, player_hand) in enumerate(public_player_hands)
#         for path_num in player_hand.paths
#             link_path = board_paths[path_num].path
#             for segment in link_path.segments
#                 captured_segment = CapturedSegment(
#                     player_num,
#                     segment.uuid,
#                 )
#                 push!(captured_segments, captured_segment)
#             end
#         end
#     end
#     captured_segments
# end
@dispatch(State)
def getcapturedsegments(s):
    public_player_hands = [getpublicplayerinfo(s, p) for p in s.player_hands]
    board_paths = s.game_config.fig.board_config.board_paths
    captured_segments = []
    for player_idx, player_hand in enumerate(public_player_hands):
        for path_idx in player_hand.paths:
            link_path = board_paths[path_idx].path
            for segment in link_path.segments:
                captured_segment = CapturedSegment(
                    player_num=(player_idx+1),
                    segment_uuid=segment.uuid,
                )
                captured_segments.append(captured_segment)
    return captured_segments


# Implementing the following Julia function:
# function getcapturedpoints(s::State)
#     (; fig) = s
#     public_player_hands = PublicPlayerInfo.(s, s.player_hands)
#     captured_points = CapturedPoint[]
#     for (player_num, player_hand) in enumerate(public_player_hands)
#         for point_uuid in player_hand.points
#             captured_point = CapturedPoint(
#                 player_num,
#                 point_uuid,
#             )
#             push!(captured_points, captured_point)
#         end
#     end
#     captured_points
# end
@dispatch(State)
def getcapturedpoints(s):
    public_player_hands = [getpublicplayerinfo(s, p) for p in s.player_hands]
    captured_points = []
    for player_idx, player_hand in enumerate(public_player_hands):
        for point_uuid in player_hand.points:
            captured_point = CapturedPoint(
                player_num=player_idx+1,
                point_uuid=point_uuid,
            )
            captured_points.append(captured_point)
    return captured_points


def json_serializer(obj):
    if isinstance(obj, set):
        return list(obj)
    elif hasattr(obj, '__todict__'):
        return obj.__todict__()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


@dispatch(str, str, Fig, int, int)
def initgameconfig(uuid, started_at, fig, num_players, seed):
    return GameConfig(
        uuid=uuid,
        started_at=started_at,
        fig=fig, 
        num_players=num_players, 
        seed=seed,
    )


def rng2json(rng):
    """Convert a random.Random instance to a JSON string."""
    rng_state = rng.getstate()
    return json.dumps({"state": [rng_state[0], list(rng_state[1]), rng_state[2]]})


def json2rng(json_str):
    """Reconstruct a random.Random instance from a JSON string."""
    data = json.loads(json_str)
    state_data = data["state"]
    
    # Create a new Random instance
    rng = random.Random()
    
    # Convert the middle part back to tuple of integers
    state = (state_data[0], tuple(state_data[1]), state_data[2])
    
    # Set the state
    rng.setstate(state)
    
    return rng


# Implementing the following Julia function:
# function getprivatestate(s::State, player_idx::Int)
#     legal_actions = getlegalactions(s, player_idx)
#     PrivateState(
#         getpublicstate(s),
#         legal_actions,
#         getsegmentstatuses(s, player_idx),
#         s.player_hands[player_idx],
#     )
# end
@dispatch(State, int)
def getprivatestate(s, player_idx):
    legal_actions = getlegalactionspecs(s, player_idx)
    goal_completions = get_goal_completions(s, player_idx)
    return PrivateState(
        player_score=getprivateplayerscore(s, s.player_scores[player_idx]),
        player=s.players[player_idx],
        legal_actions_2 = get_legal_actions(s, player_idx),
        legal_actions=legal_actions,
        hand=s.player_hands[player_idx],
        goal_completions=goal_completions,
    )


# Implement the following Julia function
# function getqvaluetrajectories(g::Game)
#     curr_state = getinitialstate(g)
#     states = State[]
#     scores = [Int[] for _ in 1:(length(g.actions)+1)]
#     action_player_nums = Vector{Int}(undef, length(g.actions)) 
#     q_values = Vector{Int}(undef, length(g.actions))
#     formula_q_idxs = Vector{Union{Nothing,Int}}(nothing, length(g.actions))
#     formula_score_diffs = Vector{Tuple{Int,Int}}(undef, length(g.actions))
#     for (i,action) in enumerate(g.actions)
#         push!(states, curr_state)
#         scores[i] = map(1:g.num_players) do player_num
#             getprivatescore(curr_state, player_num; bonus=true).total
#         end
#         action_player_nums[i] = action.player_idx
#         curr_state = getnextstate(curr_state, action)
#     end
#     scores[end] = map(1:g.num_players) do player_num
#         getprivatescore(curr_state, player_num; bonus=true).total
#     end
#     for player_num in 1:g.num_players
#         player_action_idxs = findall(isequal(player_num), action_player_nums)
#         player_action_idxs_plus_terminal_idx = [player_action_idxs..., length(scores)]
#         scores_at_player_action_idxs = [x[player_num] for x in scores[player_action_idxs_plus_terminal_idx]]
#         q_values_at_player_action_idxs = reverse(cumsum(-diff(reverse(scores_at_player_action_idxs))))
#         q_values[player_action_idxs] = q_values_at_player_action_idxs
#         formula_q_idxs[player_action_idxs[1:end-1]] .= player_action_idxs[2:end]
#         formula_score_diffs[player_action_idxs] .= map(enumerate(player_action_idxs_plus_terminal_idx[1:end-1])) do (i,idx)
#             (player_action_idxs_plus_terminal_idx[i+1], idx)
#         end
#     end
#     formulas = map(zip(formula_q_idxs, formula_score_diffs)) do (formula_q_idx, formula_score_diff)
#         QValueFormula((q_num=formula_q_idx, score_diff=formula_score_diff))
#     end
#     QValueTrajectories(scores, q_values, formulas, states, g.actions)
#     # for player_idx in 1:g.num_players
#     # end
#     # -diff([110,10,0,0])
#     # cumsum([100,10,0])
# end
@dispatch(GameConfig, list)
def get_qvalue_trajectories(game_config, actions):
    curr_state = getinitialstate(game_config)
    states = []
    scores = np.array([list([0] * game_config.num_players) for _ in range(len(actions) + 1)])
    action_player_idxs = [None] * len(actions)
    q_values = [None] * len(actions)
    formula_q_idxs = np.array([None] * len(actions))
    formula_score_diffs = np.array([None] * len(actions))

    for i, action in enumerate(actions):
        states.append(curr_state)
        scores[i] = list([getprivatescore(curr_state, player_idx)[0] for player_idx in range(game_config.num_players)])
        action_player_idxs[i] = action.player_idx
        curr_state = getnextstate(curr_state, action)

    scores[-1] = np.array([getprivatescore(curr_state, player_idx)[0] for player_idx in range(game_config.num_players)])

    for player_idx in range(game_config.num_players):
        player_action_idxs = [i for i, x in enumerate(action_player_idxs) if x == player_idx]

        player_action_idxs_plus_terminal_idx = player_action_idxs + [len(scores) - 1]
        scores_at_player_action_idxs = [x[player_idx] for x in scores[player_action_idxs_plus_terminal_idx]]
        q_values_at_player_action_idxs = np.flip(
            np.cumsum((-1 * np.diff(np.flip(np.array(scores_at_player_action_idxs)))))
        )

        for idx, action_idx in enumerate(player_action_idxs):
            q_values[action_idx] = q_values_at_player_action_idxs[idx].item()

        formula_q_idxs[player_action_idxs[:-1]] = player_action_idxs[1:]

        formula_score_diffs[player_action_idxs] = [
            (player_action_idxs_plus_terminal_idx[i+1], idx)
            for i, idx in enumerate(player_action_idxs_plus_terminal_idx[:-1])
        ]

    formulas = [
        QValueFormula(q_num=formula_q_idx, score_diff=ScoreDiff(a=formula_score_diff[0], b=formula_score_diff[1]))
        for formula_q_idx, formula_score_diff in zip(formula_q_idxs, formula_score_diffs)
    ]

    return QValueTrajectories(scores=scores.tolist(), q_values=q_values, formulas=formulas, states_no_terminal=states, actions=actions)


@dispatch(str, str, str, int, int, list)
def get_qvalue_trajectories(logged_game_uuid, started_at, static_board_config_uuid, board_config_json, num_players, seed, actions):
    game_config = initgameconfig(logged_game_uuid, started_at, static_board_config_uuid, board_config_json, num_players, seed)
    return get_qvalue_trajectories(game_config, actions)


@dispatch(str, str, str, int, int)
def initgameconfig(logged_game_uuid, started_at, static_board_config_uuid, board_config_json, num_players, seed):
    board_config = FrozenBoardConfig.__fromdict__(json.loads(board_config_json))
    return initgameconfig(
        logged_game_uuid, 
        started_at,
        initfig(static_board_config_uuid, board_config),
        num_players, 
        seed,
    )


# Implementing the following Julia function:
# diff(A::AbstractVector)
# diff(A::AbstractArray; dims::Integer)

#   Finite difference operator on a vector or a multidimensional array A. In the latter case the dimension to operate on needs to be specified with the dims keyword argument.

#   │ Julia 1.1
#   │
#   │  diff for arrays with dimension higher than 2 requires at least Julia 1.1.

#   Examples
#   ≡≡≡≡≡≡≡≡

#   julia> a = [2 4; 6 16]
#   2×2 Matrix{Int64}:
#    2   4
#    6  16
  
#   julia> diff(a, dims=2)
#   2×1 Matrix{Int64}:
#     2
#    10
  
#   julia> diff(vec(a))
#   3-element Vector{Int64}:
#     4
#    -2
#    12
def diff(A, dims=None):
    if dims is None:
        # For 1D arrays, return the difference between consecutive elements
        return [A[i] - A[i - 1] for i in range(1, len(A))]
    else:
        # For 2D arrays, compute the difference along the specified dimension
        if dims == 1:
            return [[A[i][j] - A[i - 1][j] for j in range(len(A[0]))] for i in range(1, len(A))]
        elif dims == 2:
            return [[A[i][j] - A[i][j - 1] for j in range(1, len(A[0]))] for i in range(len(A))]
        else:
            raise ValueError("dims must be either 1 or 2")
        

@dispatch(StaticBoardConfig, PlayerState)
def get_imagined_state(static_board_config, player_state):
    board_config = static_board_config.board_config
    public_state = player_state.public
    private_state = player_state.private
    my_hand = private_state.hand

    fig = initfig("af472d67-05ec-4b5d-9eb7-6b0cea9eec5a", board_config)
    seed = 4012489341 # TODO: this should be random (or if non-stochastic, loaded from the net.seed)
    rng = getrng(seed)

    # TODO: this needs to come from x_json['game_config']
    game_config = GameConfig(
        uuid = str(generate_uuid_with_rng(rng)),
        started_at = "2025-01-01 00:00:00",
        num_players = 2, 
        fig = fig,
        seed = seed     
    )

    possible_route_card_idxs = list(range(getnumroutecards(fig)))
    possible_unit_card_idxs = list(range(gettotaldeckcards(fig)))

    def remove_card_idx(to_mutate, card_idx):
        if card_idx in to_mutate:
            to_mutate.remove(card_idx)

    def remove_card_idxs(to_mutate, card_idxs):
        for card_idx in card_idxs:
            remove_card_idx(to_mutate, card_idx)

    
    imagined_route_card_idxs = rng.sample(possible_route_card_idxs, public_state.num_route_cards)
    remove_card_idxs(possible_route_card_idxs, imagined_route_card_idxs)
    imagined_route_discard_idxs = rng.sample(possible_route_card_idxs, public_state.num_route_discards)
    remove_card_idxs(possible_route_card_idxs, imagined_route_discard_idxs)

    imagined_route_cards = [x+1 for x in imagined_route_card_idxs]
    imagined_route_discards = [x+1 for x in imagined_route_discard_idxs]

    for unit_card in public_state.unit_discards:
        remove_card_idx(possible_unit_card_idxs, unit_card-1)

    for unit_card in my_hand.unit_cards:
        remove_card_idx(possible_unit_card_idxs, unit_card-1)

    for action in public_state.action_history:
        if action.action_name == "DRAW_UNIT_DECK":
            remove_card_idx(possible_unit_card_idxs, action.unit_card_num - 1)

    imagined_unit_card_idxs = rng.sample(possible_unit_card_idxs, public_state.num_unit_cards)
    imagined_unit_cards = [x+1 for x in imagined_unit_card_idxs]
    remove_card_idxs(possible_unit_card_idxs, imagined_unit_card_idxs)


    imagined_player_hands = []

    for (player_idx, public_player_info) in enumerate(public_state.player_hands):
        if player_idx == my_hand.player_idx:
            imagined_player_hands.append(PlayerInfo.clone(my_hand))
        else:
            imagined_player_unit_card_idxs = rng.sample(possible_unit_card_idxs, public_player_info.num_unit_cards)
            imagined_player_unit_cards = [x+1 for x in imagined_player_unit_card_idxs]
            remove_card_idxs(possible_unit_card_idxs, imagined_player_unit_card_idxs)
            imagined_player_route_card_idxs = rng.sample(possible_route_card_idxs, public_player_info.num_route_cards)
            remove_card_idxs(possible_route_card_idxs, imagined_player_route_card_idxs)
            imagined_player_new_route_card_idxs = rng.sample(possible_route_card_idxs, public_player_info.num_new_route_cards)
            remove_card_idxs(possible_route_card_idxs, imagined_player_new_route_card_idxs)
            imagined_player_route_cards = [x+1 for x in imagined_player_route_card_idxs]
            imagined_player_new_route_cards = [x+1 for x in imagined_player_new_route_card_idxs]
            imagined_player_hands.append(
                PlayerInfo(
                    fig = fig,
                    player_idx = player_idx,
                    new_route_cards = pvector(imagined_player_new_route_cards), # Guess at this.
                    route_cards = pvector(imagined_player_route_cards), # Guess at this.
                    unit_cards = pvector(imagined_player_unit_cards), # Guess at this.
                    completed_routes = [], # Guess at this.
                    completed_clusters = public_player_info.completed_clusters,
                    paths = public_player_info.paths,
                    points = public_player_info.points,
                    tokens = public_player_info.tokens,
                    num_pieces = public_player_info.num_pieces,
                    num_point_pieces = public_player_info.num_point_pieces,
                    longest_road = public_player_info.longest_road,
                    longest_road_len = public_player_info.longest_road_len,
                    final_score = public_player_info.final_score,
                )
            )


    nodeuuid2idx = {node.uuid: idx for idx, node in enumerate(board_config.points)}
    edges = get_edges(board_config, nodeuuid2idx)
    edgeuuid2idx = {edge.uuid: idx for idx, edge in enumerate(edges)}
    edgetuple2uuid = {}
    for edge in edges:
        node_1_idx = nodeuuid2idx[edge.node_1_uuid]
        node_2_idx = nodeuuid2idx[edge.node_2_uuid]
        edge_tuple = (min(node_1_idx, node_2_idx), max(node_1_idx, node_2_idx))
        edgetuple2uuid[edge_tuple] = edge.uuid
    
    return State(
        final_scores = None,
        player_graphs = [],
        nodes = get_nodes(board_config),
        nodeuuid2idx = nodeuuid2idx,
        edges = get_edges(board_config, nodeuuid2idx),
        edgeuuid2idx = edgeuuid2idx,
        edgetuple2uuid = edgetuple2uuid,
        regions = get_regions(board_config),
        legal_actions = [],  # TODO: Should use PublicState, but empty for now.
        piles = [], # TODO: Should use PublicState, but empty for now.
        players = [], # TODO: Should use PublicState, but empty for now.
        player_idxs = public_state.player_idxs,
        decks = [], # TODO: Should use PublicState, but empty for now.
        game_config = game_config,
        rng = rng, # TODO: again figure out this stochasticity
        terminal = public_state.terminal,
        initial_to_play = public_state.initial_to_play,
        action_history = public_state.action_history,
        route_cards = pvector(imagined_route_cards), # Guess at this.
        route_discards = pvector(imagined_route_discards), # Guess at this.
        player_hands = pvector(imagined_player_hands), # Guess at this.
        unit_cards = pvector(imagined_unit_cards), # Guess at this.
        faceup_spots = pvector(public_state.faceup_spots),
        unit_discards = pvector(public_state.unit_discards),
        most_clusters_player_idxs = public_state.most_clusters_player_idxs,
        longest_road_player_idxs = public_state.longest_road_player_idxs,
        last_to_play = public_state.last_to_play,
        winners = public_state.winners,
    )

INIT_HOOK_1 = """def handler(game):
    return shuffle_all_decks(game)  
"""
INIT_HOOK_2 = """def handler(game):
    return deal_cards_to_each_player(game, 0, 4)
"""
INIT_HOOK_3 = """def handler(game):
    return deal_cards_to_each_player_discard_tray(game, 1, 3)
"""
INIT_HOOK_4 = """def handler(game):
    return distribute_all_piles(game)
"""
INIT_HOOK_5 = """def handler(game):
    return flip_cards(game, 0, 5)
"""
INIT_HOOK_6 = """def handler(game):
    for player in game.players:
        game = append_to_legal_actions(
            game,
            LegalAction(
                player_idx=player.idx,
                name="INITIAL-GOAL-KEEP",
                instruction="Your move. Please select the routes you want to keep.",
                allotted_seconds=180,
                allotted_since_action_idx=(len(game.history) - 1),
                keep=LegalActionKeep(
                    deck_idx=1,
                    min=2,
                )
            )
        )
    return game
"""
INIT_HOOK_7 = """def handler(game):
    return shuffle_player_order(game)
"""

DEFAULT_LEGAL_ACTIONS_HOOK = """def handler(game, player_idx):
    allotted_seconds = 60
    allotted_since_action_idx = len(game.history) - 1

    game = append_to_legal_actions(
            game,
            LegalAction(
                player_idx=player_idx,
                name="DRAW-GOAL",
                instruction="draw a route",
                allotted_seconds=allotted_seconds,
                allotted_since_action_idx=allotted_since_action_idx,
                draw_discard=LegalActionDrawDiscard(
                    deck_idx=1,
                    quantity=3,
                    min=1,
                )
            )
        )

    game = append_to_legal_actions(
        game,
        LegalAction(
            player_idx=player_idx,
            name="DRAW",
            instruction="draw a unit",
            allotted_seconds=allotted_seconds,
            allotted_since_action_idx=allotted_since_action_idx,
            draw=LegalActionDraw(
                deck_idx=0,
                quantity=1,
            )
        )
    )

    for card_uuid in game.decks[0].faceup_spots:
        game = append_to_legal_actions(
            game,
            LegalAction(
                player_idx=player_idx,
                name="FACEUP-DRAW",
                instruction="draw a faceup unit",
                allotted_seconds=allotted_seconds,
                allotted_since_action_idx=allotted_since_action_idx,
                faceup_draw=LegalActionFaceupDraw(
                    deck_idx=0,
                    card_uuid=card_uuid,
                )
            )
        )

    game = append_all_to_legal_actions(
        game,
        get_legal_actions_for_paths(game, player_idx),
    )
    
    return game
"""

INITIALIZATION_HOOKS = [
    Hook(
        name="SampleHook1",
        uuid="81248263-5cb4-4439-afea-78c01aba3de3",
        when="AFTER_GAME_STARTS",
        code=INIT_HOOK_1,
    ),
    Hook(
        name="SampleHook2",
        uuid="d654d7f6-c2f4-443d-b603-8fa034717830",
        when="AFTER_GAME_STARTS",
        code=INIT_HOOK_2,
    ),
    Hook(
        name="SampleHook3",
        uuid="ffbc3d4a-85c6-461d-9272-0ddeb873f216",
        when="AFTER_GAME_STARTS",
        code=INIT_HOOK_3,
    ),
    Hook(
        name="SampleHook4",
        uuid="e3a9161b-ad27-4166-a013-77ebcd2f75b7",
        when="AFTER_GAME_STARTS",
        code=INIT_HOOK_4,
    ),
    Hook(
        name="SampleHook5",
        uuid="bff1a9e9-90a5-4431-9d41-2b68c5eff55e",
        when="AFTER_GAME_STARTS",
        code=INIT_HOOK_5,
    ),
    Hook(
        name="SampleHook6",
        uuid="e3079338-7eac-4180-979c-69dedbe1eabd",
        when="AFTER_GAME_STARTS",
        code=INIT_HOOK_6,
    ),
    Hook(
        name="SampleHook7",
        uuid="240b8706-7fcf-4d35-9894-276aa10f799f",
        when="AFTER_GAME_STARTS",
        code=INIT_HOOK_7,
    ),
]

HANDLE_ACTION_HOOK_1 = """
def handler(game, action):
    return default_handle_action(game, action)
"""

HANDLE_ACTION_HOOKS = [
    Hook(
        name="SampleHookHandleAction1",
        uuid="11e83980-5a10-43f0-9504-66fe66eebb11",
        when="HANDLE_ACTION",
        code=HANDLE_ACTION_HOOK_1,
    ),
]

AFTER_ACCEPT_ACTION_HOOK_1 = """
def handler(game, action):
    return default_after_accept_action(game, action)
"""

AFTER_ACCEPT_ACTION_HOOKS = [
    Hook(
        name="SampleHookAfterAcceptAction1",
        uuid="3467e35e-f6b6-4b75-aeff-97e4bab47c75",
        when="AFTER_ACCEPT_ACTION",
        code=AFTER_ACCEPT_ACTION_HOOK_1,
    )
]

ACCEPT_ACTION_HOOK_1 = """
def handler(game, action):
    return default_accept_action(game, action)
"""

ACCEPT_ACTION_HOOKS = [
    Hook(
        name="SampleHookAcceptAction1",
        uuid="01b8ce2c-9aa5-44f5-b82f-bc22afeb49ef",
        when="ACCEPT_ACTION",
        code=ACCEPT_ACTION_HOOK_1,
    )
]

EMPTY_LEGAL_ACTIONS_HOOK_1 = """
def handler(game, action):
    if action.legal_action.name == "INITIAL-GOAL-KEEP":
        return append_default_legal_actions_for_initial_player(game, action)
    else:
        return append_default_legal_actions_for_next_player(game, action)
    return game
"""

EMPTY_LEGAL_ACTIONS_HOOKS = [
    Hook(
        name="EmptyLegalActionsHook",
        uuid="f45dabf6-8f46-4af2-9b88-327db8b985eb",
        when="EMPTY_LEGAL_ACTIONS",
        code=EMPTY_LEGAL_ACTIONS_HOOK_1,
    )
]

HANDLE_SCORING_HOOK_1 = """
def handler(game):
    return default_handle_scoring(game)
"""

HANDLE_SCORING_HOOKS = [
    Hook(
        name="SampleHookHandleScoring1",
        uuid="11e83980-5a10-43f0-9504-66fe66eebb11",
        when="HANDLE_SCORING",
        code=HANDLE_SCORING_HOOK_1,
    ),
]

HANDLE_TERMINAL_HOOK_1 = """
def handler(game):
    return default_handle_terminal(game)
"""

HANDLE_TERMINAL_HOOKS = [
    Hook(
        name="SampleHookHandleTerminal1",
        uuid="11e83980-5a10-43f0-9504-66fe66eebb11",
        when="HANDLE_TERMINAL",
        code=HANDLE_TERMINAL_HOOK_1,
    ),
]