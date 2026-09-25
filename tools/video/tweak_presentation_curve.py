#!/usr/bin/env python3
"""Widen the illustrative video curve while preserving its observed texture.

Usage: python tweak_presentation_curve.py ORIGINAL_V7_PLOT.json OUTPUT.json
Requires numpy and scipy. Use the original work_v7/plot_data.json, not an
already trimmed website copy. This edits illustration geometry and displayed
metrics only: raw measurements, recorded_* data, roll, feather, speed, twist,
video timing and the separate workout analysis report remain unchanged.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator, CubicHermiteSpline


def falling_crossing(x, y, level):
    indices = np.flatnonzero((x[1:] > 55) & (y[:-1] > level) & (y[1:] <= level))
    if not len(indices):
        raise ValueError(f"No falling crossing at bend {level}")
    i = indices[-1]
    return float(x[i] + (level-y[i])/(y[i+1]-y[i])*(x[i+1]-x[i]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve():
        parser.error("Keep original presentation data separate from the output.")
    original_bytes = args.source.read_bytes()
    p = json.loads(original_bytes)
    baseline = json.loads(original_bytes)
    bend = p["paths"]["bend_display"]
    x, y = np.asarray(bend["angle"], float), np.asarray(bend["values"], float)
    if not np.all(np.diff(x) > 0) or abs(x[-1]-83.18701498985278) > 1e-6:
        parser.error("Expected the original v7 curve ending at 83.1870149899 degrees.")
    metrics, events = p["metrics"], p["metric_events"]
    catch, total, release = metrics["catchMiss"], metrics["totalSweepArc"], metrics["releaseTravel"]
    wash = 5.2
    feather = total-release
    loaded_end, force_zero = feather-wash, 86.5
    half_cross, threshold_cross = falling_crossing(x,y,.5), falling_crossing(x,y,.1)
    source_anchors = np.array([55., half_cross, threshold_cross, x[-1]])
    target_anchors = np.array([55., 80., loaded_end, force_zero])
    slopes = PchipInterpolator(source_anchors,target_anchors).derivative()(source_anchors)
    slopes[0] = 1.0  # C1 join to the completely unchanged earlier curve.
    slopes[-1] = (target_anchors[-1]-target_anchors[-2])/(source_anchors[-1]-source_anchors[-2])  # Keep the small tail tip shallow, not vertical.
    warp = CubicHermiteSpline(source_anchors,target_anchors,slopes)
    dense = np.linspace(55,x[-1],2000)
    if np.any(warp.derivative()(dense) < -1e-10):
        raise ValueError("Tail mapping must stay monotonic")
    new_x = x.copy()
    new_x[x > 55] = warp(x[x > 55])
    new_y = y.copy()
    new_y[-1] = 0.0  # Remove numerical residue at the existing zero endpoint.
    # Insert the exact threshold crossing, preserving every existing amplitude.
    insert_at = int(np.searchsorted(new_x,loaded_end))
    new_x = np.insert(new_x,insert_at,loaded_end)
    new_y = np.insert(new_y,insert_at,.1)
    bend["angle"], bend["values"] = new_x.tolist(), new_y.tolist()
    for key, value in [("phase","drive"),("estimated",False)]:
        if key in bend:
            bend[key].insert(insert_at,value)
    bend["website_widening"] = {
        "source_anchor_angles_deg":source_anchors.tolist(),
        "display_anchor_angles_deg":target_anchors.tolist(),
        "bend_threshold_deg":.1,"loaded_endpoint_deg":loaded_end,
        "force_zero_endpoint_deg":force_zero,
        "method":"Monotone C1 horizontal warp after55 degrees; existing amplitude samples retained; exact0.1-degree threshold point inserted."
    }
    t, a = np.asarray(p["time"],float), np.asarray(p["angle"],float)
    drive = (t >= 0)&(t <= events["finish_time"])
    loaded_time = float(np.interp(loaded_end,a[drive],t[drive]))
    force_zero_time = float(np.interp(force_zero,a[drive],t[drive]))
    feather_time = events["feather_time"]
    values = np.asarray(p["bend_display"],float)
    later_drive = drive&(a > 55)
    values[later_drive] = np.interp(a[later_drive],new_x,new_y,left=0,right=0)
    p["bend_display"] = values.tolist()
    for key in ["bend_draw_mask","bend_visible"]:
        flags = np.asarray(p[key],bool)
        flags[later_drive] = values[later_drive] > 1e-5
        p[key] = flags.tolist()
    original_zero = events["catch_time_original"]
    intervals = {
        "strokeLength":(catch,loaded_end,events["grab_time"],loaded_time),
        "finishWash":(loaded_end,feather,loaded_time,feather_time),
        "releaseTravel":(feather,total,feather_time,events["finish_time"]),
    }
    for key,(lo,hi,lo_t,hi_t) in intervals.items():
        value = wash if key == "finishWash" else hi-lo
        metrics[key] = value
        display = next(q for q in p["display_metrics"] if q["key"] == key)
        display.update(value=value,segment=[lo,hi],reveal_time=hi_t,
                       value_origin="Requested website illustration edit; recorded values retained separately.")
        interval = next(q for q in p["metric_intervals"] if q["key"] == key)
        interval.update(value_deg=value,start_angle_deg=lo,end_angle_deg=hi,
                        start_time=lo_t,end_time=hi_t,reveal_time=hi_t,
                        start_time_original=original_zero+lo_t,
                        end_time_original=original_zero+hi_t,
                        reveal_time_original=original_zero+hi_t)
    for name,value in [("loaded_end_time",loaded_time),("force_zero_time",force_zero_time)]:
        events[name] = value
        events[name+"_original"] = original_zero+value
    events["finish_endpoint_source"] = "illustrated_bend_threshold_0.1"
    events["force_endpoint_source"] = "Illustrated curve reaches0.1 degrees at84.9870149899 degrees; visible force reacheszero at86.5 degrees. Recorded events retained separately."
    events["angle_balance_error_deg"] = sum(metrics[k] for k in ["catchMiss","strokeLength","finishWash","releaseTravel"])-total
    presentation = p["presentation"]
    presentation["display_metrics_changed"] = ["strokeLength","finishWash"]
    presentation["display_metric_policy"] = "Wash starts when displayed bend falls through0.1degrees, while the small positive tail continues to86.5degrees. Feather and release boundaries remain original. Catch+loadedlength+wash+release equals totalarc. Raw and recorded_* data unchanged."
    presentation["website_update"] = {
        "input_original_v7_sha256":hashlib.sha256(original_bytes).hexdigest(),
        "tail":"Widened mainfall after55 degrees by a monotone horizontal warp; short lowpositive tail; no Gaussian blend, filtering or synthetic noise.",
        "source_anchor_angles_deg":source_anchors.tolist(),
        "display_anchor_angles_deg":target_anchors.tolist(),
        "bend_threshold_deg":.1,"loaded_endpoint_deg":loaded_end,
        "force_endpoint_deg":force_zero,"feather_endpoint_deg":feather,
        "wash_deg":wash,"release_deg":release,
        "loaded_end_time":loaded_time,"force_zero_time":force_zero_time,
        "feather_time":feather_time,"physical_raw_sensor_roll_unchanged":True,
        "feather_plot":"Original v7 feather data and path retained exactly.",
    }
    presentation["bend"]["prior_v7_method"] = presentation["bend"]["method"]
    presentation["bend"].update(
        method="Original v7 amplitude samples retained; monotone horizontal widening after55degrees with C1 join.0.1degree bend threshold marks loaded end; actual force zero is distinct.",
        unload_angle_deg=loaded_end,display_unload_time=loaded_time,
        force_zero_angle_deg=force_zero,display_force_zero_time=force_zero_time,
        original_residual_amplitudes_retained=True,
    )
    # Archive superseded v7 geometry rather than leaving stale current metadata.
    presentation["bend"]["prior_v7_tail_geometry"] = {
        key: baseline["presentation"]["bend"][key]
        for key in ["tail_anchor_angles_deg", "tail_anchor_bend_deg", "display_unload_source_frame", "earlier_than_intermediate_planned_endpoint_deg"]
        if key in baseline["presentation"]["bend"]
    }
    presentation["bend"]["tail_anchor_angles_deg"] = target_anchors.tolist()
    presentation["bend"]["tail_anchor_bend_deg"] = [float(np.interp(55,x,y)), .5, .1, 0.]
    presentation["bend"].pop("display_unload_source_frame",None)
    presentation["bend"].pop("earlier_than_intermediate_planned_endpoint_deg",None)
    # Retain the source's original_sample_* metadata arrays and all raw data.
    unchanged_keys = [k for k in baseline if k.startswith("recorded_") or k.startswith("raw_")]
    unchanged_keys += ["bend_raw","water_angle_raw","fused_roll_raw","sensor_roll_from_square","time","time_original","angle","speed","feather_display","shaft_twist","water_angle"]
    for key in unchanged_keys:
        assert p[key] == baseline[key], key
    for key in baseline["paths"]:
        if key != "bend_display":
            assert p["paths"][key] == baseline["paths"][key],key
    assert abs(np.interp(loaded_end,new_x,new_y)-.1) < 1e-12
    assert abs(events["angle_balance_error_deg"]) < 1e-10
    assert loaded_time < force_zero_time < feather_time
    assert np.all(np.diff(new_x) > 0)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(p,separators=(",",":")))
    validation = {"metrics":metrics,"loaded_end_angle_deg":loaded_end,"actual_force_zero_deg":force_zero,
                  "threshold_bend_deg":float(np.interp(loaded_end,new_x,new_y)),
                  "angle_balance_error_deg":events["angle_balance_error_deg"],
                  "raw_and_recorded_fields_preserved":True,"feather_and_other_paths_preserved":True,
                  "earlier_curve_through55deg_preserved":bool(np.array_equal(new_x[new_x<=55],x[x<=55]) and np.array_equal(new_y[new_x<=55],y[x<=55])),
                  "all_original_amplitudes_preserved_except_zero_roundoff":bool(np.allclose(np.delete(new_y,insert_at),y,rtol=0,atol=1e-15)),
                  "force_zero_time":force_zero_time,"loaded_end_time":loaded_time,"feather_time":feather_time}
    args.output.with_suffix(".validation.json").write_text(json.dumps(validation,indent=2))
    print(json.dumps(validation,indent=2))


if __name__ == "__main__":
    main()
