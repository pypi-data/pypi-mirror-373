import os
import numpy as np
import pytest
import shutil
import tempfile
import SimpleITK as sitk

from konfai.utils.dataset import Dataset, Attribute, data_to_image, image_to_data


@pytest.fixture
def temp_dataset_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def create_dummy_image():
    img = sitk.GaussianSource(size=[32, 32, 32], sigma=[1.0]*3)
    return img


def test_write_and_read_image(temp_dataset_dir):
    dataset = Dataset(temp_dataset_dir, format="npy")
    image = create_dummy_image()
    attr = Attribute()
    data, attrs = image_to_data(image)
    attr.update(attrs)

    dataset.write("GroupA", "TestImage", image, attr)
    image_out = dataset.readImage("GroupA", "TestImage")

    assert isinstance(image_out, sitk.Image)
    assert image_out.GetSize() == image.GetSize()


def test_get_names_and_groups(temp_dataset_dir):
    dataset = Dataset(temp_dataset_dir, format="npy")
    image = create_dummy_image()
    attr = Attribute()
    data, attrs = image_to_data(image)
    attr.update(attrs)

    dataset.write("GroupA", "Test1", image, attr)
    dataset.write("GroupA", "Test2", image, attr)

    names = dataset.getNames("GroupA")
    groups = dataset.getGroup()

    assert "Test1" in names
    assert "Test2" in names
    assert any("GroupA" in g for g in groups)


def test_dataset_exists(temp_dataset_dir):
    dataset = Dataset(temp_dataset_dir, format="npy")
    image = create_dummy_image()
    attr = Attribute()
    data, attrs = image_to_data(image)
    attr.update(attrs)

    dataset.write("GroupA", "ExistsImage", image, attr)

    assert dataset.isDatasetExist("GroupA", "ExistsImage")
    assert not dataset.isDatasetExist("GroupA", "MissingImage")


def test_read_data_and_transform(temp_dataset_dir):
    dataset = Dataset(temp_dataset_dir, format="npy")
    image = create_dummy_image()
    attr = Attribute()
    data, attrs = image_to_data(image)
    attr.update(attrs)

    dataset.write("GroupA", "ImageData", data, attr)

    read_data, read_attr = dataset.readData("GroupA", "ImageData")

    assert isinstance(read_data, np.ndarray)
    assert "Origin" in read_attr