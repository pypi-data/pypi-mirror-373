import numpy as np
import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from moviepy.video.io.VideoFileClip import VideoFileClip

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.assemble_movie import AssembleDlnirspMovie
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import MovieFrameHeaders
from dkist_processing_dlnirsp.tests.conftest import tag_on_mosaic_dither_loops
from dkist_processing_dlnirsp.tests.conftest import write_frames_to_task


def write_movie_frames_to_task(
    task,
    dither_mode_on: bool,
    num_mosaics: int,
    num_X_tiles: int,
    num_Y_tiles: int,
    array_shape: tuple[int, int],
) -> int:
    dataset = MovieFrameHeaders(
        dither_mode_on=dither_mode_on,
        num_mosaics=num_mosaics,
        num_X_tiles=num_X_tiles,
        num_Y_tiles=num_Y_tiles,
        array_shape=array_shape,
    )

    num_written_frames = write_frames_to_task(
        task=task,
        frame_generator=dataset,
        extra_tags=[
            DlnirspTag.movie_frame(),
        ],
        tag_func=tag_on_mosaic_dither_loops,
        data_func=make_movie_frame_data,
    )
    return num_written_frames


def make_movie_frame_data(frame: MovieFrameHeaders) -> np.ndarray:
    shape = frame.array_shape[1:]
    data = np.zeros(shape)
    total_frames = frame.dataset_shape[0]
    current_index = frame.index + 1
    horizontal_frac = int((current_index / total_frames) * shape[0])
    data[:horizontal_frac, :] = 1.0

    return data


@pytest.fixture
def assemble_movie_task(recipe_run_id, dither_mode_on, tmp_path, link_constants_db):
    num_mosaics = 4
    num_X_tiles = 3
    num_Y_tiles = 2

    constants = DlnirspTestingConstants(
        NUM_MOSAIC_REPEATS=num_mosaics,
        NUM_MOSAIC_TILES_X=num_X_tiles,
        NUM_MOSAIC_TILES_Y=num_Y_tiles,
        NUM_DITHER_STEPS=int(dither_mode_on) + 1,
    )
    link_constants_db(recipe_run_id, constants)

    with AssembleDlnirspMovie(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)

        yield task, num_mosaics, num_X_tiles, num_Y_tiles
        task._purge()


@pytest.mark.parametrize("dither_mode_on", [pytest.param(True, id="dither_mode_on")])
@pytest.mark.parametrize(
    "is_polarimetric, requires_shrinking",
    [
        pytest.param(True, True, id="polarimetric_shrink"),
        pytest.param(False, False, id="spectrographic_noshrink"),
        pytest.param(True, False, id="polarimetric_noshrink"),
    ],
)
def test_assemble_movie(
    assemble_movie_task,
    dither_mode_on,
    is_polarimetric,
    requires_shrinking,
    mocker,
    fake_gql_client,
):
    """
    Given: An AssembleDlnirspMovie task and associated MOVIE_FRAME files
    When: Running the task
    Then: A movie is generated with the correct size
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task, num_mosaics, num_X_tiles, num_Y_tiles = assemble_movie_task

    if requires_shrinking:
        movie_shape = (1080 * 2, 1920 * 2)  # Intentionally "backward" from normal
        expected_shape = (1080, 1920)[::-1]
    else:
        movie_shape = (1920 // 2 - 1, 1080 // 2 - 1)  # Weird aspect ratio
        expected_shape = (1920, 1080)[::-1]  # Because AssembleMovie will force even dimensions
    write_movie_frames_to_task(
        task,
        dither_mode_on=dither_mode_on,
        num_mosaics=num_mosaics,
        num_X_tiles=num_X_tiles,
        num_Y_tiles=num_Y_tiles,
        array_shape=movie_shape,
    )

    task()

    movie_file = list(task.read(tags=[DlnirspTag.movie()]))
    assert len(movie_file) == 1
    assert movie_file[0].exists()
    clip = VideoFileClip(str(movie_file[0]))
    assert tuple(clip.size) == expected_shape

    # import os
    # os.system(f"cp {movie_file[0]} foo.mp4")


@pytest.mark.parametrize(
    "dither_mode_on",
    [pytest.param(True, id="dither_mode_on"), pytest.param(False, id="dither_mode_off")],
)
def test_tags_for_images(assemble_movie_task, dither_mode_on):
    """
    Given: A `AssembleDlnirspMovie` task with constants describing the number of L1 frames
    When: Computing the tags for a certain movie image
    Then: The correct tags are returned
    """
    task, num_mosaics, num_X_tiles, num_Y_tiles = assemble_movie_task
    num_dither = int(dither_mode_on) + 1

    assert task.num_images == num_mosaics * num_dither * num_X_tiles * num_Y_tiles

    expected_mosaic_values = sum(
        [[i for _ in range(num_X_tiles * num_Y_tiles * num_dither)] for i in range(num_mosaics)], []
    )
    expected_dither_values = (
        sum([[d] * num_X_tiles * num_Y_tiles for d in range(num_dither)], []) * num_mosaics
    )
    expected_X_tile_values = (
        sum([[i for _ in range(num_Y_tiles)] for i in range(1, num_X_tiles + 1)] * num_mosaics, [])
        * num_dither
    )
    expected_Y_tile_values = (
        list(range(1, num_Y_tiles + 1)) * num_X_tiles * num_mosaics * num_dither
    )

    for n in range(task.num_images):
        assert sorted(task.tags_for_image_n(n)) == sorted(
            [
                DlnirspTag.mosaic_num(expected_mosaic_values[n]),
                DlnirspTag.dither_step(expected_dither_values[n]),
                DlnirspTag.mosaic_tile_x(expected_X_tile_values[n]),
                DlnirspTag.mosaic_tile_y(expected_Y_tile_values[n]),
            ]
        )
