# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel
from ..file_info import FileInfo
from ..version_info import VersionInfo
from ..extract_configuration import ExtractConfiguration
from ..extract_output_response import ExtractOutputResponse

__all__ = ["ExtractGetResponse"]


class ExtractGetResponse(BaseModel):
    configuration: ExtractConfiguration

    created_at: datetime
    """The date and time when the task was created and queued."""

    file_info: FileInfo
    """Information about the input file."""

    message: str
    """A message describing the task's status or any errors that occurred."""

    status: Literal["Starting", "Processing", "Succeeded", "Failed", "Cancelled"]
    """The status of the task."""

    task_id: str
    """The unique identifier for the task."""

    task_type: Literal["Parse", "Extract"]

    version_info: VersionInfo
    """Version information for the task."""

    expires_at: Optional[datetime] = None
    """The date and time when the task will expire."""

    finished_at: Optional[datetime] = None
    """The date and time when the task was finished."""

    input_file_url: Optional[str] = None
    """The presigned URL of the input file. Deprecated use `file_info.url` instead."""

    output: Optional[ExtractOutputResponse] = None
    """The processed results of a document extraction task.

    Shapes:

    - `results`: JSON matching the user-provided schema.
    - `citations`: mirror of `results`; only leaf positions (primitive or
      array-of-primitives) contain a `Vec<Citation>` supporting that field.
    - `metrics`: mirror of `results`; only leaf positions contain a `Metrics` object
      for that field.

    Detailed shape:

    - Shared structure: `results`, `citations`, and `metrics` have the same
      object/array shape as the user schema. Non-leaf nodes (objects, arrays of
      objects) are mirrored; only leaves carry values.
    - Leaf definition:
      - A leaf is either a JSON primitive (string, number, bool, or null) or an
        array of primitives (including empty).
      - Arrays of objects are not leaves; recurse into their elements (`items`
        mirror index-by-index).
    - Null handling:
      - If a leaf in `results` is null, the corresponding position in `citations`
        and `metrics` remains null.
    - Arrays:
      - Array of objects: `citations`/`metrics` are arrays whose elements mirror
        each object and carry values at their own leaves.
      - Array of primitives: treated as a single leaf. `citations[path]` is a list
        of `Citation` supporting the array as a whole. `metrics[path]` is a
        `Metrics` object for the array as a whole.
    - Citations leaves:
      - Type: JSON array of `Citation` objects.
      - Each `Citation` has: `citation_id: string`, `citation_type: Segment|Word`,
        `bbox: BoundingBox[]`, `content: string`, `segment_id?: string`,
        `segment_type: SegmentType`, `ss_range?: string[]`.
        - Segment citation: represents a full parsed segment; `segment_id` set,
          `bbox` has one entry (segment box), `content` is the segment text. If the
          segment is from a spreadsheet, `ss_range` contains the table range
          (single-element array) or the underlying cell refs if available.
        - Word citation: represents selected OCR words within a segment;
          `segment_id` is null, `bbox` has one entry per word, `content` is the
          whitespace-joined text of those words; `segment_type` is `Text`. If OCR
          words came from spreadsheet cells, `ss_range` lists those cell refs.
    - Metrics leaves:
      - Type: `Metrics` object with `confidence: "High" | "Low"`, indicating whether
        citations sufficiently support the item.

    Example:

    results

    ```json
    {
      "invoice_id": "INV-001",
      "seller": { "name": "Acme" },
      "line_items": [{ "sku": "A1", "qty": 2 }],
      "tags": ["urgent", "paid"],
      "notes": null
    }
    ```

    citations

    ```json
    {
      "invoice_id": [
        {
          "citation_id": "abc1234",
          "citation_type": "Segment",
          "bbox": [{ "left": 10, "top": 20, "width": 100, "height": 18 }],
          "content": "Invoice INV-001",
          "segment_id": "seg_001",
          "segment_type": "Text",
          "ss_range": ["A1:C10"]
        },
        {
          "citation_id": "pqr2345",
          "citation_type": "Word",
          "bbox": [
            { "left": 12, "top": 24, "width": 36, "height": 18 },
            { "left": 52, "top": 24, "width": 48, "height": 18 }
          ],
          "content": "INV-001",
          "segment_id": null,
          "segment_type": "Text",
          "ss_range": ["B3", "C3"]
        }
      ],
      "seller": {
        "name": [
          {
            "citation_id": "def5678",
            "citation_type": "Word",
            "bbox": [
              { "left": 45, "top": 80, "width": 30, "height": 12 },
              { "left": 80, "top": 80, "width": 40, "height": 12 }
            ],
            "content": "Acme",
            "segment_id": null,
            "segment_type": "Text"
          }
        ]
      },
      "line_items": [
        {
          "sku": [
            {
              "citation_id": "ghi9012",
              "citation_type": "Segment",
              "bbox": [{ "left": 12, "top": 140, "width": 60, "height": 16 }],
              "content": "A1",
              "segment_id": "seg_010",
              "segment_type": "Text",
              "ss_range": ["D5:E12"]
            }
          ],
          "qty": [
            {
              "citation_id": "jkl3456",
              "citation_type": "Word",
              "bbox": [{ "left": 85, "top": 140, "width": 12, "height": 16 }],
              "content": "2",
              "segment_id": null,
              "segment_type": "Text",
              "ss_range": ["E12"]
            }
          ]
        }
      ],
      "tags": [
        {
          "citation_id": "mno7890",
          "citation_type": "Segment",
          "bbox": [{ "left": 12, "top": 200, "width": 100, "height": 16 }],
          "content": "urgent paid",
          "segment_id": "seg_020",
          "segment_type": "Text",
          "ss_range": ["A20:C25"]
        }
      ],
      "notes": null
    }
    ```

    metrics

    ```json
    {
      "invoice_id": { "confidence": "High" },
      "seller": { "name": { "confidence": "Low" } },
      "line_items": [
        { "sku": { "confidence": "High" }, "qty": { "confidence": "High" } }
      ],
      "tags": { "confidence": "Low" },
      "notes": null
    }
    ```
    """

    source_task_id: Optional[str] = None
    """The ID of the source `parse` task that was used for extraction"""

    started_at: Optional[datetime] = None
    """The date and time when the task was started."""

    task_url: Optional[str] = None
    """The presigned URL of the task."""
