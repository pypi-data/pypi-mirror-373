# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing utility functions for the PydanticVisitor class.
"""

import ast

#######################################################################
## adapted from: flake8-pydantic v0.4.0
##
## Original: Copyright (c) 2023 Victorien
#######################################################################


def getDecoratorNames(decoratorList):
    """
    Function to extract the set of decorator names.

    @param decoratorList list of decorators to be processed
    @type list of ast.expr
    @return set containing the decorator names
    @rtype set of str
    """
    names = set()

    for dec in decoratorList:
        if isinstance(dec, ast.Call):
            names.add(
                dec.func.attr if isinstance(dec.func, ast.Attribute) else dec.func.id
            )
        elif isinstance(dec, ast.Name):
            names.add(dec.id)
        elif isinstance(dec, ast.Attribute):
            names.add(dec.attr)

    return names


def _hasPydanticModelBase(node, *, includeRootModel):
    """
    Function to check, if a class definition inherits from Pydantic model classes.

    @param node reference to the node to be be analyzed
    @type ast.ClassDef
    @keyparam includeRootModel flag indicating to include the root model
    @type bool
    @return flag indicating that the class definition inherits from a Pydantic model
        class
    @rtype bool
    """
    modelClassNames = {"BaseModel"}
    if includeRootModel:
        modelClassNames.add("RootModel")

    for base in node.bases:
        if isinstance(base, ast.Name) and base.id in modelClassNames:
            return True
        if isinstance(base, ast.Attribute) and base.attr in modelClassNames:
            return True
    return False


def _hasModelConfig(node):
    """
    Function to check, if the class has a `model_config` attribute set.

    @param node reference to the node to be be analyzed
    @type ast.ClassDef
    @return flag indicating that the class has a `model_config` attribute set
    @rtype bool
    """
    for stmt in node.body:
        if (
            isinstance(stmt, ast.AnnAssign)
            and isinstance(stmt.target, ast.Name)
            and stmt.target.id == "model_config"
        ):
            ##~ model_config: ... = ...
            return True

        if isinstance(stmt, ast.Assign) and any(
            t.id == "model_config" for t in stmt.targets if isinstance(t, ast.Name)
        ):
            ##~ model_config = ...
            return True

    return False


PYDANTIC_FIELD_ARGUMENTS = {  # noqa: M-916
    "default",
    "default_factory",
    "alias",
    "alias_priority",
    "validation_alias",
    "title",
    "description",
    "examples",
    "exclude",
    "discriminator",
    "json_schema_extra",
    "frozen",
    "validate_default",
    "repr",
    "init",
    "init_var",
    "kw_only",
    "pattern",
    "strict",
    "gt",
    "ge",
    "lt",
    "le",
    "multiple_of",
    "allow_inf_nan",
    "max_digits",
    "decimal_places",
    "min_length",
    "max_length",
    "union_mode",
}


def _hasFieldFunction(node):
    """
    Function to check, if the class has a field defined with the `Field` function.

    @param node reference to the node to be be analyzed
    @type ast.ClassDef
    @return flag indicating that the class has a field defined with the `Field` function
    @rtype bool
    """
    if any(
        isinstance(stmt, (ast.Assign, ast.AnnAssign))
        and isinstance(stmt.value, ast.Call)
        and (
            (
                isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == "Field"
            )  # f = Field(...)
            or (
                isinstance(stmt.value.func, ast.Attribute)
                and stmt.value.func.attr == "Field"
            )  # f = pydantic.Field(...)
        )
        and all(
            kw.arg in PYDANTIC_FIELD_ARGUMENTS
            for kw in stmt.value.keywords
            if kw.arg is not None
        )
        for stmt in node.body
    ):
        return True

    return False


def _hasAnnotatedField(node):
    """
    Function to check if the class has a field making use of `Annotated`.

    @param node reference to the node to be be analyzed
    @type ast.ClassDef
    @return flag indicating that the class has a field making use of `Annotated`
    @rtype bool
    """
    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(
            stmt.annotation, ast.Subscript
        ):
            if (
                isinstance(stmt.annotation.value, ast.Name)
                and stmt.annotation.value.id == "Annotated"
            ):
                ##~ f: Annotated[...]
                return True

            if (
                isinstance(stmt.annotation.value, ast.Attribute)
                and stmt.annotation.value.attr == "Annotated"
            ):
                ##~ f: typing.Annotated[...]
                return True

    return False


PYDANTIC_DECORATORS = {  # noqa: M-916
    "computed_field",
    "field_serializer",
    "model_serializer",
    "field_validator",
    "model_validator",
}


def _hasPydanticDecorator(node):
    """
    Function to check, if the class makes use of Pydantic decorators, such as
    `computed_field` or `model_validator`.

    @param node reference to the node to be be analyzed
    @type ast.ClassDef
    @return flag indicating that the class makes use of Pydantic decorators, such as
        `computed_field` or `model_validator`.
    @rtype bool
    """
    for stmt in node.body:
        if isinstance(stmt, ast.FunctionDef):
            decoratorNames = getDecoratorNames(stmt.decorator_list)
            if PYDANTIC_DECORATORS & decoratorNames:
                return True
    return False


PYDANTIC_METHODS = {  # noqa: M-916
    "model_construct",
    "model_copy",
    "model_dump",
    "model_dump_json",
    "model_json_schema",
    "model_parametrized_name",
    "model_rebuild",
    "model_validate",
    "model_validate_json",
    "model_validate_strings",
}


def _hasPydanticMethod(node: ast.ClassDef) -> bool:
    """
    Function to check, if the class overrides any of the Pydantic methods, such as
    `model_dump`.

    @param node reference to the node to be be analyzed
    @type ast.ClassDef
    @return flag indicating that class overrides any of the Pydantic methods, such as
        `model_dump`
    @rtype bool
    """
    if any(
        isinstance(stmt, ast.FunctionDef)
        and (
            stmt.name.startswith(("__pydantic_", "__get_pydantic_"))
            or stmt.name in PYDANTIC_METHODS
        )
        for stmt in node.body
    ):
        return True

    return False


def isPydanticModel(node, *, includeRootModel=True):
    """
    Function to determine if a class definition is a Pydantic model.

    Multiple heuristics are use to determine if this is the case:
    - The class inherits from `BaseModel` (or `RootModel` if `includeRootModel` is
      `True`).
    - The class has a `model_config` attribute set.
    - The class has a field defined with the `Field` function.
    - The class has a field making use of `Annotated`.
    - The class makes use of Pydantic decorators, such as `computed_field` or
      `model_validator`.
    - The class overrides any of the Pydantic methods, such as `model_dump`.

    @param node reference to the node to be be analyzed
    @type ast.ClassDef
    @keyparam includeRootModel flag indicating to include the root model
        (defaults to True)
    @type bool (optional)
    @return flag indicating a Pydantic model class
    @rtype bool
    """
    if not node.bases:
        return False

    return (
        _hasPydanticModelBase(node, includeRootModel=includeRootModel)
        or _hasModelConfig(node)
        or _hasFieldFunction(node)
        or _hasAnnotatedField(node)
        or _hasPydanticDecorator(node)
        or _hasPydanticMethod(node)
    )


def isDataclass(node):
    """
    Function to check, if a class is a dataclass.

    @param node reference to the node to be be analyzed
    @type ast.ClassDef
    @return flag indicating that the class is a dataclass.
    @rtype bool
    """
    """Determine if a class is a dataclass."""

    return bool(
        {"dataclass", "pydantic_dataclass"} & getDecoratorNames(node.decorator_list)
    )


def isFunction(node, functionName):
    """
    Function to check, if a function call is referencing a given function name.

    @param node reference to the node to be be analyzed
    @type ast.Call
    @param functionName name of the function to check for
    @type str
    @return flag indicating that the function call is referencing the given function
        name
    @rtype bool
    """
    return (isinstance(node.func, ast.Name) and node.func.id == functionName) or (
        isinstance(node.func, ast.Attribute) and node.func.attr == functionName
    )


def isName(node, name):
    """
    Function to check, if an expression is referencing a given name.

    @param node reference to the node to be be analyzed
    @type ast.expr
    @param name name to check for
    @type str
    @return flag indicating that the expression is referencing teh given name
    @rtype bool
    """
    return (isinstance(node, ast.Name) and node.id == name) or (
        isinstance(node, ast.Attribute) and node.attr == name
    )


def extractAnnotations(node):
    """
    Function to extract the annotations of an expression.

    @param node reference to the node to be be processed
    @type ast.expr
    @return set containing the annotation names
    @rtype set[str]
    """
    annotations = set()

    if isinstance(node, ast.Name):
        ##~ foo: date = ...
        annotations.add(node.id)

    elif isinstance(node, ast.BinOp):
        ##~ foo: date | None = ...
        annotations |= extractAnnotations(node.left)
        annotations |= extractAnnotations(node.right)

    elif isinstance(node, ast.Subscript):
        ##~ foo: dict[str, date]
        ##~ foo: Annotated[list[date], ...]
        if isinstance(node.slice, ast.Tuple):
            for elt in node.slice.elts:
                annotations |= extractAnnotations(elt)
        if isinstance(node.slice, ast.Name):
            annotations.add(node.slice.id)

    return annotations
