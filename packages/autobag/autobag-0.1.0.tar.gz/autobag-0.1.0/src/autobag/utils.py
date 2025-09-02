from pathlib import Path
import autonomous_proto
import numpy as np
from rosbags.highlevel import AnyReader
import pymap3d as pm

def get_matched_control_vehicle_state_from_bag(bag: Path):
    matched: list[tuple[autonomous_proto.Control, autonomous_proto.VehicleState]] = []
    if not bag.exists():
        raise RuntimeError(f'Bag: {bag} does not exist')
    control_protos: list[autonomous_proto.Control] = []
    vehicle_state_protos: list[autonomous_proto.VehicleState] = []
    with AnyReader([bag.expanduser()]) as reader:
        for connection, t, rawdata in reader.messages():
            if connection.topic == "/control" or connection.topic == "control":
                msg = reader.deserialize(rawdata, connection.msgtype)
                if hasattr(msg, 'data'):
                    control_protos.append(autonomous_proto.Control.FromString(bytes(msg.data)))
            if connection.topic == "/vehicle_state" or connection.topic == "vehicle_state":
                msg = reader.deserialize(rawdata, connection.msgtype)
                if hasattr(msg, 'data'):
                    vehicle_state_protos.append(autonomous_proto.VehicleState.FromString(bytes(msg.data)))
    vs_iter = iter(vehicle_state_protos)
    cur_vs = next(vs_iter, None)
    for control_proto in control_protos:
        for source in control_proto.header.sources:
            if source.topic_name != autonomous_proto.MessageInfoTopicNameValue.vehicle_state:
                continue
            while cur_vs and cur_vs.header.info.count < source.count:
                cur_vs = next(vs_iter, None)
            if cur_vs and cur_vs.header.info.count == source.count:
                matched.append((control_proto, cur_vs))
    return matched

def get_navigation_from_bag(bag: Path):
    if not bag.exists():
        raise RuntimeError(f'Bag: {bag} does not exist')
    nav_protos: list[autonomous_proto.Navigation] = []
    with AnyReader([bag.expanduser()]) as reader:
        for connection, t, rawdata in reader.messages():
            if connection.topic == "/navigation" or connection.topic == "navigation":
                msg = reader.deserialize(rawdata, connection.msgtype)
                if hasattr(msg, 'data'):
                    nav_protos.append(autonomous_proto.Navigation.FromString(bytes(msg.data)))
    return nav_protos

def navigation_list_to_enu(
        navigation_protos: list[autonomous_proto.Navigation],
        origin_llh: tuple[float, float, float] = None,
):
    if len(navigation_protos) == 0:
        return np.empty((0, 2), dtype=np.float64)
    if origin_llh is None:
        origin_nav = navigation_protos[0]
        origin_llh = (origin_nav.position.lat, origin_nav.position.lon, origin_nav.position.alt)
    return np.array([
        pm.geodetic2enu(nav.position.lat, nav.position.lon, nav.position.alt, origin_llh[0], origin_llh[1], origin_llh[2])
        for nav in navigation_protos
    ])
