Test Writing Guidelines
=======================

This document is intended to discuss common patterns used in the unit-test suite. It is intended to only provide general
guidelines; it's a useful starting (and maybe ending!) point, but shouldn't be treated as gospel.

Header Generators
-----------------

"header_models.py" contains many `VispHeaders*` classes. These are all subclasses of `dkist-data-simulator`'s `Spec122Dataset`
and are designed to leverage many of that class' neat features. In particular, each class produces a *complete* and
*correct* set of frames of the given type. By "complete" we mean that they generate the smallest set of files that covers
the all the instrument loops that are relevant for that task type. For most of the calibration task-types this just means
they loop over modstate, but for OBSERVE and POLCAL task-types there are many more loops (e.g., map scan, cs step, etc.).
By "correct" we mean that the header for each individual frame will be correct given that frame's place in the nest of
instrument loops.

To demonstrate a simple example, consider creating a set of LAMP_GAIN frames for a dataset that has 4 modstates:

.. code-block:: python

  >>> dataset = VispHeadersInputLampGainFrames(array_shape=(1, 10, 10), time_delta=10., num_modstates=4)
  >>> [frame.header()["VISP_011"] for frame in dataset]
  [1, 2, 3, 4]

We have produced 4 separate headers and the current modstate (VISP_011) correctly increases for each one.

Generating Data and Files
^^^^^^^^^^^^^^^^^^^^^^^^^

The usage of these data generator classes is closely tied to `write_frames_to_task` in conftest.py. This function
accepts a task and data generator class and iterates through all frames in the generator, writing a new file to the task
scratch location for each. The default is to write a random array and only tag with FRAME, but this behavior can be changed
with the `extra_tags`, `data_func`, and `tag_func` args. Both the `data_func` and `tag_func` are expected to have a single
argument that is a `VispHeader*` data generator class and return a numpy array or list of tags, respectively. To build
upon the previous example, if we wanted to have each LAMP_GAIN frame have an array value equal to its current modstate and
also be tagged as a LAMP_GAIN with the correct MODSTATE tag then we would write something like this

.. code-block:: python

 >>> def mod_data_func(frame):
 >>>   modstate = frame.header()["VISP_011"]
 >>>   array_shape = frame.array_shape
 >>>   return np.ones(array_shape) * modstate
 >>>
 >>> def tag_on_modstate(frame):
 >>>   modstate = frame.header()["VISP_011"]
 >>>   return [VispTag.modstate(modstate)]
 >>>
 >>> write_frames_to_task(task=task, frame_generator=dataset,
                          extra_tags=[VispTag.task_lamp_gain()], data_func=mod_data_func, tag_func=tag_on_modstate)

By using these fully-featured data generator classes we can avoid explicit loops inside our tests fixtures.

Another tip is that it's fairly straight-forward to subclass an existing data generator if you need more specific control
over the headers (for example, to create "bad" data). Generally, if you find yourself modifying the headers explicitly
after generation then you might think of how you could make a data generator class that produces the headers you want
in the first place.


Task Fixtures
-------------

Often (always?) our tests require a "test" version of a specific Task class. By "test" we mean a Task class that has
been instantiated as if it were running as part of a real pipeline (or at least close enough that any tests can run).
In most cases this involves building a Task class with three things: **data**, **constants**, and **parameters**. We
will dive into each of these, but first let's establish the most basic pattern of writing a Task fixture. The way we
currently make an essentially useless task (i.e., it has none of the three things mentioned above) is like this
(we'll use `DarkCalibration` just as an example):

.. code-block:: python

  @pytest.fixture
  def dark_calibration_task(recipe_run_id):
      with DarkCalibration(
          recipe_run_id=recipe_run_id,
          workflow_name="dark_calibration",
          workflow_version="vX.Y",
      ) as task:
          yield task
          task._purge()

Here we've instantiated the `DarkCalibration` task with a dummy `recipe_run_id` and yielded it from the fixture. The
`yield` and `_purge()` ensure that the task is correctly cleaned up after the testing is done. Note that this fixture
won't actually work due to interactions between constants and parameters; it is just here to show the bare skeleton of
a Task fixture.

Adding Data
^^^^^^^^^^^

The data generators described above provide an easy way to write whatever data we want, but we still need somewhere to
put it. This means we need to define a "scratch" location for our Task. In pipeline language, the Task needs a
`WorkflowFileSystem`. This is easy to add; just assign one to the Task's `.scratch` property:

.. code-block:: python

  @pytest.fixture
  def dark_calibration_task(
      recipe_run_id,
      tmp_path,
  ):
      with DarkCalibration(
          recipe_run_id=recipe_run_id,
          workflow_name="dark_calibration",
          workflow_version="vX.Y",
      ) as task:
          task.scratch = WorkflowFileSystem(
              scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
          )
          yield task
          task._purge()

Now we can use, e.g., `task.write()` and the data will end up somewhere controlled by `pytest` (and therefore be cleaned
up correctly).

.. note::
  While assigning `task.scratch` in the fixture is what allows use to easily write data to a task, we should **NOT**
  actually write any data in the Task fixture. Test data setup should happen *in the test itself*. This has two benefits:
  it keeps the Task fixture *light* and *general*, and it moves data generation to where it is actually used, which is
  easier to read and maintain.

Adding Constants
^^^^^^^^^^^^^^^^

To add constants to a test Task we need two things: 1) A `dataclass` that contains the constant values we want, and 2)
the `init_visp_constants_db` fixture that creates the actual database and links it to a given task. The usage looks like
this:

