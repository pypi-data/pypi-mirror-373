import pytest
import torch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from precious.models import PreciousConfig, PreciousModel

@pytest.fixture
def model():
    config = PreciousConfig(mode="tfree")
    model = PreciousModel(config)
    return model

def test_model_initialization(model):
    assert model.cfg.mode == "tfree"
    assert model.cfg.d_model == 512
    assert model.cfg.n_heads == 8
    assert model.cfg.n_layers == 4

def test_forward_pass_tfree(model):
    inputs = ["This is a test sentence.", "Another test."]
    outputs = model(inputs)
    assert "logits" in outputs
    assert outputs["logits"].shape[0] == len(inputs)

def test_forward_pass_canine():
    config = PreciousConfig(mode="canine")
    model = PreciousModel(config)
    inputs = ["This is a test sentence.", "Another test."]
    outputs = model(inputs)
    assert "logits" in outputs
    assert outputs["logits"].shape[0] == len(inputs)

def test_forward_pass_byte():
    config = PreciousConfig(mode="byte")
    model = PreciousModel(config)
    inputs = ["This is a test sentence.", "Another test."]
    outputs = model(inputs)
    assert "logits" in outputs
    assert outputs["logits"].shape[0] == len(inputs)

def test_loss_calculation_tfree(model):
    inputs = ["This is a test sentence.", "Another test."]
    targets = ["This is a test.", "Another one."]
    outputs = model(inputs, targets)
    assert "loss" in outputs

def test_loss_calculation_canine():
    config = PreciousConfig(mode="canine")
    model = PreciousModel(config)
    inputs = ["This is a test sentence.", "Another test."]
    targets = ["This is a test.", "Another one."]
    outputs = model(inputs, targets)
    assert "loss" in outputs

def test_loss_calculation_byte():
    config = PreciousConfig(mode="byte")
    model = PreciousModel(config)
    inputs = ["This is a test sentence.", "Another test."]
    targets = ["This is a test.", "Another one."]
    outputs = model(inputs, targets)
    assert "loss" in outputs
