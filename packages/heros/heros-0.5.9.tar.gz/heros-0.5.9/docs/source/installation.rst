Installation
############

Installing HEROS is as simple as doing

.. code:: console

    pip install heros

It will automatically install the few requirements that HEROS has (mainly eclipse-zenoh) and you are ready to create your first own HERO.

If alternatively, you prefer to keep everything neatly inside a docker container you can run

.. code:: console

    docker run -it --network host registry.gitlab.com/atomiq-project/heros /usr/local/bin/python