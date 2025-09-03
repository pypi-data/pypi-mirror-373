from __future__ import annotations

from seekrai.abstract import api_requestor
from seekrai.resources.resource_base import ResourceBase
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import (
    ImageRequest,
    ImageResponse,
    SeekrFlowClient,
    SeekrFlowRequest,
)


class Images(ResourceBase):
    def generate(
        self,
        *,
        prompt: str,
        model: str,
        steps: int | None = 20,
        seed: int | None = None,
        n: int | None = 1,
        height: int | None = 1024,
        width: int | None = 1024,
        negative_prompt: str | None = None,
    ) -> ImageResponse:
        """
        Method to generate images based on a given prompt using a specified model.

        Args:
            prompt (str): A description of the desired images. Maximum length varies by model.

            model (str, optional): The model to use for image generation.

            steps (int, optional): Number of generation steps. Defaults to 20

            seed (int, optional): Seed used for generation. Can be used to reproduce image generations.
                Defaults to None.

            n (int, optional): Number of image results to generate. Defaults to 1.

            height (int, optional): Height of the image to generate in number of pixels. Defaults to 1024

            width (int, optional): Width of the image to generate in number of pixels. Defaults to 1024

            negative_prompt (str, optional): The prompt or prompts not to guide the image generation.
                Defaults to None

            image_base64: (str, optional): Reference image used for generation. Defaults to None.

        Returns:
            ImageResponse: Object containing image data
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = ImageRequest(
            prompt=prompt,
            model=model,
            steps=steps,
            seed=seed,
            n=n,
            height=height,
            width=width,
            negative_prompt=negative_prompt,
        ).model_dump()

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url="inference/images/generations",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return ImageResponse(**response.data)


class AsyncImages(ResourceBase):
    def __init__(self, client: SeekrFlowClient) -> None:
        self._client = client

    async def generate(
        self,
        *,
        prompt: str,
        model: str,
        steps: int | None = 20,
        seed: int | None = None,
        n: int | None = 1,
        height: int | None = 1024,
        width: int | None = 1024,
        negative_prompt: str | None = None,
    ) -> ImageResponse:
        """
        Async method to generate images based on a given prompt using a specified model.

        Args:
            prompt (str): A description of the desired images. Maximum length varies by model.

            model (str, optional): The model to use for image generation.

            steps (int, optional): Number of generation steps. Defaults to 20

            seed (int, optional): Seed used for generation. Can be used to reproduce image generations.
                Defaults to None.

            n (int, optional): Number of image results to generate. Defaults to 1.

            height (int, optional): Height of the image to generate in number of pixels. Defaults to 1024

            width (int, optional): Width of the image to generate in number of pixels. Defaults to 1024

            negative_prompt (str, optional): The prompt or prompts not to guide the image generation.
                Defaults to None

            image_base64: (str, optional): Reference image used for generation. Defaults to None.

        Returns:
            ImageResponse: Object containing image data
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = ImageRequest(
            prompt=prompt,
            model=model,
            steps=steps,
            seed=seed,
            n=n,
            height=height,
            width=width,
            negative_prompt=negative_prompt,
        ).model_dump()

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url="inference/images/generations",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return ImageResponse(**response.data)
