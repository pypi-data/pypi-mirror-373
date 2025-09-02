# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo
from .generation_config_param import GenerationConfigParam

__all__ = ["SegmentProcessingParam"]


class SegmentProcessingParam(TypedDict, total=False):
    caption: Annotated[Optional[GenerationConfigParam], PropertyInfo(alias="Caption")]
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

    footnote: Annotated[Optional[GenerationConfigParam], PropertyInfo(alias="Footnote")]
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

    formula: Annotated[Optional[GenerationConfigParam], PropertyInfo(alias="Formula")]
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

    list_item: Annotated[Optional[GenerationConfigParam], PropertyInfo(alias="ListItem")]
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

    page: Annotated[Optional[GenerationConfigParam], PropertyInfo(alias="Page")]
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

    page_footer: Annotated[Optional[GenerationConfigParam], PropertyInfo(alias="PageFooter")]
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

    page_header: Annotated[Optional[GenerationConfigParam], PropertyInfo(alias="PageHeader")]
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

    picture: Annotated[Optional[GenerationConfigParam], PropertyInfo(alias="Picture")]
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

    section_header: Annotated[Optional[GenerationConfigParam], PropertyInfo(alias="SectionHeader")]
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

    table: Annotated[Optional[GenerationConfigParam], PropertyInfo(alias="Table")]
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

    text: Annotated[Optional[GenerationConfigParam], PropertyInfo(alias="Text")]
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

    title: Annotated[Optional[GenerationConfigParam], PropertyInfo(alias="Title")]
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
