# Standard Library Dependencies
import math
from typing import Any, Tuple

# PyTorch dependencies
import torch
from torch import Tensor

# Internal dependencies
from thoad.differentiation.engine.broadcasting.alignment import shape_align_indep
from thoad.differentiation.internals.base import ContractiveFunction
from thoad.differentiation.internals.utils.denull import denull_tensor
from thoad.differentiation.internals.utils.derivate import (
    prod0_derivate,
    prod1_derivate,
)
from thoad.differentiation.internals.utils.recalibration import recalibrate_dim
from thoad.typing import Shape, Indep, Notation, IDData


class ProdXBackward0(ContractiveFunction):

    schwarz: bool = True

    def check_shape(
        self,
        out_id: int,
        inp_id: int,
        shape: Shape,
        indep: Indep,
        crossed: bool,
    ) -> Tuple[Shape, Indep]:
        assert self._processed_context is not None
        assert out_id == 0
        assert inp_id == 0
        # initialize shape and indep projections
        projected_shape: Shape = tuple()
        projected_indep: Indep = tuple()
        self._shape0 = projected_shape
        return (projected_shape, projected_indep)

    def _extract_context(self) -> None:
        # extract info
        saved_result: Tensor = getattr(self._grad_fn, "_saved_result")
        saved_self: Tensor = getattr(self._grad_fn, "_saved_self")
        # ensure proper tensor configuration
        saved_result = saved_result.to(dtype=self._dtype, device=self._device)
        getattr(saved_result, "_fix_weakref")()
        saved_self = saved_self.to(dtype=self._dtype, device=self._device)
        getattr(saved_self, "_fix_weakref")()
        # save context
        context: dict[str, Any] = dict()
        context["saved_result"] = saved_result
        context["saved_self"] = saved_self
        self._context = context
        # process context
        self._process_context()
        return None

    def _process_context(self) -> None:
        # checks
        assert self._context is not None
        # load context
        saved_result: Tensor = self._context["saved_result"]
        saved_self: Tensor = self._context["saved_self"]
        # process context
        input: Tensor = denull_tensor(
            tensor=saved_self, dtype=self._dtype, device=self._device
        )
        output: Tensor = denull_tensor(
            tensor=saved_result, dtype=self._dtype, device=self._device
        )  # save processed context
        processed_context: dict[str, Any] = dict()
        processed_context["input"] = input
        processed_context["output"] = output
        self._processed_context = processed_context

        return None

    def _compute_internal_0(self, order: int) -> IDData:
        assert self._processed_context is not None
        assert self._shape0 is not None
        assert self._processed_context is not None
        ### Read context

        input: Tensor = self._processed_context["input"]
        output: Tensor = self._processed_context["output"]

        ### Carry out instrumental operations
        input_shape: Tuple[int, ...] = tuple(input.shape)
        input_size: int = math.prod(input_shape)
        ndim: int = len(input_shape)
        # calculate derivative shape and indices
        external_indices: list[int] = list()
        internal_indices: list[int] = list(range(ndim * order))
        composed_indices: list[list[int]] = list()
        for o in range(order):
            ndims: int = o * ndim
            composed_indices.append([*(range(ndims, ndims + ndim))])
        quotient: Tensor = output / input

        ### Instantiate derivative
        derivative: Tensor
        internal_shape: list[int] = list(input_shape * order)
        if order == 1:
            quotient = quotient.view(size=tuple(internal_shape))
            derivative = quotient
        else:
            quotient = quotient.view(size=(1, input_size))
            quotient = prod0_derivate(tensor=quotient, order=order)
            quotient = quotient.view(size=tuple(internal_shape))
            derivative = quotient

        ### Create einstein notation
        einstein_external: Tuple[int, ...] = tuple(external_indices)
        einstein_internal: Tuple[int, ...] = tuple(internal_indices)
        einstein_composed: Tuple[Tuple[int, ...], ...]
        einstein_composed = tuple(tuple(indices) for indices in composed_indices)
        einstein_notation: Notation = list()
        einstein_notation.append((einstein_external, einstein_internal))
        einstein_notation.append(tuple(einstein_composed))
        einstein_notation.append(
            (tuple(internal_shape), tuple(False for _ in internal_shape))
        )

        return (derivative, einstein_notation)

    def compute_internal(self, out_id: int, inp_id: Tuple[int, ...]) -> IDData:
        ID_data: IDData
        if out_id == 0 and all(i == 0 for i in inp_id):
            order: int = len(inp_id)
            ID_data = self._compute_internal_0(order=order)
        else:
            ID_data = (None, None)
        return ID_data


