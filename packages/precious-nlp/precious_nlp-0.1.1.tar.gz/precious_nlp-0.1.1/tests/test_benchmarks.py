import time
import torch
import pytest
import os
import sys
from typing import Dict, List, Tuple
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from precious import PreciousConfig, PreciousModel


class PerformanceBenchmark:
    """Performance benchmark utilities for Precious models."""

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.results = {}

    def measure_memory_usage(self) -> float:
        """Get current memory usage in MB (simplified without psutil)."""
        return 0.0  # Placeholder - would need psutil for real measurement

    def measure_gpu_memory(self) -> float:
        """Get current GPU memory usage in MB."""
        if torch.cuda.is_available():
            return torch.cuda.memory_allocated() / 1024 / 1024
        return 0.0

    def benchmark_forward_pass(self, model: torch.nn.Module, inputs: List[str],
                             num_iterations: int = 100) -> Dict[str, float]:
        """Benchmark forward pass performance."""
        model.eval()

        # Warmup
        with torch.no_grad():
            for _ in range(10):
                _ = model(inputs)

        # Clear cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()

        # Measure performance
        start_time = time.time()
        start_gpu_memory = self.measure_gpu_memory()

        with torch.no_grad():
            for _ in range(num_iterations):
                outputs = model(inputs)
                if torch.cuda.is_available():
                    torch.cuda.synchronize()

        end_time = time.time()
        end_gpu_memory = self.measure_gpu_memory()

        total_time = end_time - start_time
        avg_time = total_time / num_iterations
        gpu_memory_diff = end_gpu_memory - start_gpu_memory

        return {
            "total_time": total_time,
            "avg_time_per_iteration": avg_time,
            "throughput_samples_per_sec": len(inputs) / avg_time,
            "memory_usage_mb": 0.0,  # Simplified without psutil
            "gpu_memory_usage_mb": gpu_memory_diff,
            "output_shape": outputs["logits"].shape if "logits" in outputs else None
        }

    def benchmark_training_step(self, model: torch.nn.Module, inputs: List[str],
                               targets: List[str], num_iterations: int = 50) -> Dict[str, float]:
        """Benchmark training step performance."""
        model.train()
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)

        # Warmup
        for _ in range(5):
            optimizer.zero_grad()
            outputs = model(inputs, targets=targets)
            if "loss" in outputs:
                outputs["loss"].backward()
                optimizer.step()

        # Clear cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()

        # Measure performance
        start_time = time.time()
        start_gpu_memory = self.measure_gpu_memory()

        for _ in range(num_iterations):
            optimizer.zero_grad()
            outputs = model(inputs, targets=targets)
            if "loss" in outputs:
                outputs["loss"].backward()
                optimizer.step()
            if torch.cuda.is_available():
                torch.cuda.synchronize()

        end_time = time.time()
        end_gpu_memory = self.measure_gpu_memory()

        total_time = end_time - start_time
        avg_time = total_time / num_iterations
        gpu_memory_diff = end_gpu_memory - start_gpu_memory

        return {
            "total_time": total_time,
            "avg_time_per_iteration": avg_time,
            "throughput_samples_per_sec": len(inputs) / avg_time,
            "memory_usage_mb": 0.0,  # Simplified without psutil
            "gpu_memory_usage_mb": gpu_memory_diff
        }


@pytest.fixture
def benchmark():
    return PerformanceBenchmark()


@pytest.fixture
def sample_data():
    return {
        "short_texts": ["Hello", "World", "Test"],
        "medium_texts": [
            "This is a medium length sentence for testing.",
            "Another sentence with some more words in it.",
            "Testing the performance with moderate length text."
        ],
        "long_texts": [
            "This is a much longer text that contains multiple sentences and should test the model's ability to handle longer sequences. " * 3,
            "Another long text example that we use for benchmarking purposes and performance evaluation across different model configurations. " * 3,
            "A third example of longer text that helps us understand how the model scales with sequence length and complexity. " * 3
        ]
    }


