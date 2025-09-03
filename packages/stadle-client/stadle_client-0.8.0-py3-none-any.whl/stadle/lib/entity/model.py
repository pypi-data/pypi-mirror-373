import pathlib
import pickle
from typing import Any

from stadle.lib import (BaseModelConvFormat, extract_weights_dict,
                        merge_model_weights)
from stadle.lib.env.handler import EnvironmentHandler

# TODO replace with conditional import
if EnvironmentHandler.pt_installed_flag():
    import torch

if EnvironmentHandler.tf_installed_flag():
    import tensorflow as tf


class BaseModel(object):
    """Base Model represents an entity which contains the Deep Learning Model
    Args:
        name: name of the model
        obj: deep learning model object (Torch Model, Tensorflow Model)
        type: Model Type (PyTorch, Tensorflow)
        id: model id
    """

    def __init__(self, name: str, obj: object, type: BaseModelConvFormat, id: str = None):
        """constructor
        """
        self._name = name
        self._obj = obj
        self._type = type
        self._id = id

        self.create_serialized_obj()
        self.extract_initial_weights()

    @property
    def name(self) -> str:
        """
        get the name of the model
        Returns:
        """
        return self._name

    @name.setter
    def name(self, name) -> None:
        """
        set the name of the model
        Args:
            name:
        """
        self._name = name

    @property
    def obj(self) -> Any:
        """
        get model object
        Returns:
        """
        return self._obj

    @obj.setter
    def obj(self, obj) -> None:
        """
        set model object
        Args:
            obj:
        """
        self._obj = obj

    @property
    def ser_obj(self) -> Any:
        """
        get model object
        Returns:
        """
        return self._ser_obj

    @ser_obj.setter
    def ser_obj(self, ser_obj) -> None:
        """
        set model object
        Args:
            obj:
        """
        self._ser_obj = ser_obj

    @property
    def weights(self) -> Any:
        """
        get model object
        Returns:
        """
        return self._weights

    @weights.setter
    def weights(self, weights) -> None:
        """
        set model object
        Args:
            obj:
        """
        self._weights = weights

    @property
    def type(self) -> BaseModelConvFormat:
        """
        get model type
        Returns:
        """
        return self._type

    @type.setter
    def type(self, type) -> None:
        """
        set model type
        Args:
            type:
        """
        self._type = type

    @property
    def id(self) -> str:
        """
        get model id
        Returns:
        """
        return self._id

    @id.setter
    def id(self, id) -> None:
        """
        set model id
        Args:
            id: unique id for the model
        """
        self._id = id

    def __str__(self):
        if self._type == BaseModelConvFormat.pytorch_format:
            type_name = "PyTorch"
        elif self._type == BaseModelConvFormat.keras_format:
            type_name = "Keras"
        elif self._type == BaseModelConvFormat.tensorflow_format:
            type_name = "TensorFlow"
        else:
            type_name = "No Type Set"

        return f"Base Model: \n\tName: {self._name}\n\tType: {type_name}\n\tModel Object Serialized: {self._ser_obj != None}"
        #return "Model Name: " + self._name + "\n" + ", Model : " + self._ser_obj.__str__() + "\n" + "Type : " + str(
        #    self._type) + "\n" + "ID : " + self._id

    def create_serialized_obj(self):
        if self.type == BaseModelConvFormat.pytorch_format:
            state_dict = self.obj.state_dict()
            self.ser_obj = {k:v.numpy() for k,v in state_dict.items()}
        elif self.type == BaseModelConvFormat.keras_format:
            self.ser_obj = None
        else:
            raise ValueError("Attempted to serialize base model obj without valid model type")

    def extract_initial_weights(self):
        self.weights = extract_weights_dict(self.obj, self.type)

    def prep_for_pickle(self):
        self.obj = None

    def save(self, data_path, file_handler) -> None:
        """
        save the model
        Args:
            data_path: path to save the model
        Returns:
        """
        filepath = f"{data_path}/base_models/{self.id}.pkl"
        ser_filepath = f"{data_path}/base_models/{self.id}_ser.pkl"

        pathlib.Path(f'{data_path}/base_models').mkdir(exist_ok=True)

        if (self.type == BaseModelConvFormat.pytorch_format):
            with open(ser_filepath, 'wb') as f:
                pickle.dump(self.ser_obj, f)
            # upload ser_filepath to s3 bucket
            if not file_handler.s3_file_exists(s3_file_path=ser_filepath):
                file_handler.upload_file(file_path_local=ser_filepath)

            self.ser_obj = None

        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
        # upload filepath to s3 bucket
        if not file_handler.s3_file_exists(s3_file_path=filepath):
            file_handler.upload_file(file_path_local=filepath)

        return filepath

    def get_merged_model(self, weight_dict):
        """
        get the fused model considering the based model and the updated weight vectors
        Args:
            weight_dict: weight dictionary
        Returns:
        """
        merged_model = merge_model_weights(self.obj, weight_dict, self.type)

        return merged_model
