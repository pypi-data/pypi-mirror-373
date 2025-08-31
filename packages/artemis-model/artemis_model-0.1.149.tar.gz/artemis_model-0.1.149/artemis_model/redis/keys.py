"""Redis keys."""

KEY_ZONE_PLAY_HISTORY_TEMPLATE = "zone_{zone_id}_play_history"
KEY_ZONE_PUSH_PLAYLIST_BUCKET_TEMPLATE = "zone_{zone_id}_pp_bucket_{timeslot_ts}"
KEY_ZONE_SCHEDULE_BUCKET_TEMPLATE = "zone_{zone_id}_sc_bucket_{timeslot_ts}"
KEY_ZONE_STATE_TEMPLATE = "zone_{zone_id}_state"
KEY_ZONE_ACTIVE_DEVICE_TEMPLATE = "zone_{zone_id}_active_devices"
KEY_ZONE_SKIPPED_TRACKS_TEMPLATE = "zone_{zone_id}_skipped_tracks"


__all__ = [
    "KEY_ZONE_PLAY_HISTORY_TEMPLATE",
    "KEY_ZONE_PUSH_PLAYLIST_BUCKET_TEMPLATE",
    "KEY_ZONE_SCHEDULE_BUCKET_TEMPLATE",
    "KEY_ZONE_STATE_TEMPLATE",
    "KEY_ZONE_ACTIVE_DEVICE_TEMPLATE",
]
