:orphan:

Examples
========

Learn how to use braindecode by the examples. There are several ways to learn and understand how a library works. Here at braindecode, we encourage hands-on mode.

See which tutorial best fits the approach you want and try to reproduce it on the examples data or on your data :)



.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. thumbnail-parent-div-close

.. raw:: html

    </div>


Basic model building and training
---------------------------------

Examples introducing fundamental model building and training strategies.



.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="The braindecode library gives you access to a large number of neural network architectures that were developed for EEG data decoding. This tutorial will show you how you can easily use any of these models to decode your own data. In particular, we assume that have your data in an MNE format and want to train one of the Braindecode models on it.">

.. only:: html

  .. image:: /auto_examples/model_building/images/thumb/sphx_glr_plot_basic_training_epochs_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_model_building_plot_basic_training_epochs.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Simple training on MNE epochs</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Cropped Decoding on BCIC IV 2a Dataset">

.. only:: html

  .. image:: /auto_examples/model_building/images/thumb/sphx_glr_plot_bcic_iv_2a_moabb_cropped_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_model_building_plot_bcic_iv_2a_moabb_cropped.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Cropped Decoding on BCIC IV 2a Dataset</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This tutorial shows you how to train and test deep learning models with Braindecode in a classical EEG setting: you have trials of data with labels (e.g., Right Hand, Left Hand, etc.).">

.. only:: html

  .. image:: /auto_examples/model_building/images/thumb/sphx_glr_plot_bcic_iv_2a_moabb_trial_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_model_building_plot_bcic_iv_2a_moabb_trial.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Basic Brain Decoding on EEG Data</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This tutorial shows you how to properly train, tune and test your deep learning models with Braindecode. We will use the BCIC IV 2a dataset [1]_ as a showcase example.">

.. only:: html

  .. image:: /auto_examples/model_building/images/thumb/sphx_glr_plot_how_train_test_and_tune_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_model_building_plot_how_train_test_and_tune.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">How to train, test and tune your model?</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="The braindecode provides some compatibility with `&lt;scikit-learn_&gt;`_. This allows us to use scikit-learn functionality to find the best hyperparameters for our model. This is especially useful to tune hyperparameters or parameters for one decoding task or a specific dataset.">

.. only:: html

  .. image:: /auto_examples/model_building/images/thumb/sphx_glr_plot_hyperparameter_tuning_with_scikit-learn_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_model_building_plot_hyperparameter_tuning_with_scikit-learn.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Hyperparameter tuning with scikit-learn</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to create a CNN regressor from a CNN classifier by removing softmax function from the classifier&#x27;s output layer and how to train it on a fake regression dataset.">

.. only:: html

  .. image:: /auto_examples/model_building/images/thumb/sphx_glr_plot_regression_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_model_building_plot_regression.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Convolutional neural network regression model on fake data.</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This tutorial shows you how to train a Braindecode model with PyTorch. The data preparation and model instantiation steps are identical to that of the tutorial train-test-tune-model.">

.. only:: html

  .. image:: /auto_examples/model_building/images/thumb/sphx_glr_plot_train_in_pure_pytorch_and_pytorch_lightning_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_model_building_plot_train_in_pure_pytorch_and_pytorch_lightning.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Training a Braindecode model in PyTorch</div>
    </div>


.. thumbnail-parent-div-close

.. raw:: html

    </div>


Loading and organizing data
---------------------------

Examples introducing data loading and basic data processing.



.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="In this example, we compare the execution time and memory requirements of 1) eager loading, i.e., preloading the entire data into memory and 2) lazy loading, i.e., only loading examples from disk when they are required. We also include some other experiment parameters in the comparison for the sake of completeness (e.g., num_workers, cuda, batch_size, etc.).">

.. only:: html

  .. image:: /auto_examples/datasets_io/images/thumb/sphx_glr_benchmark_lazy_eager_loading_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_datasets_io_benchmark_lazy_eager_loading.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Benchmarking eager and lazy loading</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="In this example, we compare the execution time and memory requirements of preprocessing data with the parallelization and serialization functionalities available in braindecode.preprocessing.preprocess.">

