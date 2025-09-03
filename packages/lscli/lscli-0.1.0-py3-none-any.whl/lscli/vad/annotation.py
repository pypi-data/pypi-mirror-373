import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd
from label_studio_sdk import LabelStudio
from tqdm import tqdm
from yarl import URL


def upload_and_annotation(input_dir: Path):
    bar = tqdm(input_dir.glob("**/*.wav"), desc="Uploading and annotating")
    for audio_path in bar:
        csv_path = audio_path.with_suffix(".csv")


def annotation(
    client: LabelStudio,
    annotation_id: int,
    label_data: List[Dict],
):
    client.annotations.create(
        id=annotation_id,
        ground_truth=True,
        result=label_data,
        was_cancelled=False,
    )


def to_seconds(x):
    t = datetime.strptime(x, "%M:%S.%f")
    return t.minute * 60 + t.second + t.microsecond / 1e6


def annotation_df(
    client: LabelStudio,
    annotation_id: int,
    df: pd.DataFrame,
):
    starts = df["Start"].apply(to_seconds).to_numpy()
    durations = df["Duration"].apply(to_seconds).to_numpy()
    ends = starts + durations
    label_data = [
        {
            "id": f"annotation_{i}",
            "from_name": "label",
            "to_name": "audio",
            "type": "labels",
            "value": {
                "start": start,
                "end": end,
                "labels": ["speech"],
            },
        }
        for i, (start, end) in enumerate(zip(starts, ends))
    ]
    annotation(client, annotation_id, label_data)