def test_tfree_performance_comparison(benchmark, sample_data):
    """Compare T-FREE performance across different model sizes."""
    configs = [
        PreciousConfig(mode="tfree", d_model=128, n_heads=4, n_layers=2),
        PreciousConfig(mode="tfree", d_model=256, n_heads=8, n_layers=4),
        PreciousConfig(mode="tfree", d_model=512, n_heads=8, n_layers=6)
    ]

    results = {}

    for i, config in enumerate(configs):
        model = PreciousModel(config).to(benchmark.device)
        model_name = f"tfree_size_{i+1}"

        # Test on medium texts
        perf = benchmark.benchmark_forward_pass(
            model, sample_data["medium_texts"], num_iterations=50
        )
        results[model_name] = perf

        print(f"\n{model_name} (d_model={config.d_model}):")
        print(f"  Average time: {perf['avg_time_per_iteration']:.4f}s")
        print(f"  Throughput: {perf['throughput_samples_per_sec']:.2f} samples/sec")
        print(f"  Memory usage: {perf['memory_usage_mb']:.2f} MB")
        if perf['gpu_memory_usage_mb'] > 0:
            print(f"  GPU memory: {perf['gpu_memory_usage_mb']:.2f} MB")

    # Assert that larger models are reasonably slower
    assert results["tfree_size_1"]["avg_time_per_iteration"] <= results["tfree_size_3"]["avg_time_per_iteration"] * 2


def test_mode_performance_comparison(benchmark, sample_data):
    """Compare performance across different tokenizer-free modes."""
    configs = [
        PreciousConfig(mode="tfree", d_model=256),
        PreciousConfig(mode="canine", d_model=256),
        PreciousConfig(mode="byte", d_model=256)
    ]

    results = {}

    for config in configs:
        model = PreciousModel(config).to(benchmark.device)

        # Forward pass benchmark
        forward_perf = benchmark.benchmark_forward_pass(
            model, sample_data["medium_texts"], num_iterations=30
        )

        # Training step benchmark
        training_perf = benchmark.benchmark_training_step(
            model, sample_data["medium_texts"], sample_data["medium_texts"], num_iterations=20
        )

        results[config.mode] = {
            "forward": forward_perf,
            "training": training_perf
        }

        print(f"\n{config.mode.upper()} mode:")
        print(f"  Forward pass: {forward_perf['avg_time_per_iteration']:.4f}s")
        print(f"  Training step: {training_perf['avg_time_per_iteration']:.4f}s")
        print(f"  Forward throughput: {forward_perf['throughput_samples_per_sec']:.2f} samples/sec")

    # Store results for comparison
    benchmark.results["mode_comparison"] = results


def test_sequence_length_scaling(benchmark):
    """Test how performance scales with sequence length."""
    config = PreciousConfig(mode="byte", d_model=256)
    model = PreciousModel(config).to(benchmark.device)

    # Different sequence lengths
    test_cases = [
        (["short"], "short"),
        (["This is a medium length sequence with more tokens"], "medium"),
        (["This is a very long sequence that contains many more words and should test the model's scaling behavior with increased sequence length and complexity " * 3], "long"),
        (["x" * 500], "very_long")
    ]

    results = {}

    for inputs, length_name in test_cases:
        perf = benchmark.benchmark_forward_pass(model, inputs, num_iterations=20)
        results[length_name] = perf

        print(f"\n{length_name} sequence:")
        print(f"  Input length: ~{len(inputs[0])} chars")
        print(f"  Average time: {perf['avg_time_per_iteration']:.4f}s")
        print(f"  Output shape: {perf['output_shape']}")

    # Assert that longer sequences take more time (roughly)
    assert results["short"]["avg_time_per_iteration"] <= results["long"]["avg_time_per_iteration"]