class ProdXBackward1(ContractiveFunction):

    schwarz: bool = True

    def check_shape(
        self,
        out_id: int,
        inp_id: int,
        shape: Shape,
        indep: Indep,
        crossed: bool,
    ) -> Tuple[Shape, Indep]:
        assert self._processed_context is not None
        assert out_id == 0
        assert inp_id == 0
        dim: Tensor = self._processed_context["dim"]
        keepdim: Tensor = self._processed_context["keepdim"]
        output: Tensor = self._processed_context["output"]
        # initialize shape and indep projections
        projected_shape: Shape = tuple(output.shape)
        projected_indep: Indep = indep
        # project indep if necesary
        if shape != projected_shape:
            projected_indep = shape_align_indep(
                shape=shape,
                indep=indep,
                expected_shape=projected_shape,
            )
        # save as class attributes
        self._shape0 = projected_shape
        if keepdim:
            projected_indep = tuple(d if d != dim else None for d in projected_indep)
        return (projected_shape, projected_indep)

    def _extract_context(self) -> None:
        # extract info
        saved_dim: int = getattr(self._grad_fn, "_saved_dim")
        saved_keepdim: bool = getattr(self._grad_fn, "_saved_keepdim")
        saved_result: Tensor = getattr(self._grad_fn, "_saved_result")
        saved_self: Tensor = getattr(self._grad_fn, "_saved_self")
        # ensure proper tensor configuration
        saved_result = saved_result.to(dtype=self._dtype, device=self._device)
        getattr(saved_result, "_fix_weakref")()
        saved_self = saved_self.to(dtype=self._dtype, device=self._device)
        getattr(saved_self, "_fix_weakref")()
        # save context
        context: dict[str, Any] = dict()
        context["saved_dim"] = saved_dim
        context["saved_keepdim"] = saved_keepdim
        context["saved_result"] = saved_result
        context["saved_self"] = saved_self
        self._context = context
        # process context
        self._process_context()
        return None

    def _process_context(self) -> None:
        # checks
        assert self._context is not None
        # load context
        saved_dim: int = self._context["saved_dim"]
        saved_keepdim: int = self._context["saved_keepdim"]
        saved_result: Tensor = self._context["saved_result"]
        saved_self: Tensor = self._context["saved_self"]
        # process context
        dim: int = recalibrate_dim(dim=saved_dim, shape=saved_self.shape)
        input: Tensor = denull_tensor(
            tensor=saved_self, dtype=self._dtype, device=self._device
        )
        output: Tensor = denull_tensor(
            tensor=saved_result, dtype=self._dtype, device=self._device
        )
        # save processed context
        processed_context: dict[str, Any] = dict()
        processed_context["dim"] = dim
        processed_context["keepdim"] = saved_keepdim
        processed_context["input"] = input
        processed_context["output"] = output
        self._processed_context = processed_context

        return None

    def _compute_internal_0(self, order: int) -> IDData:
        assert self._processed_context is not None
        ### Read context
        dim: int = self._processed_context["dim"]
        keepdim: int = self._processed_context["keepdim"]
        input: Tensor = self._processed_context["input"]
        output: Tensor = self._processed_context["output"]

        ### Carry out instrumental operations
        ndim: int = input.ndim
        dim_size: int = input.shape[dim]
        # calculate external and internal shapes
        external_shape: Tuple[int, ...]
        external_shape = tuple(s for d, s in enumerate(input.shape) if d != dim)
        internal_shape: Tuple[int, ...] = (*external_shape, *(order * (dim_size,)))
        # calculate indices for each stage
        external_indices: list[int] = [d for d in range(ndim) if d != dim or keepdim]
        reduced_external_indices: list[int] = [d for d in range(ndim) if d != dim]
        new_indices: list[int] = list(range(ndim, ndim + order))
        internal_indices: list[int] = [*reduced_external_indices, *new_indices]
        composed_indices: list[list[int]]
        composed_indices = [[*reduced_external_indices] for _ in range(order)]
        for i in range(order):
            composed_indices[i].insert(dim, new_indices[i])
        # create no-keepdim view of output
        viewed_output: Tensor = output.view(size=external_shape)
        # declare info about internal derivative shape & values
        internal_independencies: list[bool] = [True for _ in external_shape]
        internal_independencies.extend([False for _ in range(order)])

        ### Instantiate derivative
        derivative: Tensor = prod1_derivate(
            input=input,
            output=viewed_output,
            dim=dim,
            order=order,
        )
        derivative = derivative.view(size=internal_shape)

        ### Create einstein notation
        einstein_external: Tuple[int, ...] = tuple(external_indices)
        einstein_internal: Tuple[int, ...] = tuple(internal_indices)
        einstein_composed: Tuple[Tuple[int, ...], ...]
        einstein_composed = tuple(tuple(indices) for indices in composed_indices)
        einstein_notation: Notation = list()
        einstein_notation.append((einstein_external, einstein_internal))
        einstein_notation.append(tuple(einstein_composed))
        einstein_notation.append(
            (tuple(internal_shape), tuple(internal_independencies))
        )

        return (derivative, einstein_notation)

    def compute_internal(self, out_id: int, inp_id: Tuple[int, ...]) -> IDData:
        ID_data: IDData
        if out_id == 0 and all(i == 0 for i in inp_id):
            order: int = len(inp_id)
            ID_data = self._compute_internal_0(order=order)
        else:
            ID_data = (None, None)
        return ID_data
