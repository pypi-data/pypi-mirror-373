from dataclasses import dataclass, field

import numpy as np
from scipy.spatial.transform import Rotation as R


@dataclass
class SElement:
    translation: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    rotation: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0, 1.0]))

    def euler_rot(self, seq="xyz", degrees=False):
        return R.from_quat(self.rotation).as_euler(seq=seq, degrees=degrees)

    def matrix_rot(self):
        return R.from_quat(self.rotation).as_matrix()

    def as_matrix(self):
        matrix = np.eye(4)
        matrix[:3, :3] = R.from_quat(self.rotation).as_matrix()
        matrix[:3, 3] = self.translation
        return matrix

    @classmethod
    def from_matrix(cls, matrix: np.ndarray) -> "SElement":
        return cls(
            translation=matrix[:3, 3], rotation=R.from_matrix(matrix[:3, :3]).as_quat()
        )

    @classmethod
    def from_rot_matrix(
        cls, rot_matrix: np.ndarray, translation: np.ndarray
    ) -> "SElement":
        matrix = np.eye(4)
        matrix[:3, :3] = rot_matrix
        matrix[:3, 3] = translation
        return cls.from_matrix(matrix)


def to_pos_matrix(selement: SElement) -> list:
    pos_matrix = []
    pos_matrix.extend(selement.translation.tolist())
    pos_matrix.extend(selement.euler_rot(seq="zyx").tolist())
    return pos_matrix