def test_batch_size_scaling(benchmark, sample_data):
    """Test how performance scales with batch size."""
    config = PreciousConfig(mode="byte", d_model=256)
    model = PreciousModel(config).to(benchmark.device)

    batch_sizes = [1, 4, 8, 16]
    results = {}

    for batch_size in batch_sizes:
        # Create batch by repeating medium text
        batch_inputs = sample_data["medium_texts"][:1] * batch_size

        perf = benchmark.benchmark_forward_pass(model, batch_inputs, num_iterations=20)
        results[f"batch_{batch_size}"] = perf

        per_sample_time = perf['avg_time_per_iteration'] / batch_size

        print(f"\nBatch size {batch_size}:")
        print(f"  Total time: {perf['avg_time_per_iteration']:.4f}s")
        print(f"  Per sample: {per_sample_time:.4f}s")
        print(f"  Throughput: {perf['throughput_samples_per_sec']:.2f} samples/sec")

    # Assert that larger batches have better throughput per sample
    batch_1_per_sample = results["batch_1"]["avg_time_per_iteration"]
    batch_16_per_sample = results["batch_16"]["avg_time_per_iteration"] / 16

    assert batch_16_per_sample <= batch_1_per_sample, "Batching should improve per-sample efficiency"


def test_memory_efficiency(benchmark, sample_data):
    """Test memory efficiency across different configurations."""
    configs = [
        PreciousConfig(mode="byte", d_model=128, n_layers=2),
        PreciousConfig(mode="byte", d_model=256, n_layers=4),
        PreciousConfig(mode="byte", d_model=512, n_layers=6)
    ]

    for i, config in enumerate(configs):
        model = PreciousModel(config).to(benchmark.device)

        # Count parameters
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

        # Measure memory during forward pass
        perf = benchmark.benchmark_forward_pass(model, sample_data["medium_texts"], num_iterations=10)

        print(f"\nModel {i+1} (d_model={config.d_model}, layers={config.n_layers}):")
        print(f"  Parameters: {total_params:,} total, {trainable_params:,} trainable")
        print(f"  Time per iteration: {perf['avg_time_per_iteration']:.4f}s")
        if perf['gpu_memory_usage_mb'] > 0:
            print(f"  GPU memory: {perf['gpu_memory_usage_mb']:.2f} MB")


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
def test_gpu_vs_cpu_performance(benchmark, sample_data):
    """Compare GPU vs CPU performance when CUDA is available."""
    config = PreciousConfig(mode="byte", d_model=256)

    # CPU benchmark
    model_cpu = PreciousModel(config).to("cpu")
    cpu_perf = benchmark.benchmark_forward_pass(model_cpu, sample_data["medium_texts"], num_iterations=10)

    # GPU benchmark
    model_gpu = PreciousModel(config).to("cuda")
    gpu_perf = benchmark.benchmark_forward_pass(model_gpu, sample_data["medium_texts"], num_iterations=10)

    speedup = cpu_perf["avg_time_per_iteration"] / gpu_perf["avg_time_per_iteration"]

    print(f"\nCPU vs GPU Performance:")
    print(f"  CPU time: {cpu_perf['avg_time_per_iteration']:.4f}s")
    print(f"  GPU time: {gpu_perf['avg_time_per_iteration']:.4f}s")
    print(f"  Speedup: {speedup:.2f}x")

    # GPU should be faster (though this depends on model size and hardware)
    assert speedup > 0.8, f"Expected reasonable performance, got speedup: {speedup:.2f}x"


if __name__ == "__main__":
    # Run benchmarks directly
    benchmark = PerformanceBenchmark()
    sample_data = {
        "short_texts": ["Hello", "World", "Test"],
        "medium_texts": [
            "This is a medium length sentence for testing.",
            "Another sentence with some more words in it.",
            "Testing the performance with moderate length text."
        ]
    }

    print("Running performance benchmarks...")

    # Quick benchmark
    config = PreciousConfig(mode="byte", d_model=256)
    model = PreciousModel(config).to(benchmark.device)

    perf = benchmark.benchmark_forward_pass(model, sample_data["medium_texts"], num_iterations=20)
    print(f"\nQuick benchmark results:")
    print(f"  Average time: {perf['avg_time_per_iteration']:.4f}s")
    print(f"  Throughput: {perf['throughput_samples_per_sec']:.2f} samples/sec")
    print(f"  Device: {benchmark.device}")
