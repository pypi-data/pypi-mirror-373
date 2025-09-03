import sys
import torch
import pytest
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from precious import PreciousConfig, PreciousModel


def test_integration_all_modes():
    """Integration test for all three modes with device support"""
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Test T-FREE mode
    m1 = PreciousModel(PreciousConfig(mode="tfree", d_model=256)).to(device)
    o1 = m1(["Hello world!"])
    print("tfree logits:", o1["logits"].shape)
    assert "logits" in o1
    assert o1["logits"].dim() == 3  # [batch, seq_len, vocab_size]

    # Test CANINE mode with targets
    m2 = PreciousModel(PreciousConfig(mode="canine", d_model=256)).to(device)
    o2 = m2(["hello"], targets=["hello!"])
    print("canine logits:", o2["logits"].shape, "loss:", o2.get("loss"))
    assert "logits" in o2
    assert "loss" in o2
    assert o2["logits"].dim() == 3
    assert isinstance(o2["loss"], torch.Tensor)

    # Test byte mode with targets
    m3 = PreciousModel(PreciousConfig(mode="byte", d_model=256)).to(device)
    o3 = m3(["abc"], targets=["abcd"])
    print("byte logits:", o3["logits"].shape, "loss:", o3.get("loss"))
    assert "logits" in o3
    assert "loss" in o3
    assert o3["logits"].dim() == 3
    assert isinstance(o3["loss"], torch.Tensor)


def test_device_compatibility():
    """Test that models work on both CPU and CUDA if available"""
    config = PreciousConfig(mode="byte", d_model=128)

    # Test CPU
    model_cpu = PreciousModel(config)
    output_cpu = model_cpu(["test"])
    assert output_cpu["logits"].device.type == "cpu"

    # Test CUDA if available
    if torch.cuda.is_available():
        model_cuda = PreciousModel(config).to("cuda")
        output_cuda = model_cuda(["test"])
        assert output_cuda["logits"].device.type == "cuda"


def test_different_model_sizes():
    """Test different model configurations"""
    small_config = PreciousConfig(mode="byte", d_model=64, n_heads=2, n_layers=2)
    large_config = PreciousConfig(mode="byte", d_model=512, n_heads=8, n_layers=6)

    small_model = PreciousModel(small_config)
    large_model = PreciousModel(large_config)

    inputs = ["test input"]

    small_output = small_model(inputs)
    large_output = large_model(inputs)

    assert small_output["logits"].shape[-1] == 256  # byte vocab size
    assert large_output["logits"].shape[-1] == 256  # byte vocab size
    assert small_output["logits"].shape[0] == large_output["logits"].shape[0]  # same batch size


def test_batch_processing():
    """Test that models handle different batch sizes correctly"""
    config = PreciousConfig(mode="byte", d_model=128)
    model = PreciousModel(config)

    # Test different batch sizes
    single_input = ["hello"]
    batch_input = ["hello", "world", "test"]
    large_batch = ["text"] * 10

    single_output = model(single_input)
    batch_output = model(batch_input)
    large_batch_output = model(large_batch)

    assert single_output["logits"].shape[0] == 1
    assert batch_output["logits"].shape[0] == 3
    assert large_batch_output["logits"].shape[0] == 10


if __name__ == "__main__":
    # Run the main integration test
    test_integration_all_modes()
