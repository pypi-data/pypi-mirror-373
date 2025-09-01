from pathlib import Path
import autonomous_proto
from rosbags.highlevel import AnyReader
import numpy as np

def get_matched_control_vehicle_state(bag: Path):
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

def get_matched_k(data: list[tuple[autonomous_proto.Control, autonomous_proto.VehicleState]]):
    c = []
    v = []
    t = []
    t0 = data[0][1].header.info.timestamp * 1e-9
    for control, vehicle_state in data:
        c.append(control.k[0])
        v.append(vehicle_state.k[0])
        t.append(vehicle_state.header.info.timestamp * 1e-9 - t0)
    c = np.array(c)
    v = np.array(v)
    t = np.array(t)
    return c, v, t