.. only:: html

  .. image:: /auto_examples/datasets_io/images/thumb/sphx_glr_plot_benchmark_preprocessing_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_datasets_io_plot_benchmark_preprocessing.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Benchmarking preprocessing with parallelization and serialization</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="In this example, we show how to fetch and prepare a BIDS dataset for usage with Braindecode.">

.. only:: html

  .. image:: /auto_examples/datasets_io/images/thumb/sphx_glr_plot_bids_dataset_example_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_datasets_io_plot_bids_dataset_example.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">BIDS Dataset Example</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to convert data X and y as numpy arrays to a braindecode compatible data format.">

.. only:: html

  .. image:: /auto_examples/datasets_io/images/thumb/sphx_glr_plot_custom_dataset_example_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_datasets_io_plot_custom_dataset_example.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Custom Dataset Example</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="In this example, we show how to load and save braindecode datasets.">

.. only:: html

  .. image:: /auto_examples/datasets_io/images/thumb/sphx_glr_plot_load_save_datasets_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_datasets_io_plot_load_save_datasets.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Load and save dataset example</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="MNE Dataset Example">

.. only:: html

  .. image:: /auto_examples/datasets_io/images/thumb/sphx_glr_plot_mne_dataset_example_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_datasets_io_plot_mne_dataset_example.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">MNE Dataset Example</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="In this example, we show how to fetch and prepare a MOABB dataset for usage with Braindecode.">

.. only:: html

  .. image:: /auto_examples/datasets_io/images/thumb/sphx_glr_plot_moabb_dataset_example_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_datasets_io_plot_moabb_dataset_example.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">MOABB Dataset Example</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="In this example, we aim to show multiple ways of how you can split your datasets for training, testing, and evaluating your models.">

.. only:: html

  .. image:: /auto_examples/datasets_io/images/thumb/sphx_glr_plot_split_dataset_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_datasets_io_plot_split_dataset.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Split Dataset Example</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Welcome to this tutorial where we demonstrate how to work with multiple discrete targets for each recording in the TUH EEG Corpus. We&#x27;ll guide you through the process step by step.">

.. only:: html

  .. image:: /auto_examples/datasets_io/images/thumb/sphx_glr_plot_tuh_discrete_multitarget_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_datasets_io_plot_tuh_discrete_multitarget.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Multiple discrete targets with the TUH EEG Corpus</div>
    </div>


.. thumbnail-parent-div-close

.. raw:: html

    </div>


Advanced neural network training strategies
-------------------------------------------

Examples explaining more advanced topics in neural network training strategies.



.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This tutorial shows you how to train and test deep learning models with Braindecode on ECoG BCI IV competition dataset 4 using cropped mode. For this dataset we will predict 5 regression targets corresponding to flexion of each finger. The targets were recorded as a time series (each 25 Hz), so this tutorial is an example of time series target prediction.">

.. only:: html

  .. image:: /auto_examples/advanced_training/images/thumb/sphx_glr_bcic_iv_4_ecog_cropped_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_advanced_training_bcic_iv_4_ecog_cropped.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Fingers flexion cropped decoding on BCIC IV 4 ECoG Dataset</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This tutorial shows how to train EEG deep models with data augmentation. It follows the trial-wise decoding example and also illustrates the effect of a transform on the input signals.">

.. only:: html

  .. image:: /auto_examples/advanced_training/images/thumb/sphx_glr_plot_data_augmentation_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_advanced_training_plot_data_augmentation.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Data Augmentation on BCIC IV 2a Dataset</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This tutorial shows how to search data augmentations using braindecode. Indeed, it is known that the best augmentation to use often dependent on the task or phenomenon studied. Here we follow the methodology proposed in [1]_ on the openly available BCI IV 2a Dataset.">

.. only:: html

  .. image:: /auto_examples/advanced_training/images/thumb/sphx_glr_plot_data_augmentation_search_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_advanced_training_plot_data_augmentation_search.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Searching the best data augmentation on BCIC IV 2a Dataset</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Cross-session motor imagery with deep learning EEGNet v4 model">

