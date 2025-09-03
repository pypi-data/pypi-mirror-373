from .paths import RobotModel, RobotType, URDFModel


class Vega1Model(RobotModel):
    @property
    def vega_upper_body_right_arm(self) -> URDFModel:
        return URDFModel(self._type, self._name, "vega_upper_body_right_arm")

    @property
    def vega_upper_body_no_effector(self) -> URDFModel:
        return URDFModel(self._type, self._name, "vega_upper_body_no_effector")

    @property
    def vega_no_effector(self) -> URDFModel:
        return URDFModel(self._type, self._name, "vega_no_effector")

    @property
    def vega(self) -> URDFModel:
        return URDFModel(self._type, self._name, "vega")

    @property
    def vega_upper_body(self) -> URDFModel:
        return URDFModel(self._type, self._name, "vega_upper_body")


class F5d6HandModel(RobotModel):
    @property
    def f5d6_right(self) -> URDFModel:
        return URDFModel(self._type, self._name, "f5d6_right")

    @property
    def f5d6_left(self) -> URDFModel:
        return URDFModel(self._type, self._name, "f5d6_left")


class HumanoidType(RobotType):
    @property
    def vega_1(self) -> Vega1Model:
        return Vega1Model("humanoid", "vega_1")


class HandsType(RobotType):
    @property
    def f5d6_hand(self) -> F5d6HandModel:
        return F5d6HandModel("hands", "f5d6_hand")


humanoid = HumanoidType("humanoid")
hands = HandsType("hands")


def get_all_robot_dirs() -> list[RobotModel]:
    return []
