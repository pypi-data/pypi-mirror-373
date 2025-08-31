# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from typing import List
from typing import Optional

from easydiffraction.core.objects import Collection
from easydiffraction.sample_models.sample_model import SampleModel
from easydiffraction.utils.decorators import enforce_type
from easydiffraction.utils.formatting import paragraph


class SampleModels(Collection):
    """
    Collection manager for multiple SampleModel instances.
    """

    @property
    def _child_class(self):
        return SampleModel

    def __init__(self) -> None:
        super().__init__()  # Initialize Collection
        self._models = self._items  # Alias for legacy support

    def add(
        self,
        model: Optional[SampleModel] = None,
        name: Optional[str] = None,
        cif_path: Optional[str] = None,
        cif_str: Optional[str] = None,
    ) -> None:
        """
        Add a new sample model to the collection.
        Dispatches based on input type: pre-built model or parameters for new creation.

        Args:
            model: An existing SampleModel instance.
            name: Name for a new model if created from scratch.
            cif_path: Path to a CIF file to create a model from.
            cif_str: CIF content as string to create a model from.
        """
        if model:
            self._add_prebuilt_sample_model(model)
        else:
            self._create_and_add_sample_model(name, cif_path, cif_str)

    def remove(self, name: str) -> None:
        """
        Remove a sample model by its ID.

        Args:
            name: ID of the model to remove.
        """
        if name in self._models:
            del self._models[name]

    def get_ids(self) -> List[str]:
        """
        Return a list of all model IDs in the collection.

        Returns:
            List of model IDs.
        """
        return list(self._models.keys())

    @property
    def ids(self) -> List[str]:
        """Property accessor for model IDs."""
        return self.get_ids()

    def show_names(self) -> None:
        """List all model IDs in the collection."""
        print(paragraph('Defined sample models' + ' 🧩'))
        print(self.get_ids())

    def show_params(self) -> None:
        """Show parameters of all sample models in the collection."""
        for model in self._models.values():
            model.show_params()

    def as_cif(self) -> str:
        """
        Export all sample models to CIF format.

        Returns:
            CIF string representation of all sample models.
        """
        return '\n'.join([model.as_cif() for model in self._models.values()])

    @enforce_type
    def _add_prebuilt_sample_model(self, sample_model: SampleModel) -> None:
        """
        Add a pre-built SampleModel instance.

        Args:
            model: The SampleModel instance to add.

        Raises:
            TypeError: If model is not a SampleModel instance.
        """
        self._models[sample_model.name] = sample_model

    def _create_and_add_sample_model(
        self,
        name: Optional[str] = None,
        cif_path: Optional[str] = None,
        cif_str: Optional[str] = None,
    ) -> None:
        """
        Create a SampleModel instance and add it to the collection.

        Args:
            name: Name for the new model.
            cif_path: Path to a CIF file.
            cif_str: CIF content as string.

        Raises:
            ValueError: If neither name, cif_path, nor cif_str is provided.
        """
        if cif_path:
            model = SampleModel(cif_path=cif_path)
        elif cif_str:
            model = SampleModel(cif_str=cif_str)
        elif name:
            model = SampleModel(name=name)
        else:
            raise ValueError('You must provide a name, cif_path, or cif_str.')

        self._models[model.name] = model
