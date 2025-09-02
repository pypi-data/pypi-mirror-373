import logging
import os
import string

IMPORT_MODULE_NAME = "model_service"


def get_int_env(env_name: string, default_var: int) -> int:
    try:
        const_var = int(os.getenv(env_name))
    except:
        const_var = default_var
    return const_var


__ti_model_dir = os.getenv("TI_MODEL_DIR", "/data/model")
__ti_preprocess_nums = get_int_env("TI_PREPROCESS_NUMS", 0)
__ti_inference_nums = get_int_env("TI_INFERENCE_NUMS", 1)
__ti_postprocess_nums = get_int_env("TI_POSTPROCESS_NUMS", 0)
__ti_inference_max_batch_size = get_int_env("TI_INFERENCE_MAX_BATCH_SIZE", 1)


def print_envs() -> None:
    # logging.info(f"TI_MODEL_DIR: {__ti_model_dir}")
    logging.info(f"TI_PREPROCESS_NUMS: {__ti_preprocess_nums}")
    logging.info(f"TI_INFERENCE_NUMS: {__ti_inference_nums}")
    logging.info(f"TI_POSTPROCESS_NUMS: {__ti_postprocess_nums}")
    logging.info(f"TI_INFERENCE_MAX_BATCH_SIZE: {__ti_inference_max_batch_size}")


def set_ti_preprocess_nums(num: int):
    global __ti_preprocess_nums
    __ti_preprocess_nums = num


def set_ti_inference_nums(num: int):
    global __ti_inference_nums
    __ti_inference_nums = num


def set_ti_postprocess_nums(num: int):
    global __ti_postprocess_nums
    __ti_postprocess_nums = num


def set_ti_inference_max_batch_size(batch: int):
    global __ti_inference_max_batch_size
    __ti_inference_max_batch_size = batch


def get_ti_model_dir() -> string:
    return __ti_model_dir


def get_ti_preprocess_nums():
    return __ti_preprocess_nums


def get_ti_inference_nums():
    return __ti_inference_nums


def get_ti_postprocess_nums():
    return __ti_postprocess_nums


def get_ti_inference_max_batch_size():
    return __ti_inference_max_batch_size


def Is_Multi_Framework_Type() -> bool:
    """Preprocess And PostProcess Run In Single Process"""
    return __ti_preprocess_nums != 0 or __ti_postprocess_nums != 0
