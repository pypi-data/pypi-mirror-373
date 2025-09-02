# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from chunkr_ai import Chunkr, AsyncChunkr
from tests.utils import assert_matches_type
from chunkr_ai.types.tasks import ExtractGetResponse, ExtractCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestExtract:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Chunkr) -> None:
        extract = client.tasks.extract.create(
            file="file",
            schema={},
        )
        assert_matches_type(ExtractCreateResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Chunkr) -> None:
        extract = client.tasks.extract.create(
            file="file",
            schema={},
            expires_in=0,
            file_name="file_name",
            parse_configuration={
                "chunk_processing": {
                    "ignore_headers_and_footers": True,
                    "target_length": 0,
                    "tokenizer": {"enum": "Word"},
                },
                "error_handling": "Fail",
                "llm_processing": {
                    "fallback_strategy": "None",
                    "llm_model_id": "llm_model_id",
                    "max_completion_tokens": 0,
                    "temperature": 0,
                },
                "ocr_strategy": "All",
                "pipeline": "Azure",
                "segment_processing": {
                    "caption": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "footnote": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "formula": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "list_item": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "page": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "page_footer": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "page_header": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "picture": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "section_header": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "table": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "text": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "title": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                },
                "segmentation_strategy": "LayoutAnalysis",
            },
            system_prompt="system_prompt",
        )
        assert_matches_type(ExtractCreateResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Chunkr) -> None:
        response = client.tasks.extract.with_raw_response.create(
            file="file",
            schema={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extract = response.parse()
        assert_matches_type(ExtractCreateResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Chunkr) -> None:
        with client.tasks.extract.with_streaming_response.create(
            file="file",
            schema={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extract = response.parse()
            assert_matches_type(ExtractCreateResponse, extract, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Chunkr) -> None:
        extract = client.tasks.extract.get(
            task_id="task_id",
        )
        assert_matches_type(ExtractGetResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Chunkr) -> None:
        extract = client.tasks.extract.get(
            task_id="task_id",
            base64_urls=True,
            include_chunks=True,
            wait_for_completion=True,
        )
        assert_matches_type(ExtractGetResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Chunkr) -> None:
        response = client.tasks.extract.with_raw_response.get(
            task_id="task_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extract = response.parse()
        assert_matches_type(ExtractGetResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Chunkr) -> None:
        with client.tasks.extract.with_streaming_response.get(
            task_id="task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extract = response.parse()
            assert_matches_type(ExtractGetResponse, extract, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Chunkr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.tasks.extract.with_raw_response.get(
                task_id="",
            )


class TestAsyncExtract:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncChunkr) -> None:
        extract = await async_client.tasks.extract.create(
            file="file",
            schema={},
        )
        assert_matches_type(ExtractCreateResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncChunkr) -> None:
        extract = await async_client.tasks.extract.create(
            file="file",
            schema={},
            expires_in=0,
            file_name="file_name",
            parse_configuration={
                "chunk_processing": {
                    "ignore_headers_and_footers": True,
                    "target_length": 0,
                    "tokenizer": {"enum": "Word"},
                },
                "error_handling": "Fail",
                "llm_processing": {
                    "fallback_strategy": "None",
                    "llm_model_id": "llm_model_id",
                    "max_completion_tokens": 0,
                    "temperature": 0,
                },
                "ocr_strategy": "All",
                "pipeline": "Azure",
                "segment_processing": {
                    "caption": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "footnote": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "formula": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "list_item": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "page": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "page_footer": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "page_header": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "picture": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "section_header": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "table": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "text": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                    "title": {
                        "crop_image": "All",
                        "description": True,
                        "extended_context": True,
                        "format": "Html",
                        "strategy": "LLM",
                    },
                },
                "segmentation_strategy": "LayoutAnalysis",
            },
            system_prompt="system_prompt",
        )
        assert_matches_type(ExtractCreateResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncChunkr) -> None:
        response = await async_client.tasks.extract.with_raw_response.create(
            file="file",
            schema={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extract = await response.parse()
        assert_matches_type(ExtractCreateResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncChunkr) -> None:
        async with async_client.tasks.extract.with_streaming_response.create(
            file="file",
            schema={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extract = await response.parse()
            assert_matches_type(ExtractCreateResponse, extract, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncChunkr) -> None:
        extract = await async_client.tasks.extract.get(
            task_id="task_id",
        )
        assert_matches_type(ExtractGetResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncChunkr) -> None:
        extract = await async_client.tasks.extract.get(
            task_id="task_id",
            base64_urls=True,
            include_chunks=True,
            wait_for_completion=True,
        )
        assert_matches_type(ExtractGetResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncChunkr) -> None:
        response = await async_client.tasks.extract.with_raw_response.get(
            task_id="task_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extract = await response.parse()
        assert_matches_type(ExtractGetResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncChunkr) -> None:
        async with async_client.tasks.extract.with_streaming_response.get(
            task_id="task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extract = await response.parse()
            assert_matches_type(ExtractGetResponse, extract, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncChunkr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.tasks.extract.with_raw_response.get(
                task_id="",
            )
