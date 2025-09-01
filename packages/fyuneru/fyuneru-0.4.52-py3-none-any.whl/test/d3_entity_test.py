import numpy as np
from loguru import logger
from scipy.spatial.transform import Rotation as R

from fyuneru.lib import init_logger
from fyuneru.d3_entity import SElement


def test_euler_rot():
    quat_rot = np.array([0.0, 0.0, 0.707, 0.707])
    element = SElement(rotation=quat_rot)

    # assert element.euler_rot() == R.from_quat(quat_rot).as_euler("xyz")
    assert np.allclose(element.euler_rot(), R.from_quat(quat_rot).as_euler("xyz"))


def test_matrix_rot():
    quat_rot = np.array([0.0, 0.0, 0.707, 0.707])
    element = SElement(rotation=quat_rot)
    assert np.allclose(element.matrix_rot(), R.from_quat(quat_rot).as_matrix())


# def test_euler():
#     quat_rot = np.array([0.1, 0.3, 0.707, 0.707])
#     euler_rot_xyz = R.from_quat(quat_rot).as_euler("xyz")
#     euler_rot_zyx = R.from_quat(quat_rot).as_euler("zyx")
#     logger.info(f"euler_rot_xyz: {euler_rot_xyz}")
#     logger.info(f"euler_rot_zyx: {euler_rot_zyx}")
#     assert np.allclose(euler_rot_xyz, euler_rot_zyx[::-1])


if __name__ == "__main__":
    init_logger(level="INFO")
    test_euler_rot()
    test_matrix_rot()
    # test_euler()
