# Website changes — 16 October 2026, v11

The guides follow the completed iOS v97-sync1 and server v96-view2 sources.

- Direct explanations of setup, recording, live views, saved workouts and cloud analysis.
- Core and Advanced choices organized by Oar, GPS, Time, Boat and Body.
- Current metrics and curves, including horizontal sweep and boat motion. Check metrics use the normal Boat category and selectors.
- Speed check and Distance check use relative boat motion from the phone. Energy-loss check uses the GPS/IMU fused-speed V² model.
- Current plot, grouping, map and replay controls, plus saved view setups that can be used with a different workout.
- Clear separation between a new upload and re-running the same workout.
- A fresh example generated from the original DAT oar, GPS and phone-motion files using the current server pipeline.

The welcome page retains its existing color, video and images. Setup guides retain useful assembly and connection illustrations. Pricing and the custom domain are unchanged.

The example uses the public Core and Advanced choices. Technical diagnostics and magnetic features are excluded from the public pages and example controls.

## Edit the guides later

Edit the individual HTML guide files, then rebuild `index.html` so its embedded pages match them:

```
python3 -m pip install -r tools/requirements.txt
python3 tools/rebuild_site.py
python3 tools/validate_site.py
```

The standalone guide URLs and the combined site's navigation remain supported.