.. code-block:: python

  @pytest.fixture
  def dark_calibration_task(
      recipe_run_id,
      tmp_path,
      init_visp_constants_db,
  ):
      constants_db = VispConstantsDb()
      init_visp_constants_db(recipe_run_id, constants_db)
      with DarkCalibration(
          recipe_run_id=recipe_run_id,
          workflow_name="dark_calibration",
          workflow_version="vX.Y",
      ) as task:
          task.scratch = WorkflowFileSystem(
              scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
          )
          yield task
          task._purge()

The `VispConstantsDb` dataclass from "conftest.py" contains all constants used in the pipeline and you can make the values
whatever you want when it's instantiated (e.g., `constants_db = VispConstantsDb(NUM_MODSTATES=2)`).

Note that we have linked the constants db to the task (via `recipe_run_id`) *before* actually instantiating the Task class
itself. This is necessary because all ViSP science tasks need to have populated constants to initialize their `.parameter`
property, which happens on instantiation.

Adding Parameters
^^^^^^^^^^^^^^^^^

Much like constants, to add parameters to a test Task we need two things: 1) A `dataclass` contatining the parameter
values we want, and 2) the `assign_input_dataset_doc_to_task` fixture to actually assign the parameters to a task:

.. code-block:: python

  @pytest.fixture
  def dark_calibration_task(
      recipe_run_id,
      tmp_path,
      init_visp_constants_db,
      assign_input_dataset_doc_to_task,
  ):
      constants_db = VispConstantsDb()
      init_visp_constants_db(recipe_run_id, constants_db)
      with DarkCalibration(
          recipe_run_id=recipe_run_id,
          workflow_name="dark_calibration",
          workflow_version="vX.Y",
      ) as task:
          task.scratch = WorkflowFileSystem(
              scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
          )
          assign_input_dataset_doc_to_task(task, VispTestingParameterValues())
          yield task
          task._purge()

The `VispTestingParameterValues` dataclass in "conftest.py" contains all parameters used by the pipeline and can be
initialized with any custom values you want.

Note an important distinction between how constants and parameters are initialized is that `init_visp_constants_db`
gets linked to a task via the `recipe_run_id`, while `assign_input_dataset_doc_to_task` actually takes the instantiated
Task as an argument. A consequence is that `assign_input_dataset_doc_to_task` can happen only *after* a task is instantiated.

Common Patterns
---------------

Following these guidelines won't guarantee success, but may help you set off in the right direction.

Don't Write Data in Task Fixtures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Don't write data in Task fixtures; do it in the test instead. The final Task fixture shown above is *just about* as
complicated as any Task fixture should ever be. There are, of course, exceptions, but it is almost always better to
write needed data to a task inside the actual test itself.

Assign Parameters in Tests if They are Test Dependent
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Assign parameters in actual tests if they are different for different tests. The beauty of a simple Task fixture is that
it can be used for multiple tests. If these tests all use the same parameter values then it's fine to just call
`assign_input_dataset_doc_to_task` once in the Task fixture. If each test needs a different set of parameter values then
you can easily call `assign_input_dataset_doc_to_task` in the test itself.

Constants NEED to be Linked Prior to Task Instantiation But Can Be Modified After the Fact
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Constants *need* to be linked prior to task instantiation, but they can be modified later if needed. Thus, if you have
multiple tests that need different values for constants you can still use the same Task fixture and then call
`init_visp_constants_db` again in the actual test. Every time `init_visp_constants_db` is called it first wipes the old
constant values and then replaces them with whatever new ones you've specified.

An Example
^^^^^^^^^^

Here is a set of example tests showing usage of all the patterns discussed above:

.. code-block:: python

  @pytest.fixture
  def dark_calibration_task(
      recipe_run_id,
      tmp_path,
      init_visp_constants_db,
      assign_input_dataset_doc_to_task,
  ):
      # Constants *need* to be linked prior to task instantiation
      constants_db = VispConstantsDb()
      init_visp_constants_db(recipe_run_id, constants_db)
      with DarkCalibration(
          recipe_run_id=recipe_run_id,
          workflow_name="dark_calibration",
          workflow_version="vX.Y",
      ) as task:
          task.scratch = WorkflowFileSystem(
              scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
          )

          # We'll assign the parameters here because they don't change in the different tests
          assign_input_dataset_doc_to_task(task, VispTestingParameterValues())
          yield task
          task._purge()

  def test_thing_1(dark_calibration_task, init_visp_constants_db):

      task = dark_calibration_task

      # This test needs some unique constants
      init_visp_constants_db(task.recipe_run_id, VispConstantsDb(NON_DARK_TASK_READOUT_EXP_TIMES=(10.,)))

      assert True

  def test_thing_2(dark_calibration_task):

      # Default constants are OK for this test
      task = dark_calibration_task

      # Write some lamp frames (see the first section for detailed explanation)
      lamp_data_generator = VispHeadersInputLampGainFrames(array_shape=(10, 10), time_delta=10., num_modstates=4)
      num_lamp_frames = write_frames_to_task(task=task,
                                             frame_generator=lamp_data_generator,
                                             extra_tags=[VispTag.task_lamp_gain(), VispTag.input()],
                                             tag_func=tag_on_modstate,
                                             data_func=mod_data_func)

      assert num_lamp_frames == 4  # This will pass
