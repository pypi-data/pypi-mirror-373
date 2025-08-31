"""
Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
SPDX-License-Identifier: MIT
"""

import argparse
import os

import tensorrt_llm
import tensorrt_llm.profiler as profiler
from PIL import Image
from tensorrt_llm import logger

from dolphin_runner import DolphinRunner
from utils import add_common_args

os.environ["TOKENIZERS_PARALLELISM"] = "false"


def print_result(model, input_text, output_text, args):
    logger.info("---------------------------------------------------------")
    logger.info(f"\n[Q] {input_text}")
    for i in range(len(output_text)):
        logger.info(f"\n[A]: {output_text[i]}")

    if args.num_beams == 1:
        output_ids = model.tokenizer(output_text[0][0], add_special_tokens=False)[
            "input_ids"
        ]
        logger.info(f"Generated {len(output_ids)} tokens")

    if args.check_accuracy:
        if model.model_type != "nougat":
            if model.model_type == "vila":
                for i in range(len(args.image_path.split(args.path_sep))):
                    if i % 2 == 0:
                        assert (
                            output_text[i][0].lower()
                            == "the image captures a bustling city intersection teeming with life. from the perspective of a car's dashboard camera, we see"
                        )
                    else:
                        assert (
                            output_text[i][0].lower()
                            == "the image captures the iconic merlion statue in singapore, a renowned worldwide landmark. the merlion, a mythical"
                        )
            elif model.model_type == "llava":
                for i in range(len(args.image_path.split(args.path_sep))):
                    assert output_text[i][0].lower() == "singapore"
            elif model.model_type == "fuyu":
                assert output_text[0][0].lower() == "4"
            elif model.model_type == "pix2struct":
                assert (
                    "characteristic | cat food, day | cat food, wet | cat treats"
                    in output_text[0][0].lower()
                )
            elif model.model_type in ["blip2", "neva", "phi-3-vision", "llava_next"]:
                assert "singapore" in output_text[0][0].lower()
            elif model.model_type == "video-neva":
                assert "robot" in output_text[0][0].lower()
            elif model.model_type == "kosmos-2":
                assert "snowman" in output_text[0][0].lower()
            elif model.model_type == "mllama":
                if "If I had to write a haiku for this one" in input_text:
                    assert (
                        "it would be:.\\nPeter Rabbit is a rabbit.\\nHe lives in a"
                        in output_text[0][0]
                        or "Here is a haiku for the image:\n\n" in output_text[0][0]
                    ), (
                        f"expected results: 'it would be:.\\nPeter Rabbit is a rabbit.\\nHe lives in a', generated results: '{output_text[0][0]}'"
                    )
                elif "The key to life is" in input_text:
                    assert (
                        "to find your passion and pursue it with all your heart."
                        in output_text[0][0]
                        or "not to be found in the external world," in output_text[0][0]
                    ), (
                        f"expected results: 'to find your passion and pursue it with all your heart.', generated results: '{output_text[0][0]}'"
                    )
            elif model.model_type == "llava_onevision":
                if args.video_path is None:
                    assert "singapore" in output_text[0][0].lower()
                else:
                    assert (
                        "the video is funny because the child's actions are"
                        in output_text[0][0].lower()
                    )
            elif model.model_type == "qwen2_vl":
                assert "dog" in output_text[0][0].lower()
            else:
                assert output_text[0][0].lower() == "singapore"

    if args.run_profiling:
        msec_per_batch = (
            lambda name: 1000
            * profiler.elapsed_time_in_sec(name)
            / args.profiling_iterations
        )
        logger.info("Latencies per batch (msec)")
        logger.info("TRT vision encoder: %.1f" % (msec_per_batch("Vision")))
        logger.info("TRTLLM LLM generate: %.1f" % (msec_per_batch("LLM")))
        logger.info("Multimodal generate: %.1f" % (msec_per_batch("Generate")))

    logger.info("---------------------------------------------------------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser = add_common_args(parser)
    args = parser.parse_args()
    logger.set_level(args.log_level)

    model = DolphinRunner(args)

    input_image = Image.open(args.image_path[0]).convert("RGB")
    num_iters = args.profiling_iterations if args.run_profiling else 1

    for _ in range(num_iters):
        output_texts = model.run(args.input_text, [input_image], args.max_new_tokens)

    runtime_rank = tensorrt_llm.mpi_rank()
    if runtime_rank == 0:
        print_result(model, args.input_text, output_texts, args)