.. only:: html

  .. image:: /auto_examples/advanced_training/images/thumb/sphx_glr_plot_moabb_benchmark_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_advanced_training_plot_moabb_benchmark.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Cross-session motor imagery with deep learning EEGNet v4 model</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to train a neural network with self-supervision on sleep EEG data. We follow the relative positioning approach of [1]_ on the openly accessible Sleep Physionet dataset [2]_ [3]_.">

.. only:: html

  .. image:: /auto_examples/advanced_training/images/thumb/sphx_glr_plot_relative_positioning_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_advanced_training_plot_relative_positioning.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Self-supervised learning on EEG with relative positioning</div>
    </div>


.. thumbnail-parent-div-close

.. raw:: html

    </div>


Applied examples on real-world datasets
---------------------------------------

Examples demonstrating analaysis of EEG on data from clinical studies, sleep & cognitive experiments.



.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This tutorial shows you how to train and test deep learning models with Braindecode on ECoG BCI IV competition dataset 4. For this dataset we will predict 5 regression targets corresponding to flexion of each finger. The targets were recorded as a time series (each 25 Hz), so this tutorial is an example of time series target prediction.">

.. only:: html

  .. image:: /auto_examples/applied_examples/images/thumb/sphx_glr_bcic_iv_4_ecog_trial_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_applied_examples_bcic_iv_4_ecog_trial.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Fingers flexion decoding on BCIC IV 4 ECoG Dataset</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This tutorial shows how to train and test a sleep staging neural network with Braindecode. We adapt the time distributed approach of [1]_ to learn on sequences of EEG windows using the openly accessible Sleep Physionet dataset [2]_ [3]_.">

.. only:: html

  .. image:: /auto_examples/applied_examples/images/thumb/sphx_glr_plot_sleep_staging_chambon2018_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_applied_examples_plot_sleep_staging_chambon2018.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Sleep staging on the Sleep Physionet dataset using Chambon2018 network</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This tutorial shows how to train and test a sleep staging neural network with Braindecode. We use the attention-based model from [1]_ with the time distributed approach of [2]_ to learn on sequences of EEG windows using the openly accessible Sleep Physionet dataset [3]_ [4]_.">

.. only:: html

  .. image:: /auto_examples/applied_examples/images/thumb/sphx_glr_plot_sleep_staging_eldele2021_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_applied_examples_plot_sleep_staging_eldele2021.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Sleep staging on the Sleep Physionet dataset using Eldele2021</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This tutorial shows how to train and test a sleep staging neural network with Braindecode. We adapt the U-Sleep approach of [1]_ to learn on sequences of EEG windows using the openly accessible Sleep Physionet dataset [2]_ [3]_.">

.. only:: html

  .. image:: /auto_examples/applied_examples/images/thumb/sphx_glr_plot_sleep_staging_usleep_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_applied_examples_plot_sleep_staging_usleep.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Sleep staging on the Sleep Physionet dataset using U-Sleep network</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="In this example, we showcase usage of the Temple University Hospital EEG Corpus (https://isip.piconepress.com/projects/nedc/html/tuh_eeg/) including simple preprocessing steps as well as cutting of compute windows.">

.. only:: html

  .. image:: /auto_examples/applied_examples/images/thumb/sphx_glr_plot_tuh_eeg_corpus_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_applied_examples_plot_tuh_eeg_corpus.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Process a big data EEG resource (TUH EEG Corpus)</div>
    </div>


.. thumbnail-parent-div-close

.. raw:: html

    </div>


.. toctree::
   :hidden:
   :includehidden:


   /auto_examples/model_building/index.rst
   /auto_examples/datasets_io/index.rst
   /auto_examples/advanced_training/index.rst
   /auto_examples/applied_examples/index.rst


.. only:: html

  .. container:: sphx-glr-footer sphx-glr-footer-gallery

    .. container:: sphx-glr-download sphx-glr-download-python

      :download:`Download all examples in Python source code: auto_examples_python.zip </auto_examples/auto_examples_python.zip>`

    .. container:: sphx-glr-download sphx-glr-download-jupyter

      :download:`Download all examples in Jupyter notebooks: auto_examples_jupyter.zip </auto_examples/auto_examples_jupyter.zip>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_
