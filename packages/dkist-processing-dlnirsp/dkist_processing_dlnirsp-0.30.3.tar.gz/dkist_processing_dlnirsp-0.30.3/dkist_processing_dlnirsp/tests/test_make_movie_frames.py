import pytest
from astropy.io import fits
from dkist_processing_common._util.scratch import WorkflowFileSystem

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.make_movie_frames import MakeDlnirspMovieFrames
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import write_calibrated_frames_to_task


@pytest.fixture
def make_movie_task(recipe_run_id, is_polarimetric, link_constants_db, tmp_path):
    dither_mode_on = True
    num_mosaics = 3
    num_X_tiles = 2
    num_Y_tiles = 1

    constants_db = DlnirspTestingConstants(
        NUM_MOSAIC_REPEATS=num_mosaics,
        NUM_MOSAIC_TILES_X=num_X_tiles,
        NUM_MOSAIC_TILES_Y=num_Y_tiles,
        NUM_DITHER_STEPS=int(dither_mode_on) + 1,
        POLARIMETER_MODE="Full Stokes" if is_polarimetric else "Stokes I",
    )
    link_constants_db(recipe_run_id, constants_db)

    with MakeDlnirspMovieFrames(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)

        yield task, num_mosaics, dither_mode_on, num_X_tiles, num_Y_tiles
        task._purge()


@pytest.mark.parametrize(
    "is_polarimetric",
    [pytest.param(True, id="polarimetric"), pytest.param(False, id="spectrographic")],
)
def test_make_movie_frames(
    make_movie_task, is_polarimetric, link_constants_db, mocker, fake_gql_client
):
    """
    Given: A Make Movie Frames task and some calibrated Science frames
    When: Running the task
    Then: The correct number of movie frames are produced and they have the correct shape (depending on polarimetric or not)
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task, num_mosaics, dither_mode_on, num_X_tiles, num_Y_tiles = make_movie_task

    num_dither = int(dither_mode_on) + 1
    wave_size = 3
    X_size = 4
    Y_size = 5
    write_calibrated_frames_to_task(
        task,
        num_mosaics=num_mosaics,
        num_X_tiles=num_X_tiles,
        num_Y_tiles=num_Y_tiles,
        is_polarimetric=is_polarimetric,
        array_shape=(wave_size, X_size, Y_size),
        dither_mode_on=dither_mode_on,
    )

    task()

    if is_polarimetric:
        expected_movie_frame_shape = (X_size * 2, Y_size * 2)
    else:
        expected_movie_frame_shape = (X_size, Y_size)

    all_movie_frames = list(task.read([DlnirspTag.movie_frame()]))
    assert len(all_movie_frames) == num_dither * num_mosaics * num_X_tiles * num_Y_tiles

    for mosaic in range(num_mosaics):
        for dither in range(num_dither):
            for X_tile in range(1, num_X_tiles + 1):
                for Y_tile in range(1, num_Y_tiles + 1):
                    single_frame = list(
                        task.read(
                            [
                                DlnirspTag.movie_frame(),
                                DlnirspTag.mosaic_num(mosaic),
                                DlnirspTag.dither_step(dither),
                                DlnirspTag.mosaic_tile_x(X_tile),
                                DlnirspTag.mosaic_tile_y(Y_tile),
                            ]
                        )
                    )
                    assert len(single_frame) == 1
                    hdul = fits.open(single_frame[0])
                    assert len(hdul) == 1
                    data = hdul[0].data
                    assert data.shape == expected_movie_frame_shape
