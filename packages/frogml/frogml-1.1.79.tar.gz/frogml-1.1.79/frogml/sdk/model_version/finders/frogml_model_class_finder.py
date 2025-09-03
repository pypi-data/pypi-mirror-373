from typing import Optional, Set

import libcst as cst
from typing_extensions import Self


class FrogMlModelClassFinder(cst.CSTVisitor):
    """Visitor to find FrogMlModel classes and their model fields."""

    def __init__(self: Self):
        super().__init__()
        self.__found_class_name: Optional[str] = None
        self.__found_model_field: Optional[str] = None
        self.__is_in_target_class: bool = False
        self.__is_in_init_method: bool = False
        self.__possible_model_field_names: Set[str] = {"model", "_model", "__model"}

    @property
    def found_class_name(self: Self) -> Optional[str]:
        return self.__found_class_name

    @property
    def found_model_field(self: Self) -> Optional[str]:
        return self.__found_model_field

    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        """
        Check if this class inherits from FrogMlModel.

        :param node: ClassDef node to check
        :return: True if the class inherits from FrogMlModel, False otherwise
        """
        if self.__found_class_name is not None:
            return False

        for base in node.bases:
            inherits_without_changed_name: bool = (
                isinstance(base.value, cst.Attribute)
                and isinstance(base.value.value, cst.Name)
                and (
                    base.value.attr.value == "FrogMlModel"
                    and base.value.value.value == "frogml"
                )
            )

            inherits_with_changed_name: bool = (
                isinstance(base.value, cst.Name) and base.value.value == "FrogMlModel"
            )

            if inherits_without_changed_name or inherits_with_changed_name:
                self.__is_in_target_class = True
                self.__found_class_name = node.name.value
                return True

        return False

    def leave_ClassDef(self, original_node: cst.ClassDef):
        """
        Reset the state when leaving a class.

        :param original_node: The original ClassDef node
        """
        self.__is_in_target_class = False

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
        """
        Check if this function is the __init__ method of the target class.

        :param node: FunctionDef node to check
        """
        if self.__is_in_target_class and node.name.value == "__init__":
            self.__is_in_init_method = True
            return True

        return False

    def leave_FunctionDef(self, original_node: cst.FunctionDef):
        """
        Reset the state when leaving a function.

        :param original_node: The original FunctionDef node
        """
        self.__is_in_init_method = False

    def visit_Assign(self, node: cst.Assign) -> bool:
        """
        Check if this assignment is a model field assignment.

        :param node: Assign node to check
        :return: True if this is a model field assignment, False otherwise
        """

        if not self.__is_in_init_method:
            return False

        for target in node.targets:
            if isinstance(target, cst.AssignTarget) and isinstance(
                target.target, cst.Attribute
            ):
                attr: cst.Attribute = target.target

                if isinstance(attr.value, cst.Name) and attr.value.value == "self":
                    if attr.attr.value in self.__possible_model_field_names:
                        self.__found_model_field = attr.attr.value
                        return False

        return True

    def visit_AnnAssign(self, node: cst.AnnAssign) -> bool:
        """
        Check if this annotation assignment is a model field assignment.

        :param node: AnnAssign node to check
        :return: True if this is a model field assignment, False otherwise
        """
        if not self.__is_in_init_method:
            return False

        if isinstance(node.target, cst.Attribute):
            attr: cst.Attribute = node.target

            if isinstance(attr.value, cst.Name) and attr.value.value == "self":
                if attr.attr.value in self.__possible_model_field_names:
                    self.__found_model_field = attr.attr.value
                    return False

        return True
