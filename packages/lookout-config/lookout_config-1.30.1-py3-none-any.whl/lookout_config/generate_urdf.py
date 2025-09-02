from lookout_config import LookoutConfig
from greenstream_config import Offsets, get_cameras_urdf
from gr_urchin import (
    URDF,
    Joint,
    Material,
    Link,
    xyz_rpy_to_matrix,
    Visual,
    Mesh,
    Geometry,
    Box,
)
from math import radians


def joint_from_offsets(offsets: Offsets, parent: str, child: str) -> Joint:
    return Joint(
        name=f"{parent}_to_{child}",
        parent=parent,
        child=child,
        joint_type="fixed",
        origin=xyz_rpy_to_matrix(
            [
                offsets.forward or 0.0,
                offsets.left or 0.0,
                offsets.up or 0.0,
                offsets.roll or 0.0,
                offsets.pitch or 0.0,
                offsets.yaw or 0.0,
            ]
        ),
    )


def generate_urdf(
    config: LookoutConfig,
    add_optical_frame: bool = True,
):
    mesh_path = (
        f"package://lookout_bringup/meshes/{config.offsets.name}"
        if config.offsets.name != ""
        else None
    )
    file_path = f"/tmp/vessel_{config.mode.value}.urdf"
    camera_links, camera_joints = get_cameras_urdf(config.cameras, add_optical_frame)  # type: ignore

    urdf = URDF(
        name="origins",
        materials=[
            Material(name="grey", color=[0.75, 0.75, 0.75, 0.6]),
            Material(name="blue", color=[0, 0.12, 0.25, 0.9]),
        ],
        links=[
            Link(name="ins", inertial=None, visuals=None, collisions=None),
            Link(
                name="waterline",
                visuals=[
                    Visual(
                        name="waterline",
                        geometry=Geometry(box=Box([10.0, 10.0, 0.01])),
                        material=Material(name="blue"),
                    )
                ],
                inertial=None,
                collisions=None,
            ),
            Link(
                name="base_link",
                visuals=(
                    [
                        Visual(
                            name="visual",
                            geometry=Geometry(
                                mesh=Mesh(
                                    filename=mesh_path,
                                    combine=False,
                                    lazy_filename=mesh_path,
                                )
                            ),
                            origin=xyz_rpy_to_matrix([0, 0, 0, radians(-90), 0, 0]),
                            material=Material(name="grey"),
                        ),
                    ]
                    if mesh_path
                    else []
                ),
                inertial=None,
                collisions=None,
            ),
            *camera_links,
        ],
        joints=[
            joint_from_offsets(config.offsets.baselink_to_ins, "base_link", "ins"),
            joint_from_offsets(config.offsets.baselink_to_waterline, "base_link", "waterline"),
            *camera_joints,
        ],
    )

    urdf.save(file_path)

    with open(file_path) as infp:
        robot_description = infp.read()

    return robot_description
