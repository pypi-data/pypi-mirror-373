from argparse import ArgumentParser
import json
from math import floor
from pathlib import Path

from jacobi import Planner, Trajectory
import zipfile


def main():
    parser = ArgumentParser(description=(
        'Create a *.jacobi-blender file of an animated robot motion'
        'from a Jacobi project and a corresponding trajectory.'
    ))
    parser.add_argument('project', type=Path, help='Jacobi project file.')
    parser.add_argument('trajectory', help='Trajectory *.json file for animate the robot.')
    parser.add_argument('-r', '--robot', default=None, help='Robot that should run the trajectory.')
    parser.add_argument('-o', '--output', type=Path, default=None, help='Output *.jacobi-blender file.')

    args = parser.parse_args()

    planner = Planner.load_from_project_file(args.project)
    environment = planner.environment
    robot = environment.get_robot(args.robot) if args.robot else environment.get_robot()

    tmp_file = Path('tmp')
    tmp_file.mkdir(exist_ok=True)

    # Extract project file to readable folder
    with zipfile.ZipFile(args.project, 'r') as zip_ref:
        zip_ref.extractall(tmp_file)

    trajectory = Trajectory.from_json_file(args.trajectory)

    # Scale down fps
    delta_time = trajectory.times[1] - trajectory.times[0]
    scale = floor(1.0 / (30 * delta_time))

    result = {
        'trajectory': {
            'times': trajectory.times[::scale],
        },
    }

    link_objects = []
    for dof, o in enumerate(robot.link_obstacles):
        data = {
            'file_path': f'{str(tmp_file)}/public/{robot.model}/meshes/visual/{o.name}.glb',
        }

        frames = []
        for p in trajectory.positions[::scale]:
            robot.calculate_tcp(p)
            frames.append(robot.link_frames[dof].matrix)

        data['frames'] = frames
        link_objects.append(data)

    result['link_objects'] = link_objects

    # Export to *.jacobi-blender file
    output = args.output or Path(args.project.name).with_suffix('.jacobi-blender')
    with output.open('w') as json_file:
        json.dump(result, json_file)


if __name__ == '__main__':
    main()
