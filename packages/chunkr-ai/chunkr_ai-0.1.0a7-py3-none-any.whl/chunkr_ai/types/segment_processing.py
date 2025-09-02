# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .generation_config import GenerationConfig

__all__ = ["SegmentProcessing"]


class SegmentProcessing(BaseModel):
    caption: Optional[GenerationConfig] = FieldInfo(alias="Caption", default=None)
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.
    """

    footnote: Optional[GenerationConfig] = FieldInfo(alias="Footnote", default=None)
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.
    """

    formula: Optional[GenerationConfig] = FieldInfo(alias="Formula", default=None)
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.
    """

    list_item: Optional[GenerationConfig] = FieldInfo(alias="ListItem", default=None)
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.
    """

    page: Optional[GenerationConfig] = FieldInfo(alias="Page", default=None)
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.
    """

    page_footer: Optional[GenerationConfig] = FieldInfo(alias="PageFooter", default=None)
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.
    """

    page_header: Optional[GenerationConfig] = FieldInfo(alias="PageHeader", default=None)
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.
    """

    picture: Optional[GenerationConfig] = FieldInfo(alias="Picture", default=None)
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.
    """

    section_header: Optional[GenerationConfig] = FieldInfo(alias="SectionHeader", default=None)
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.
    """

    table: Optional[GenerationConfig] = FieldInfo(alias="Table", default=None)
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.
    """

    text: Optional[GenerationConfig] = FieldInfo(alias="Text", default=None)
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.
    """

    title: Optional[GenerationConfig] = FieldInfo(alias="Title", default=None)
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.
    """
