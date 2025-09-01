from typing import List, Tuple

from gr_urchin import Joint, Link, xyz_rpy_to_matrix
from greenstream_config.types import Camera


def get_camera_urdf(
    camera: Camera,
    links: List[Link],
    joints: List[Joint],
    add_optical_frame: bool = True,
    has_duplicate_camera_link: bool = False,
) -> Tuple[List[Link], List[Joint]]:
    # This is the camera urdf from the gama/lookout greenstream.launch.py
    # We need to generate this from the camera config

    # Only generate camera link if it currently doesn't exist. This checks for multiple cameras within the same housing
    # etc: bow camera has both visible and thermal cameras, it is assumed that they are connected via the same ptz system
    if not has_duplicate_camera_link:
        camera_xyz_rpy = (
            [
                camera.camera_offsets.forward or 0.0,
                camera.camera_offsets.left or 0.0,
                camera.camera_offsets.up or 0.0,
                camera.camera_offsets.roll or 0.0,
                camera.camera_offsets.pitch or 0.0,
                camera.camera_offsets.yaw or 0.0,
            ]
            if camera.camera_offsets
            else [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        )

        links.append(
            Link(
                name=f"{camera.name}_link",
                inertial=None,
                visuals=None,
                collisions=None,
            )
        )
        joints.append(
            Joint(
                name=f"{camera.name}_joint",
                parent="base_link",
                child=f"{camera.name}_link",
                joint_type="fixed",
                origin=xyz_rpy_to_matrix(camera_xyz_rpy),
            )
        )

        if camera.ptz:
            for ptz_component in camera.ptz_offsets:
                parent_link = links[-1].name
                if ptz_component.type == "pan":
                    links.append(
                        Link(
                            name=f"{camera.name}_pan_link",
                            inertial=None,
                            visuals=None,
                            collisions=None,
                        ),
                    )

                    camera_pan_xyz_rpy = [
                        ptz_component.forward or 0.0,
                        ptz_component.left or 0.0,
                        ptz_component.up or 0.0,
                        ptz_component.roll or 0.0,
                        ptz_component.pitch or 0.0,
                        ptz_component.yaw or 0.0,
                    ]

                    joints.append(
                        Joint(
                            name=f"{camera.name}_pan_joint",
                            parent=parent_link,
                            child=f"{camera.name}_pan_link",
                            joint_type="continuous",
                            origin=xyz_rpy_to_matrix(camera_pan_xyz_rpy),
                            axis=[0, 0, 1],
                        )
                    )

                elif ptz_component.type == "tilt":
                    links.append(
                        Link(
                            name=f"{camera.name}_tilt_link",
                            inertial=None,
                            visuals=None,
                            collisions=None,
                        ),
                    )

                    camera_tilt_xyz_rpy = [
                        ptz_component.forward or 0.0,
                        ptz_component.left or 0.0,
                        ptz_component.up or 0.0,
                        ptz_component.roll or 0.0,
                        ptz_component.pitch or 0.0,
                        ptz_component.yaw or 0.0,
                    ]

                    joints.append(
                        Joint(
                            name=f"{camera.name}_tilt_joint",
                            parent=parent_link,
                            child=f"{camera.name}_tilt_link",
                            joint_type="continuous",
                            origin=xyz_rpy_to_matrix(camera_tilt_xyz_rpy),
                            axis=[0, 1, 0],
                        )
                    )

    if add_optical_frame:

        if has_duplicate_camera_link:
            # search for the parent link of another camera frame bounded by the same camera link (i.e. color, thermal within the same housing)
            for joint in reversed(joints):
                child_link_name = joint.child
                if (
                    child_link_name.startswith(camera.name)
                    and child_link_name.endswith("frame")
                    and "optical" not in child_link_name
                ):
                    parent_link = joint.parent
                    break
        else:
            parent_link = links[-1].name

        links.append(
            Link(
                name=f"{camera.name}_{camera.type}_frame",
                inertial=None,
                visuals=None,
                collisions=None,
            )
        )
        links.append(
            Link(
                name=f"{camera.name}_{camera.type}_optical_frame",
                inertial=None,
                visuals=None,
                collisions=None,
            )
        )
        # fixed transforms between camera frame and optical frame FRD -> NED
        joints.append(
            Joint(
                name=f"{parent_link}_to_{camera.type}_frame",
                parent=f"{parent_link}",
                child=f"{camera.name}_{camera.type}_frame",
                joint_type="fixed",
                origin=xyz_rpy_to_matrix([0, 0, 0, 0, 0, 0]),
            )
        )
        joints.append(
            Joint(
                name=f"{camera.name}_{camera.type}_frame_to_optical_frame",
                parent=f"{camera.name}_{camera.type}_frame",
                child=f"{camera.name}_{camera.type}_optical_frame",
                joint_type="fixed",
                origin=xyz_rpy_to_matrix([0, 0, 0, -1.570796, 0, -1.570796]),
            )
        )

    return (links, joints)


def get_cameras_urdf(
    cameras: List[Camera],
    add_optical_frame: bool = True,
) -> Tuple[List[Link], List[Joint]]:

    links: List[Link] = []
    joints: List[Joint] = []

    for camera in cameras:

        # skip duplicate camera links, only add optical frame of camera of a different type (i.e. color, thermal)
        if camera.name in [prev_camera.name for prev_camera in cameras[: cameras.index(camera)]]:
            links, joints = get_camera_urdf(
                camera,
                links,
                joints,
                add_optical_frame,
                has_duplicate_camera_link=True,
            )
        else:
            links, joints = get_camera_urdf(
                camera,
                links,
                joints,
                add_optical_frame,
                has_duplicate_camera_link=False,
            )

    return links, joints
