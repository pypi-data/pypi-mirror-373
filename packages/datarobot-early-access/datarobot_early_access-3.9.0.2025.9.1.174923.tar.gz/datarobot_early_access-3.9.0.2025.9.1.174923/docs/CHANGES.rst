#########
Changelog
#########
3.2.0b0
========

New Features
************
 - Added the ability to share deployments. See :ref:`deployment sharing <deployment_sharing>` for more information on sharing deployments.

 - Added new methods get_bias_and_fairness_settings and update_bias_and_fairness_settings to retrieve or update bias and fairness settings
   :meth:`Deployment.get_bias_and_fairness_settings<datarobot.models.Deployment.get_bias_and_fairness_settings>`
   :meth:`Deployment.update_bias_and_fairness_settings<datarobot.models.Deployment.update_bias_and_fairness_settings>`

- Updated methods in :class:`Model <datarobot.models.model.Model>` to support use of Sliced Insights:
  :meth:`Model.get_multiclass_lift_chart <datarobot.models.Model.get_multiclass_lift_chart>`
  :meth:`Model.get_all_multiclass_lift_charts <datarobot.models.Model.get_all_multiclass_lift_charts>`

Enhancements
************
- Improve error message of :meth:`SampleImage.list<datarobot.models.visualai.SampleImage.list>`
  to clarify that a selected parameter cannot be used when a project has not proceeded to the
  correct stage prior to calling this method.

- Extended :meth:`SampleImage.list<datarobot.models.visualai.SampleImage.list>` by two parameters
  to filter for a target value range in regression projects.

- Added text explanations data to :meth:`PredictionExplanations <datarobot.PredictionExplanations>`

Bugfixes
********

API Changes
***********

Deprecation Summary
*******************

Configuration Changes
*********************

Documentation Changes
*********************

Experimental changes
*********************
- Added experimental support for data matching:

  - :class:`DataMatching <datarobot._experimental.models.data_matching.DataMatching>`
  - :class:`DataMatchingQuery <datarobot._experimental.models.data_matching.DataMatchingQuery>`

3.1.0
=====

New Features
************

Enhancements
************
- Added new methods :meth:`BatchPredictionJob.apply_time_series_data_prep_and_score<datarobot.models.BatchPredictionJob.apply_time_series_data_prep_and_score>`
  and :meth:`BatchPredictionJob.apply_time_series_data_prep_and_score_to_file<datarobot.models.BatchPredictionJob.apply_time_series_data_prep_and_score_to_file>`
  that apply time series data prep to a file or dataset and make batch predictions with a deployment.
- Added new methods :meth:`DataEngineQueryGenerator.prepare_prediction_dataset<datarobot.DataEngineQueryGenerator.prepare_prediction_dataset>`
  and :meth:`DataEngineQueryGenerator.prepare_prediction_dataset_from_catalog<datarobot.DataEngineQueryGenerator.prepare_prediction_dataset_from_catalog>`
  that apply time series data prep to a file or catalog dataset and upload the prediction dataset to a
  project.
- Added new `max_wait` parameter to method :meth:`Project.create_from_dataset<datarobot.models.Project.create_from_dataset>`.
  Values larger than the default can be specified to avoid timeouts when creating a project from Dataset.

- Added new method for creating a segmented modeling project from an existing clustering project and model
  :meth:`Project.create_segmented_project_from_clustering_model<datarobot.models.Project.create_segmented_project_from_clustering_model>`.
  Please switch to this function if you are previously using ModelPackage for segmented modeling purposes.

- Added new method is_unsupervised_clustering_or_multiclass for checking whether the clustering or multiclass parameters are used, quick and efficient without extra API calls.
  :meth:`PredictionExplanations.is_unsupervised_clustering_or_multiclass <datarobot.PredictionExplanations.is_unsupervised_clustering_or_multiclass>`

- Retry idempotent requests which result in HTTP 502 and HTTP 504 (in addition to the previous HTTP 413, HTTP 429 and HTTP 503)

- Added value PREPARED_FOR_DEPLOYMENT to the RECOMMENDED_MODEL_TYPE enum

- Added two new methods to the ImageAugmentationList class:
  :meth:`ImageAugmentationList.list<datarobot.models.visualai.ImageAugmentationList.list>`,
  :meth:`ImageAugmentationList.update<datarobot.models.visualai.ImageAugmentationList.update>`

Bugfixes
********
- Added `format` key to Batch Prediction intake and output settings for S3, GCP and Azure

API Changes
***********
- The method :meth:`PredictionExplanations.is_multiclass <datarobot.PredictionExplanations.is_multiclass>` now adds an additional API call to check for multiclass target validity, which adds a small delay.
- :class:`AdvancedOptions <datarobot.helpers.AdvancedOptions>` parameter ``blend_best_models`` defaults to false
- :class:`AdvancedOptions <datarobot.helpers.AdvancedOptions>` parameter ``consider_blenders_in_recommendation`` defaults to false
- :class:`DatetimePartitioning <datarobot.DatetimePartitioning>` has parameter ``unsupervised_mode``

Deprecation Summary
*******************
- Deprecated method :meth:`Project.create_from_hdfs<datarobot.models.Project.create_from_hdfs>`.
- Deprecated method :meth:`DatetimePartitioning.generate <datarobot.DatetimePartitioning.generate>`.
- Deprecated parameter ``in_use`` from :meth:`ImageAugmentationList.create<datarobot.models.visualai.ImageAugmentationList.create>` as DataRobot will take care of it automatically.
- Deprecated property ``Deployment.capabilities`` from :class:`Deployment <datarobot.models.Deployment>`.
- ``ImageAugmentationSample.compute`` was removed in v3.1. You
  can get the same information with the method ``ImageAugmentationList.compute_samples``.
- ``sample_id`` parameter removed from ``ImageAugmentationSample.list``. Please use ``auglist_id`` instead.

Configuration Changes
*********************

Experimental changes
*********************
- Added :meth:`DatetimePartitioning.datetime_partitioning_log_retrieve <datarobot._experimental.helpers.partitioning_methods.DatetimePartitioning.datetime_partitioning_log_retrieve>` to download the datetime partitioning log.

- Added :meth:`DatetimePartitioning.get_input_data <datarobot._experimental.helpers.partitioning_methods.DatetimePartitioning.get_input_data>` to retrieve the input data used to create an optimized datetime partitioning.

- Added :class:`DatetimePartitioningId <datarobot._experimental.helpers.partitioning_methods.DatetimePartitioningId>`, which can be passed as a `partitioning_method` to :meth:`Project.analyze_and_model <datarobot.models.Project.analyze_and_model>`.

Documentation Changes
*********************
- Update the documentation to suggest that setting `use_backtest_start_end_format` of :py:meth:`DatetimePartitioning.to_specification <datarobot.DatetimePartitioning.to_specification>` to `True` will mirror the same behavior as the Web UI.

- Update the documentation to suggest setting `use_start_end_format` of :py:meth:`Backtest.to_specification <datarobot.helpers.partitioning_methods.Backtest.to_specification>` to `True` will mirror the same behavior as the Web UI.

3.0.3
=====

Bugfixes
********
- Fixed an issue affecting backwards compatibility in :class:`datarobot.models.DatetimeModel`, where an unexpected keyword from the DataRobot API would break class deserialization.

3.0.2
=====

Bugfixes
********
- Restored :meth:`Model.get_leaderboard_ui_permalink <datarobot.models.Model.get_leaderboard_ui_permalink>`, :meth:`Model.open_model_browser <datarobot.models.Model.open_model_browser>`,
  :meth:`Project.get_leaderboard_ui_permalink <datarobot.models.Project.get_leaderboard_ui_permalink>`, and :meth:`Project.open_leaderboard_browser <datarobot.models.Project.open_leaderboard_browser>`.
  These methods were accidentally removed instead of deprecated.
- Fix for ipykernel < 6.0.0 which does not persist contextvars across cells

Deprecation Summary
*******************
- Deprecated method :meth:`Model.get_leaderboard_ui_permalink <datarobot.models.Model.get_leaderboard_ui_permalink>`. Please use :meth:`Model.get_uri <datarobot.models.Model.get_uri>` instead.
- Deprecated method :meth:`Model.open_model_browser <datarobot.models.Model.open_model_browser>`. Please use :meth:`Model.open_in_browser <datarobot.models.Model.open_in_browser>` instead.
- Deprecated method :meth:`Project.get_leaderboard_ui_permalink <datarobot.models.Project.get_leaderboard_ui_permalink>`. Please use :meth:`Project.get_uri <datarobot.models.Project.get_uri>` instead.
- Deprecated method :meth:`Project.open_leaderboard_browser <datarobot.models.Project.open_leaderboard_browser>`. Please use :meth:`Project.open_in_browser <datarobot.models.Project.open_in_browser>` instead.

3.0.1
=====

Bugfixes
********
- Added `typing-extensions` as a required dependency for the DataRobot Python SDK.

3.0.0
=====

New Features
************
- Version 3.0 of the Python client does not support Python 3.6 and earlier versions. Version 3.0 currently supports Python 3.7+.

- The default Autopilot mode for :meth:`project.start_autopilot <datarobot.models.Project.start_autopilot>` has changed to Quick mode.

- For datetime-aware models, you can now calculate and retrieve feature impact for backtests other than zero and holdout:

  - :meth:`DatetimeModel.get_feature_impact <datarobot.models.DatetimeModel.get_feature_impact>`
  - :meth:`DatetimeModel.request_feature_impact <datarobot.models.DatetimeModel.request_feature_impact>`
  - :meth:`DatetimeModel.get_or_request_feature_impact <datarobot.models.DatetimeModel.get_or_request_feature_impact>`

- Added a ``backtest`` field to feature impact metadata: :meth:`Model.get_or_request_feature_impact <datarobot.models.Model.get_feature_impact>`. This field is null for non-datetime-aware models and greater than or equal to zero for holdout in datetime-aware models.

- You can use a new method to retrieve the canonical URI for a project, model, deployment, or dataset:

  - :meth:`Project.get_uri <datarobot.models.Project.get_uri>`
  - :meth:`Model.get_uri <datarobot.models.Model.get_uri>`
  - :meth:`Deployment.get_uri <datarobot.models.Deployment.get_uri>`
  - :meth:`Dataset.get_uri <datarobot.models.Dataset.get_uri>`

- You can use a new method to open a class in a browser based on their URI (project, model, deployment, or dataset):

  - :meth:`Project.open_in_browser <datarobot.models.Project.open_in_browser>`
  - :meth:`Model.open_in_browser <datarobot.models.Model.open_in_browser>`
  - :meth:`Deployment.open_in_browser <datarobot.models.Deployment.open_in_browser>`
  - :meth:`Dataset.open_in_browser <datarobot.models.Dataset.open_in_browser>`

- Added a new method for opening DataRobot in a browser: :meth:`datarobot.rest.RESTClientObject.open_in_browser`. Invoke the method via ``dr.Client().open_in_browser()``.

- Altered method :meth:`Project.create_featurelist <datarobot.models.Project.create_featurelist>` to accept five new parameters (please see documentation for information about usage):

  - ``starting_featurelist``
  - ``starting_featurelist_id``
  - ``starting_featurelist_name``
  - ``features_to_include``
  - ``features_to_exclude``

- Added a new method to retrieve a feature list by name: :meth:`Project.get_featurelist_by_name <datarobot.models.Project.get_featurelist_by_name>`.

- Added a new convenience method to create datasets: :meth:`Dataset.upload <datarobot.models.Dataset.upload>`.

- Altered the method :meth:`Model.request_predictions <datarobot.models.Model.request_predictions>` to accept four new parameters:

  - ``dataset``
  - ``file``
  - ``file_path``
  - ``dataframe``
  - Note that the method already supports the parameter ``dataset_id`` and all data source parameters are mutually exclusive.

- Added a new method to :class:`datarobot.models.Dataset`, :meth:`Dataset.get_as_dataframe <datarobot.models.Dataset.get_as_dataframe>`, which retrieves all the originally uploaded data in a pandas DataFrame.

- Added a new method to :class:`datarobot.models.Dataset`, :meth:`Dataset.share <datarobot.models.Dataset.share>`, which allows the sharing of a dataset with another user.

- Added new convenience methods to :class:`datarobot.models.Project` for dealing with partition classes. Both methods should be called before :meth:`Project.analyze_and_model <datarobot.models.Project.analyze_and_model>`.
  - :meth:`Project.set_partitioning_method <datarobot.models.Project.set_partitioning_method>` intelligently creates the correct partition class for a regular project, based on input arguments.
  - :meth:`Project.set_datetime_partitioning <datarobot.models.Project.set_datetime_partitioning>` creates the correct partition class for a time series project.

- Added a new method to :class:`datarobot.models.Project` :meth:`Project.get_top_model <datarobot.models.Project.get_top_model>` which returns the highest scoring model for a metric of your choice.

- Use the new method :meth:`Deployment.predict_batch <datarobot.models.Deployment.predict_batch>` to pass a file, file path, or DataFrame to :class:`datarobot.models.Deployment` to easily make batch predictions and return the results as a DataFrame.

- Added support for passing in a credentials ID or credentials data to :meth:`Project.create_from_data_source <datarobot.models.Project.create_from_data_source>` as an alternative to providing a username and password.

- You can now pass in a `max_wait` value to :meth:`AutomatedDocument.generate <datarobot.models.automated_documentation.AutomatedDocument.generate>`.

- Added a new method to :class:`datarobot.models.Project` :meth:`Project.get_dataset <datarobot.models.Project.get_dataset>` which retrieves the dataset used during creation of a project.

- Added two new properties to :class:`datarobot.models.Project`:
  - ``catalog_id``
  - ``catalog_version_id``

- Added a new Autopilot method to :class:`datarobot.models.Project` :meth:`Project.analyze_and_model <datarobot.models.Project.analyze_and_model>` which allows you to initiate Autopilot or data analysis against data uploaded to DataRobot.

- Added a new convenience method to :class:`datarobot.models.Project` :meth:`Project.set_options <datarobot.models.Project.set_options>` which allows you to save :py:class:`AdvancedOptions <datarobot.helpers.AdvancedOptions>` values for use in modeling.

- Added a new convenience method to :class:`datarobot.models.Project` :meth:`Project.get_options <datarobot.models.Project.get_options>` which allows you to retrieve saved modeling options.

Enhancements
************
- Refactored the global singleton client connection (:meth:`datarobot.client.Client`) to use ContextVar instead of a global variable for better concurrency support.
- Added support for creating monotonic feature lists for time series projects. Set ``skip_datetime_partition_column`` to
  True to create monotonic feature list. For more information see :meth:`datarobot.models.Project.create_modeling_featurelist`.
- Added information about vertex to advanced tuning parameters :meth:`datarobot.models.Model.get_advanced_tuning_parameters`.
- Added the ability to automatically use saved :py:class:`AdvancedOptions <datarobot.helpers.AdvancedOptions>` set using :meth:`Project.set_options <datarobot.models.Project.set_options>` in :meth:`Project.analyze_and_model <datarobot.models.Project.analyze_and_model>`.

Bugfixes
********
- :meth:`Dataset.list <datarobot.models.Dataset.list>` no longer throws errors when listing datasets with no owner.
- Fixed an issue with the creation of ``BatchPredictionJobDefinitions`` containing a schedule.
- Fixed error handling in ``datarobot.helpers.partitioning_methods.get_class``.
- Fixed issue with portions of the payload not using camelCasing in :meth:`Project.upload_dataset_from_catalog<datarobot.models.Project.upload_dataset_from_catalog>`.

API Changes
***********
- The Python client now outputs a `DataRobotProjectDeprecationWarning` when you attempt to access certain resources (projects, models, deployments, etc.) that are deprecated or disabled as a result of the DataRobot platform's migration to Python 3.
- The Python client now raises a `TypeError` when you try to retrieve a labelwise ROC on a binary model or a binary ROC on a multilabel model.
- The method :meth:`Dataset.create_from_data_source<datarobot.models.Dataset.create_from_data_source>` now raises ``InvalidUsageError`` if ``username`` and ``password`` are not passed as a pair together.

Deprecation Summary
*******************
- ``Model.get_leaderboard_ui_permalink`` has been removed.
  Use :meth:`Model.get_uri <datarobot.models.Model.get_uri>` instead.
- ``Model.open_model_browser`` has been removed.
  Use :meth:`Model.open_in_browser <datarobot.models.Model.open_in_browser>` instead.
- ``Project.get_leaderboard_ui_permalink`` has been removed.
  Use :meth:`Project.get_uri <datarobot.models.Project.get_uri>` instead.
- ``Project.open_leaderboard_browser`` has been removed.
  Use :meth:`Project.open_in_browser <datarobot.models.Project.open_in_browser>` instead.
- Enum ``VARIABLE_TYPE_TRANSFORM.CATEGORICAL`` has been removed
- Instantiation of :class:`Blueprint <datarobot.models.Blueprint>` using a dict has been removed. Use :meth:`Blueprint.from_data <datarobot.models.Blueprint.from_data>` instead.
- Specifying an environment to use for testing with :class:`CustomModelTest <datarobot.CustomModelTest>` has been removed.
- :class:`CustomModelVersion <datarobot.CustomModelVersion>`'s ``required_metadata`` parameter has been removed. Use ``required_metadata_values`` instead.
- :class:`CustomTaskVersion <datarobot.CustomTaskVersion>`'s ``required_metadata`` parameter has been removed. Use ``required_metadata_values`` instead.
- Instantiation of :class:`Feature <datarobot.models.Feature>` using a dict has been removed. Use :meth:`Feature.from_data <datarobot.models.Feature.from_data>` instead.
- Instantiation of :class:`Featurelist <datarobot.models.Featurelist>` using a dict has been removed. Use :meth:`Featurelist.from_data <datarobot.models.Featurelist.from_data>` instead.
- Instantiation of :class:`Model <datarobot.models.Model>` using a dict, tuple, or the ``data`` parameter has been removed. Use :meth:`Model.from_data <datarobot.models.Model.from_data>` instead.
- Instantiation of :class:`Project <datarobot.models.Project>` using a dict has been removed. Use :meth:`Project.from_data <datarobot.models.Project.from_data>` instead.
- :class:`Project <datarobot.models.Project>`'s ``quickrun`` parameter has been removed. Pass ``AUTOPILOT_MODE.QUICK`` as the ``mode`` instead.
- :class:`Project <datarobot.models.Project>`'s ``scaleout_max_train_pct`` and ``scaleout_max_train_rows`` parameters have been removed.
- ``ComplianceDocumentation`` has been removed. Use :class:`AutomatedDocument <datarobot.models.automated_documentation.AutomatedDocument>` instead.
- The :class:`Deployment <datarobot.models.Deployment>` method ``create_from_custom_model_image`` was removed. Use :meth:`Deployment.create_from_custom_model_version <datarobot.models.Deployment.create_from_custom_model_version>` instead.
- ``PredictJob.create`` has been removed. Use :meth:`Model.request_predictions <datarobot.models.Model.request_predictions>` instead.
- ``Model.fetch_resource_data`` has been removed. Use :meth:`Model.get <datarobot.models.Model.get>` instead.
- The class ``CustomInferenceImage`` was removed. Use :class:`CustomModelVersion <datarobot.CustomModelVersion>` with ``base_environment_id`` instead.
- ``Project.set_target`` has been deprecated. Use :meth:`Project.analyze_and_model <datarobot.models.Project.analyze_and_model>` instead.


Configuration Changes
*********************
- Added a context manager :meth:`client_configuration <datarobot.client.client_configuration>` that can be used to change the connection configuration temporarily, for use in asynchronous or multithreaded code.
- Upgraded the `Pillow` library to version 9.2.0. Users installing DataRobot with the "images" extra (``pip install datarobot[images]``) should note that this is a required library.

Experimental changes
*********************

- Added experimental support for retrieving document thumbnails:

  - :class:`DocumentThumbnail <datarobot._experimental.models.documentai.document.DocumentThumbnail>`
  - :class:`DocumentPageFile <datarobot._experimental.models.documentai.document.DocumentPageFile>`

- Added experimental support to retrieve document text extraction samples using:
  - :class:`DocumentTextExtractionSample <datarobot._experimental.models.documentai.document.DocumentTextExtractionSample>`
  - :class:`DocumentTextExtractionSamplePage <datarobot._experimental.models.documentai.document.DocumentTextExtractionSamplePage>`
  - :class:`DocumentTextExtractionSampleDocument <datarobot._experimental.models.documentai.document.DocumentTextExtractionSampleDocument>`

- Added experimental deployment improvements:
  - :class:`RetrainingPolicy <datarobot._experimental.models.retraining.RetrainingPolicy>` can be used to manage retraining policies associated with a deployment.

- Added an experimental deployment improvement:
  - Use :class:`RetrainingPolicyRun <datarobot._experimental.models.retraining.RetrainingPolicyRun>` to manage retraining policies run for a retraining policy associated with a deployment.

- Added new methods to :class:`RetrainingPolicy <datarobot._experimental.models.retraining.RetrainingPolicy>`:
  - Use :meth:`RetrainingPolicy.get <datarobot._experimental.models.retraining.RetrainingPolicy.get>` to get a retraining policy associated with a deployment.
  -  Use :meth:`RetrainingPolicy.delete <datarobot._experimental.models.retraining.RetrainingPolicy.delete>` to delete a retraining policy associated with a deployment.

2.29.0b0
========

New Features
************
- Added support to pass `max_ngram_explanations` parameter in batch predictions that will trigger the
  compute of text prediction explanations.

  - :meth:`BatchPredictionJob.score <datarobot.models.BatchPredictionJob.score>`

- Added support to pass calculation mode to prediction explanations
  (`mode` parameter in :meth:`PredictionExplanations.create <datarobot.PredictionExplanations.create>`)
  as well as batch scoring
  (`explanations_mode` in :meth:`BatchPredictionJob.score <datarobot.models.BatchPredictionJob.score>`)
  for multiclass models. Supported modes:

  - :class:`TopPredictionsMode <datarobot.models.TopPredictionsMode>`
  - :class:`ClassListMode <datarobot.models.ClassListMode>`

- Added method :meth:`datarobot.CalendarFile.create_calendar_from_dataset` to the calendar file that allows us
  to create a calendar from a dataset.

- Added experimental support for `n_clusters` parameter in
  :meth:`Model.train_datetime <datarobot.models.Model.train_datetime>` and
  :meth:`DatetimeModel.retrain <datarobot.models.DatetimeModel.retrain>`
  that allows to specify number of clusters when creating models in Time Series Clustering project.

- Added new parameter `clone` to :meth:`datarobot.CombinedModel.set_segment_champion` that allows to
  set a new champion model in a cloned model instead of the original one, leaving latter unmodified.

- Added new property `is_active_combined_model` to :class:`datarobot.CombinedModel` that indicates
  if the selected combined model is currently the active one in the segmented project.

- Added new :meth:`datarobot.models.Project.get_active_combined_model` that allows users to get
  the currently active combined model in the segmented project.

- Added new parameters `read_timeout` to method `ShapMatrix.get_as_dataframe`.
  Values larger than the default can be specified to avoid timeouts when requesting large files.
  :meth:`ShapMatrix.get_as_dataframe <datarobot.models.ShapMatrix.get_as_dataframe>`

- Added support for bias mitigation with the following methods
  - :meth:`Project.get_bias_mitigated_models <datarobot.models.Project.get_bias_mitigated_models>`
  - :meth:`Project.apply_bias_mitigation <datarobot.models.Project.apply_bias_mitigation>`
  - :meth:`Project.request_bias_mitigation_feature_info <datarobot.models.Project.request_bias_mitigation_feature_info>`
  - :meth:`Project.get_bias_mitigation_feature_info <datarobot.models.Project.get_bias_mitigation_feature_info>`
  and by adding new bias mitigation params
  - bias_mitigation_feature_name
  - bias_mitigation_technique
  - include_bias_mitigation_feature_as_predictor_variable
  to the existing method
  - :meth:`Project.start <datarobot.models.Project.start>`
  and by adding this enum to supply params to some of the above functionality ``datarobot.enums.BiasMitigationTechnique``

- Added new property `status` to :class:`datarobot.models.Deployment` that represents model deployment status.

- Added new :meth:`Deployment.activate <datarobot.models.Deployment.activate>`
  and :meth:`Deployment.deactivate <datarobot.models.Deployment.deactivate>`
  that allows deployment activation and deactivation

- Added new :meth:`Deployment.delete_monitoring_data <datarobot.models.Deployment.delete_monitoring_data>` to delete deployment monitoring data.

Enhancements
************
- Added support for specifying custom endpoint URLs for S3 access in batch predictions:

  - :meth:`BatchPredictionJob.score <datarobot.models.BatchPredictionJob.score>`
  - :meth:`BatchPredictionJob.score <datarobot.models.BatchPredictionJob.score_s3>`

  See: `endpoint_url` parameter.

- Added guide on :ref:`working with binary data <binary_data>`
- Added multithreading support to binary data helper functions.
- Binary data helpers image defaults aligned with application's image preprocessing.
- Added the following accuracy metrics to be retrieved for a deployment - TPR, PPV, F1 and MCC :ref:`Deployment monitoring <deployment_monitoring>`

Bugfixes
********
- Don't include holdout start date, end date, or duration in datetime partitioning payload when
  holdout is disabled.
- Moved ICE Plot capabilities of Feature Effects into experimental support. Removed ICE Plot capabilities from Feature Fit.
- Handle undefined calendar_name in CalendarFile.create_calendar_from_dataset
- Raise ValueError for submitted calendar names that are not strings

API Changes
***********
- `version` field is removed from `ImportedModel` object

Deprecation Summary
*******************
- Reason Codes objects deprecated in 2.13 version were removed.
  Please use Prediction Explanations instead.

Configuration Changes
*********************
- The upper version constraint on pandas has been removed.

Documentation Changes
*********************
- Fixed a minor typo in the example for Dataset.create_from_data_source.

- Update the documentation to suggest that `feature_derivation_window_end` of :py:class:`datarobot.DatetimePartitioningSpecification` class should be a negative or zero.


2.28.0
======

New Features
************
- Added new parameter `upload_read_timeout` to :meth:`BatchPredictionJob.score <datarobot.models.BatchPredictionJob.score>`
  and :meth:`BatchPredictionJob.score_to_file <datarobot.models.BatchPredictionJob.score_to_file>` to indicate how many seconds to wait
  until intake dataset uploads to server. Default value 600s.

- Added the ability to turn off supervised feature reduction for Time Series projects. Option
  `use_supervised_feature_reduction` can be set in :py:class:`AdvancedOptions <datarobot.helpers.AdvancedOptions>`.

- Allow `maximum_memory` to be input for custom tasks versions. This will be used for setting the limit
  to which a custom task prediction container memory can grow.

- Added method :meth:`datarobot.models.Project.get_multiseries_names` to the project service which will
  return all the distinct entries in the multiseries column

- Added new `segmentation_task_id` attribute to :meth:`datarobot.models.Project.set_target` that allows to
  start project as Segmented Modeling project.

- Added new property `is_segmented` to :class:`datarobot.models.Project` that indicates if project is a
  regular one or Segmented Modeling project.

- Added method :meth:`datarobot.models.Project.restart_segment` to the project service that allows to
  restart single segment that hasn't reached modeling phase.

- Added the ability to interact with Combined Models in Segmented Modeling projects.
  Available with new class: :class:`datarobot.CombinedModel`.

  Functionality:
    - :meth:`datarobot.CombinedModel.get`
    - :meth:`datarobot.CombinedModel.get_segments_info`
    - :meth:`datarobot.CombinedModel.get_segments_as_dataframe`
    - :meth:`datarobot.CombinedModel.get_segments_as_csv`
    - :meth:`datarobot.CombinedModel.set_segment_champion`

- Added the ability to create and retrieve segmentation tasks used in Segmented Modeling projects.
  Available with new class: :class:`datarobot.SegmentationTask`.

  Functionality:
    - :meth:`datarobot.SegmentationTask.create`
    - :meth:`datarobot.SegmentationTask.list`
    - :meth:`datarobot.SegmentationTask.get`

- Added new class: :class:`datarobot.SegmentInfo` that allows to get information on all segments of
  Segmented modeling projects, i.e. segment project ID, model counts, autopilot status.

  Functionality:
    - :meth:`datarobot.SegmentInfo.list`

- Added new methods to base `APIObject` to assist with dictionary and json serialization of child objects.

  Functionality:
    - `APIObject.to_dict`
    - `APIObject.to_json`

- Added new methods to `ImageAugmentationList` for interacting with image augmentation samples.

  Functionality:
    - `ImageAugmentationList.compute_samples`
    - `ImageAugmentationList.retrieve_samples`

- Added the ability to set a prediction threshold when creating a deployment from a learning model.

- Added support for governance, owners, predictionEnvironment, and fairnessHealth fields when querying for a Deployment object.

- Added helper methods for working with files, images and documents. Methods support conversion of
  file contents into base64 string representations. Methods for images provide also image resize and
  transformation support.

  Functionality:
    - `datarobot.helpers.binary_data_utils.get_encoded_file_contents_from_urls.`
    - `datarobot.helpers.binary_data_utils.get_encoded_file_contents_from_paths`
    - `datarobot.helpers.binary_data_utils.get_encoded_image_contents_from_paths`
    - `datarobot.helpers.binary_data_utils.get_encoded_image_contents_from_urls`

Enhancements
************
- Requesting metadata instead of actual data of :class:`datarobot.PredictionExplanations` to reduce the amount of data transfer

Bugfixes
********
- Fix a bug in :meth:`Job.get_result_when_complete <datarobot.models.Job.get_result_when_complete>` for Prediction Explanations job type to
  populate all attribute of of :class:`datarobot.PredictionExplanations` instead of just one
- Fix a bug in :class:`datarobot.models.ShapImpact` where `row_count` was not optional
- Allow blank value for schema and catalog in `RelationshipsConfiguration` response data
- Fix a bug where credentials were incorrectly formatted in
  :meth:`Project.upload_dataset_from_catalog <datarobot.models.Project.upload_dataset_from_catalog>`
  and
  :meth:`Project.upload_dataset_from_data_source <datarobot.models.Project.upload_dataset_from_data_source>`
- Rejecting downloads of Batch Prediction data that was not written to the localfile output adapter
- Fix a bug in :meth:`datarobot.models.BatchPredictionJobDefinition.create` where `schedule` was not optional for all cases

API Changes
***********

- User can include ICE plots data in the response when requesting Feature Effects/Feature Fit. Extended methods are
    - :meth:`Model.get_feature_effect <datarobot.models.Model.get_feature_effect>`,
    - :meth:`Model.get_feature_fit <datarobot.models.Model.get_feature_fit>`,
    - :meth:`DatetimeModel.get_feature_effect <datarobot.models.DatetimeModel.get_feature_effect>` and
    - :meth:`DatetimeModel.get_feature_fit <datarobot.models.DatetimeModel.get_feature_fit>`.

Deprecation Summary
*******************

- `attrs` library is removed from library dependencies
- ``ImageAugmentationSample.compute`` was marked as deprecated and will be removed in v2.30. You
  can get the same information with newly introduced method ``ImageAugmentationList.compute_samples``
- ``ImageAugmentationSample.list`` using ``sample_id``
- Deprecating scaleout parameters for projects / models. Includes ``scaleout_modeling_mode``,
  ``scaleout_max_train_pct``, and ``scaleout_max_train_rows``

Configuration Changes
*********************
- `pandas` upper version constraint is updated to include version 1.3.5.

Documentation Changes
*********************

- Fixed "from datarobot.enums" import in Unsupervised Clustering example provided in docs.


2.27.0
========

New Features
************
- :class:`datarobot.UserBlueprint` is now mature with full support of functionality. Users
  are encouraged to use the `Blueprint Workshop <blueprint-workshop.datarobot.com>`_ instead of
  this class directly.
- Added the arguments attribute in :class:`datarobot.CustomTaskVersion`.
- Added the ability to retrieve detected errors in the potentially multicategorical feature types that prevented the
  feature to be identified as multicategorical.
  :meth:`Project.download_multicategorical_data_format_errors<datarobot.models.Project.download_multicategorical_data_format_errors>`
- Added the support of listing/updating user roles on one custom task.
    - :meth:`datarobot.CustomTask.get_access_list`
    - :meth:`datarobot.CustomTask.share`
- Added a method :meth:`datarobot.models.Dataset.create_from_query_generator`. This creates a dataset
  in the AI catalog from a `datarobot.DataEngineQueryGenerator`.
- Added the new functionality of creating a user blueprint with a custom task version id.
  :meth:`datarobot.UserBlueprint.create_from_custom_task_version_id`.
- The DataRobot Python Client is no longer published under the Apache-2.0 software license, but rather under the terms
  of the DataRobot Tool and Utility Agreement.
- Added a new class: :class:`datarobot.DataEngineQueryGenerator`. This class generates a Spark
  SQL query to apply time series data prep to a dataset in the AI catalog.

  Functionality:
    - :meth:`datarobot.DataEngineQueryGenerator.create`
    - :meth:`datarobot.DataEngineQueryGenerator.get`
    - :meth:`datarobot.DataEngineQueryGenerator.create_dataset`

  See the :ref:`time series data prep documentation <time_series_data_prep>` for more information.

- Added the ability to upload a prediction dataset into a project from the AI catalog
  :meth:`Project.upload_dataset_from_catalog<datarobot.models.Project.upload_dataset_from_catalog>`.
- Added the ability to specify the number of training rows to use in SHAP based Feature Impact computation. Extended
  method:

    - :meth:`ShapImpact.create <datarobot.models.ShapImpact.create>`
- Added the ability to retrieve and restore features that have been reduced using the time series feature generation and
  reduction functionality. The functionality comes with a new
  class: :class:`datarobot.models.restore_discarded_features.DiscardedFeaturesInfo`.

  Functionality:
    - :meth:`datarobot.models.restore_discarded_features.DiscardedFeaturesInfo.retrieve`
    - :meth:`datarobot.models.restore_discarded_features.DiscardedFeaturesInfo.restore`
- Added the ability to control class mapping aggregation in multiclass projects via
  :class:`ClassMappingAggregationSettings <datarobot.helpers.ClassMappingAggregationSettings>` passed as a parameter to
  :meth:`Project.set_target <datarobot.models.Project.set_target>`

- Added support for :ref:`unsupervised clustering projects<unsupervised_clustering>`

- Added the ability to compute and retrieve Feature Effects for a Multiclass model using
  :meth:`datarobot.models.Model.request_feature_effects_multiclass`,
  :meth:`datarobot.models.Model.get_feature_effects_multiclass` or
  :meth:`datarobot.models.Model.get_or_request_feature_effects_multiclass` methods. For datetime models use following
  methods :meth:`datarobot.models.DatetimeModel.request_feature_effects_multiclass`,
  :meth:`datarobot.models.DatetimeModel.get_feature_effects_multiclass` or
  :meth:`datarobot.models.DatetimeModel.get_or_request_feature_effects_multiclass` with `backtest_index` specified

- Added the ability to get and update challenger model settings for deployment
  class: :class:`datarobot.models.Deployment`

  Functionality:
    - :meth:`datarobot.models.Deployment.get_challenger_models_settings`
    - :meth:`datarobot.models.Deployment.update_challenger_models_settings`

- Added the ability to get and update segment analysis settings for deployment
  class: :class:`datarobot.models.Deployment`

  Functionality:
    - :meth:`datarobot.models.Deployment.get_segment_analysis_settings`
    - :meth:`datarobot.models.Deployment.update_segment_analysis_settings`

- Added the ability to get and update predictions by forecast date settings for deployment
  class: :class:`datarobot.models.Deployment`

  Functionality:
    - :meth:`datarobot.models.Deployment.get_predictions_by_forecast_date_settings`
    - :meth:`datarobot.models.Deployment.update_predictions_by_forecast_date_settings`

- Added the ability to specify multiple feature derivation windows when creating a Relationships Configuration using
  :meth:`RelationshipsConfiguration.create <datarobot.models.RelationshipsConfiguration.create>`

- Added the ability to manipulate a legacy conversion for a custom inference model, using the
  class: :class:`CustomModelVersionConversion <datarobot.models.CustomModelVersionConversion>`

  Functionality:
	- :meth:`CustomModelVersionConversion.run_conversion <datarobot.models.CustomModelVersionConversion.run_conversion>`
	- :meth:`CustomModelVersionConversion.stop_conversion <datarobot.models.CustomModelVersionConversion.stop_conversion>`
	- :meth:`CustomModelVersionConversion.get <datarobot.models.CustomModelVersionConversion.get>`
	- :meth:`CustomModelVersionConversion.get_latest <datarobot.models.CustomModelVersionConversion.get_latest>`
	- :meth:`CustomModelVersionConversion.list <datarobot.models.CustomModelVersionConversion.list>`

Enhancements
************
- :meth:`Project.get <datarobot.models.Project.get>` returns the query_generator_id used for time series data prep when applicable.
- Feature Fit & Feature Effects can return `datetime` instead of `numeric` for `feature_type` field for
  numeric features that are derived from dates.
- These methods now provide additional field ``rowCount`` in SHAP based Feature Impact results.

    - :meth:`ShapImpact.create <datarobot.models.ShapImpact.create>`
    - :meth:`ShapImpact.get <datarobot.models.ShapImpact.get>`
- Improved performance when downloading prediction dataframes for Multilabel projects using:
    - :meth:`Predictions.get_all_as_dataframe <datarobot.models.Predictions.get_all_as_dataframe>`
    - :meth:`PredictJob.get_predictions <datarobot.models.PredictJob.get_predictions>`
    - :meth:`Job.get_result <datarobot.models.Job.get_result>`

Bugfixes
********
- fix :class:`datarobot.CustomTaskVersion` and :class:`datarobot.CustomModelVersion` to correctly format ``required_metadata_values``
  before sending them via API
- Fixed response validation that could cause `DataError` when using :class:`datarobot.models.Dataset` for a dataset with a description that is an empty string.

API Changes
***********
- :meth:`RelationshipsConfiguration.create <datarobot.models.RelationshipsConfiguration.create>` will include a
  new key ``data_source_id`` in `data_source` field when applicable

Deprecation Summary
*******************
- ``Model.get_all_labelwise_roc_curves`` has been removed.
  You can get the same information with multiple calls of
  :meth:`Model.get_labelwise_roc_curves <datarobot.models.Model.get_labelwise_roc_curves>`, one per data source.
- ``Model.get_all_multilabel_lift_charts`` has been removed.
  You can get the same information with multiple calls of
  :meth:`Model.get_multilabel_lift_charts <datarobot.models.Model.get_multilabel_lift_charts>`, one per data source.

Configuration Changes
*********************

Documentation Changes
*********************
- This release introduces a new documentation organization. The organization has been modified to better reflect the end-to-end modeling workflow. The new "Tutorials" section has 5 major topics that outline the major components of modeling: Data, Modeling, Predictions, MLOps, and Administration.
- The Getting Started workflow is now hosted at `DataRobot's API Documentation Home <https://docs.datarobot.com/en/docs/api/index.html>`_.
- Added an example of how to set up optimized datetime partitioning for time series projects.

2.26.0
========

New Features
************
- Added the ability to use external baseline predictions for time series project. External
  dataset can be validated using :meth:`datarobot.models.Project.validate_external_time_series_baseline`.
  Option can be set in :py:class:`AdvancedOptions <datarobot.helpers.AdvancedOptions>` to scale
  datarobot models' accuracy performance using external dataset's accuracy performance.
  See the :ref:`external baseline predictions documentation <external_baseline_predictions>`
  for more information.
- Added the ability to generate exponentially weighted moving average features for time series
  project. Option can be set in :py:class:`AdvancedOptions <datarobot.helpers.AdvancedOptions>`
  and controls the alpha parameter used in exponentially weighted moving average operation.
- Added the ability to request a specific model be prepared for deployment using
  :meth:`Project.start_prepare_model_for_deployment<datarobot.models.Project.start_prepare_model_for_deployment>`.
- Added a new class: :class:`datarobot.CustomTask`. This class is a custom task that you can use
  as part (or all) of your blue print for training models. It needs
  :class:`datarobot.CustomTaskVersion` before it can properly be used.

  Functionality:
    - Create, copy, update or delete:
        - :meth:`datarobot.CustomTask.create`
        - :meth:`datarobot.CustomTask.copy`
        - :meth:`datarobot.CustomTask.update`
        - :meth:`datarobot.CustomTask.delete`
    - list, get and refresh current tasks:
        - :meth:`datarobot.CustomTask.get`
        - :meth:`datarobot.CustomTask.list`
        - :meth:`datarobot.CustomTask.refresh`
    - Download the latest :class:`datarobot.CustomTaskVersion` of the :class:`datarobot.CustomTask`
        - :meth:`datarobot.CustomTask.download_latest_version`
- Added a new class: :class:`datarobot.CustomTaskVersion`. This class
  is for management of specific versions of a custom task.

  Functionality:
        - Create new custom task versions:
            - :meth:`datarobot.CustomTaskVersion.create_clean`
            - :meth:`datarobot.CustomTaskVersion.create_from_previous`

        - list, get and refresh current available versions:
            - :meth:`datarobot.CustomTaskVersion.list`
            - :meth:`datarobot.CustomTaskVersion.get`
            - :meth:`datarobot.CustomTaskVersion.refresh`


        - :meth:`datarobot.CustomTaskVersion.download`
          will download a tarball of the files used to create the custom task


        - :meth:`datarobot.CustomTaskVersion.update`
          updates the metadata for a custom task.
- Added the ability compute batch predictions for an in-memory DataFrame using
  :meth:`BatchPredictionJob.score <datarobot.models.BatchPredictionJob.score_pandas>`
- Added the ability to specify feature discovery settings when creating a Relationships Configuration using
  :meth:`RelationshipsConfiguration.create <datarobot.models.RelationshipsConfiguration.create>`

Enhancements
************

- Improved performance when downloading prediction dataframes using:
    - :meth:`Predictions.get_all_as_dataframe <datarobot.models.Predictions.get_all_as_dataframe>`
    - :meth:`PredictJob.get_predictions <datarobot.models.PredictJob.get_predictions>`
    - :meth:`Job.get_result <datarobot.models.Job.get_result>`

- Added new `max_wait` parameter to methods:
    - :meth:`Dataset.create_from_url<datarobot.models.Dataset.create_from_url>`
    - :meth:`Dataset.create_from_in_memory_data<datarobot.models.Dataset.create_from_in_memory_data>`
    - :meth:`Dataset.create_from_data_source<datarobot.models.Dataset.create_from_data_source>`
    - :meth:`Dataset.create_version_from_in_memory_data<datarobot.models.Dataset.create_version_from_in_memory_data>`
    - :meth:`Dataset.create_version_from_url<datarobot.models.Dataset.create_version_from_url>`
    - :meth:`Dataset.create_version_from_data_source<datarobot.models.Dataset.create_version_from_data_source>`

Bugfixes
********

- :meth:`Model.get<datarobot.models.Model.get>` will return a ``DatetimeModel`` instead of ``Model``
  whenever the project is datetime partitioned. This enables the
  :meth:`ModelRecommendation.get_model<datarobot.models.ModelRecommendation.get_model>` to return
  a ``DatetimeModel`` instead of ``Model`` whenever the project is datetime partitioned.
- Try to read Feature Impact result if existing jobId is None in
  :meth:`Model.get_or_request_feature_impact <datarobot.models.Model.get_or_request_feature_impact>`.
- Set upper version constraints for pandas.
- :meth:`RelationshipsConfiguration.create <datarobot.models.RelationshipsConfiguration.create>` will return a ``catalog``
  in `data_source` field
- Argument ``required_metadata_keys`` was not properly being sent in the update and create requests for
  :class:`datarobot.ExecutionEnvironment`.
- Fix issue with :class:`datarobot.ExecutionEnvironment` create method failing when used against older versions of the application
- :class:`datarobot.CustomTaskVersion` was not properly handling ``required_metadata_values`` from the API response

API Changes
***********

- Updated :meth:`Project.start <datarobot.models.Project.start>` to use ``AUTOPILOT_MODE.QUICK`` when the
  ``autopilot_on`` param is set to True. This brings it in line with :meth:`Project.set_target
  <datarobot.models.Project.set_target>`.
- Updated :meth:`project.start_autopilot <datarobot.models.Project.start_autopilot>` to accept
  the following new GA parameters that are already in the public API: ``consider_blenders_in_recommendation``,
  ``run_leakage_removed_feature_list``

Deprecation Summary
*******************

- The ``required_metadata`` property of :class:`datarobot.CustomModelVersion` has been deprecated.
  ``required_metadata_values`` should be used instead.

- The ``required_metadata`` property of :class:`datarobot.CustomTaskVersion` has been deprecated.
  ``required_metadata_values`` should be used instead.

Configuration Changes
*********************
- Now requires dependency on package `scikit-learn <https://pypi.org/project/scikit-learn/>`_  rather than
  `sklearn <https://pypi.org/project/scikit-learn/>`_. Note: This dependency is only used in example code. See
  `this scikit-learn issue <https://github.com/scikit-learn/scikit-learn/issues/8215>`_ for more information.
- Now permits dependency on package `attrs <https://pypi.org/project/attrs/>`_  to be less than version 21. This
  fixes compatibility with apache-airflow.

- Allow to setup ``Authorization: <type> <token>`` type header for OAuth2 Bearer tokens.

Documentation Changes
*********************

- Update the documentation with respect to the permission that controls AI Catalog dataset snapshot behavior.

2.25.0
======

New Features
************
- There is a new :class:`AnomalyAssessmentRecord<datarobot.models.anomaly_assessment.AnomalyAssessmentRecord>` object that
  implements public API routes to work with anomaly assessment insight. This also adds explanations
  and predictions preview classes. The insight is available for anomaly detection models in time
  series unsupervised projects which also support calculation of Shapley values.

    - :class:`AnomalyAssessmentPredictionsPreview<datarobot.models.anomaly_assessment.AnomalyAssessmentPredictionsPreview>`
    - :class:`AnomalyAssessmentExplanations<datarobot.models.anomaly_assessment.AnomalyAssessmentExplanations>`

  Functionality:

        - Initialize an anomaly assessment insight for the specified subset.

            - :meth:`DatetimeModel.initialize_anomaly_assessment<datarobot.models.DatetimeModel.initialize_anomaly_assessment>`

        - Get anomaly assessment records, shap explanations, predictions preview:

            - :meth:`DatetimeModel.get_anomaly_assessment_records<datarobot.models.DatetimeModel.get_anomaly_assessment_records>` list available records
            - :meth:`AnomalyAssessmentRecord.get_predictions_preview<datarobot.models.anomaly_assessment.AnomalyAssessmentRecord.get_predictions_preview>` get predictions preview for the record
            - :meth:`AnomalyAssessmentRecord.get_latest_explanations<datarobot.models.anomaly_assessment.AnomalyAssessmentRecord.get_latest_explanations>` get latest predictions along with shap explanations for the most anomalous records.
            - :meth:`AnomalyAssessmentRecord.get_explanations<datarobot.models.anomaly_assessment.AnomalyAssessmentRecord.get_explanations>` get predictions along with shap explanations for the most anomalous records for the specified range.

        -  Delete anomaly assessment record:

            - :meth:`AnomalyAssessmentRecord.delete<datarobot.models.anomaly_assessment.AnomalyAssessmentRecord.delete>` delete record

- Added an ability to calculate and retrieve Datetime trend plots for :meth:`DatetimeModel<datarobot.models.DatetimeModel>`.
  This includes Accuracy over Time, Forecast vs Actual, and Anomaly over Time.

  Plots can be calculated using a common method:

    - :meth:`DatetimeModel.compute_datetime_trend_plots<datarobot.models.DatetimeModel.compute_datetime_trend_plots>`

  Metadata for plots can be retrieved using the following methods:

    - :meth:`DatetimeModel.get_accuracy_over_time_plots_metadata<datarobot.models.DatetimeModel.get_accuracy_over_time_plots_metadata>`
    - :meth:`DatetimeModel.get_forecast_vs_actual_plots_metadata<datarobot.models.DatetimeModel.get_forecast_vs_actual_plots_metadata>`
    - :meth:`DatetimeModel.get_anomaly_over_time_plots_metadata<datarobot.models.DatetimeModel.get_anomaly_over_time_plots_metadata>`

  Plots can be retrieved using the following methods:

    - :meth:`DatetimeModel.get_accuracy_over_time_plot<datarobot.models.DatetimeModel.get_accuracy_over_time_plot>`
    - :meth:`DatetimeModel.get_forecast_vs_actual_plot<datarobot.models.DatetimeModel.get_forecast_vs_actual_plot>`
    - :meth:`DatetimeModel.get_anomaly_over_time_plot<datarobot.models.DatetimeModel.get_anomaly_over_time_plot>`

  Preview plots can be retrieved using the following methods:

    - :meth:`DatetimeModel.get_accuracy_over_time_plot_preview<datarobot.models.DatetimeModel.get_accuracy_over_time_plot_preview>`
    - :meth:`DatetimeModel.get_forecast_vs_actual_plot_preview<datarobot.models.DatetimeModel.get_forecast_vs_actual_plot_preview>`
    - :meth:`DatetimeModel.get_anomaly_over_time_plot_preview<datarobot.models.DatetimeModel.get_anomaly_over_time_plot_preview>`

- Support for Batch Prediction Job Definitions has now been added through the following class:
  :class:`BatchPredictionJobDefinition<datarobot.models.BatchPredictionJobDefinition>`.
  You can create, update, list and delete definitions using the following methods:

    - :meth:`BatchPredictionJobDefinition.list <datarobot.models.BatchPredictionJobDefinition.list>`
    - :meth:`BatchPredictionJobDefinition.create <datarobot.models.BatchPredictionJobDefinition.create>`
    - :meth:`BatchPredictionJobDefinition.update <datarobot.models.BatchPredictionJobDefinition.update>`
    - :meth:`BatchPredictionJobDefinition.delete <datarobot.models.BatchPredictionJobDefinition.delete>`

Enhancements
************

- Added a new helper function to create Dataset Definition, Relationship and Secondary Dataset used by
  Feature Discovery Project. They are accessible via
  :py:class:`DatasetDefinition <datarobot.helpers.feature_discovery.DatasetDefinition>`
  :py:class:`Relationship <datarobot.helpers.feature_discovery.Relationship>`
  :py:class:`SecondaryDataset <datarobot.helpers.feature_discovery.SecondaryDataset>`

- Added new helper function to projects to retrieve the recommended model.
  :meth:`Project.recommended_model <datarobot.models.Project.recommended_model>`

- Added method to download feature discovery recipe SQLs (limited beta feature).
  :meth:`Project.download_feature_discovery_recipe_sqls<datarobot.models.Project.download_feature_discovery_recipe_sqls>`.

- Added ``docker_context_size`` and ``docker_image_size`` to :class:`datarobot.ExecutionEnvironmentVersion`

Bugfixes
********
- Remove the deprecation warnings when using with latest versions of urllib3.

- :meth:`FeatureAssociationMatrix.get <datarobot.models.FeatureAssociationMatrix.get>` is now using correct query param
  name when `featurelist_id` is specified.

- Handle scalar values in ``shapBaseValue`` while converting a predictions response to a data frame.

- Ensure that if a configured endpoint ends in a trailing slash, the resulting full URL does
  not end up with double slashes in the path.

- :meth:`Model.request_frozen_datetime_model <datarobot.models.Model.request_frozen_datetime_model>` is now implementing correct
  validation of input parameter ``training_start_date``.

API Changes
***********

- Arguments ``secondary_datasets`` now accept :py:class:`SecondaryDataset <datarobot.helpers.feature_discovery.SecondaryDataset>`
  to create secondary dataset configurations
  - :meth:`SecondaryDatasetConfigurations.create <datarobot.models.SecondaryDatasetConfigurations.create>`

- Arguments ``dataset_definitions`` and ``relationships`` now accept :py:class:`DatasetDefinition <datarobot.helpers.feature_discovery.DatasetDefinition>` :py:class:`Relationship <datarobot.helpers.feature_discovery.Relationship>`
  to create and replace relationships configuration
  - :meth:`RelationshipsConfiguration.create <datarobot.models.RelationshipsConfiguration.create>` creates a new relationships configuration between datasets
  - :meth:`RelationshipsConfiguration.retrieve <datarobot.models.RelationshipsConfiguration.get>` retrieve the requested relationships
  configuration

- Argument ``required_metadata_keys`` has been added to :class:`datarobot.ExecutionEnvironment`.  This should be used to
  define a list of :py:class:`RequiredMetadataKey <datarobot.models.execution_environment.RequiredMetadataKey>`.
  :class:`datarobot.CustomModelVersion` that use a base environment with ``required_metadata_keys`` must define
  values for these fields in their respective ``required_metadata``

- Argument ``required_metadata`` has been added to :class:`datarobot.CustomModelVersion`.  This should be set with
  relevant values defined by the base environment's ``required_metadata_keys``


2.24.0
=========

New Features
************

- Partial history predictions can be made with time series time series multiseries models using the
  ``allow_partial_history_time_series_predictions`` attribute of the
  :py:class:`datarobot.DatetimePartitioningSpecification
  <datarobot.DatetimePartitioningSpecification>`.
  See the :ref:`Time Series <time_series>` documentation for more info.
- Multicategorical Histograms are now retrievable. They are accessible via
  :class:`MulticategoricalHistogram <datarobot.models.MulticategoricalHistogram>` or
  :meth:`Feature.get_multicategorical_histogram <datarobot.models.Feature.get_multicategorical_histogram>`.
- Add methods to retrieve per-class lift chart data for multilabel models:
  :meth:`Model.get_multilabel_lift_charts <datarobot.models.Model.get_multilabel_lift_charts>` and
  ``Model.get_all_multilabel_lift_charts``.
- Add methods to retrieve labelwise ROC curves for multilabel models:
  :meth:`Model.get_labelwise_roc_curves <datarobot.models.Model.get_labelwise_roc_curves>` and
  ``Model.get_all_labelwise_roc_curves``.
- Multicategorical Pairwise Statistics are now retrievable. They are accessible via
  :class:`PairwiseCorrelations <datarobot.models.PairwiseCorrelations>`,
  :class:`PairwiseJointProbabilities <datarobot.models.PairwiseJointProbabilities>` and
  :class:`PairwiseConditionalProbabilities <datarobot.models.PairwiseConditionalProbabilities>` or
  :meth:`Feature.get_pairwise_correlations <datarobot.models.Feature.get_pairwise_correlations>`,
  :meth:`Feature.get_pairwise_joint_probabilities <datarobot.models.Feature.get_pairwise_joint_probabilities>` and
  :meth:`Feature.get_pairwise_conditional_probabilities <datarobot.models.Feature.get_pairwise_conditional_probabilities>`.
- Add methods to retrieve prediction results of a deployment:
    - :meth:`Deployment.get_prediction_results<datarobot.models.Deployment.get_prediction_results>`
    - :meth:`Deployment.download_prediction_results<datarobot.models.Deployment.download_prediction_results>`
- Add method to download scoring code of a deployment using :meth:`Deployment.download_scoring_code<datarobot.models.Deployment.download_scoring_code>`.
- Added Automated Documentation: now you can automatically generate documentation about various
  entities within the platform, such as specific models or projects. Check out the
  :ref:`Automated Documentation overview<automated_documentation_overview>` and also refer to
  the :ref:`API Reference<automated_documentation_api>` for more details.

- Create a new Dataset version for a given dataset by uploading from a file, URL or in-memory datasource.
    - :meth:`Dataset.create_version_from_file<datarobot.models.Dataset.create_version_from_file>`
    - :meth:`Dataset.create_version_from_in_memory_data<datarobot.models.Dataset.create_version_from_in_memory_data>`
    - :meth:`Dataset.create_version_from_url<datarobot.models.Dataset.create_version_from_url>`
    - :meth:`Dataset.create_version_from_data_source<datarobot.models.Dataset.create_version_from_data_source>`

Enhancements
************
- Added a new ``status`` called ``FAILED`` to from :class:`BatchPredictionJob <datarobot.models.BatchPredictionJob>` as
  this is a new status coming to Batch Predictions in an upcoming version of DataRobot.
- Added ``base_environment_version_id`` to :class:`datarobot.CustomModelVersion`.
- Support for downloading feature discovery training or prediction dataset using
  :meth:`Project.download_feature_discovery_dataset<datarobot.models.Project.download_feature_discovery_dataset>`.
- Added :class:`datarobot.models.FeatureAssociationMatrix`, :class:`datarobot.models.FeatureAssociationMatrixDetails`
  and :class:`datarobot.models.FeatureAssociationFeaturelists` that can be used to retrieve feature associations
  data as an alternative to :meth:`Project.get_associations <datarobot.models.Project.get_associations>`,
  :meth:`Project.get_association_matrix_details <datarobot.models.Project.get_association_matrix_details>` and
  :meth:`Project.get_association_featurelists <datarobot.models.Project.get_association_featurelists>` methods.


Bugfixes
********
- Fixed response validation that could cause `DataError` when using
  :meth:`TrainingPredictions.list <datarobot.models.training_predictions.TrainingPredictions.list>` and
  :meth:`TrainingPredictions.get_all_as_dataframe <datarobot.models.training_predictions.TrainingPredictions.get_all_as_dataframe>`
  methods if there are training predictions computed with `explanation_algorithm`.

API Changes
***********
- Remove `desired_memory` param from the following classes: :class:`datarobot.CustomInferenceModel`,
  :class:`datarobot.CustomModelVersion`, :class:`datarobot.CustomModelTest`
- Remove ``desired_memory`` param from the following methods:
  :meth:`CustomInferenceModel.create <datarobot.CustomInferenceModel.create>`,
  :meth:`CustomModelVersion.create_clean <datarobot.CustomModelVersion.create_clean>`,
  :meth:`CustomModelVersion.create_clean <datarobot.CustomModelVersion.create_from_previous>`,
  :meth:`CustomModelTest.create <datarobot.CustomModelTest.create>` and
  :meth:`CustomModelTest.create <datarobot.CustomModelTest.create>`


Deprecation Summary
*******************

- class ``ComplianceDocumentation``
  will be deprecated in v2.24 and will be removed entirely in v2.27. Use
  :class:`AutomatedDocument<datarobot.models.automated_documentation.AutomatedDocument>`
  instead. To start off, see the
  :ref:`Automated Documentation overview<automated_documentation_overview>` for details.

Configuration Changes
*********************

Documentation Changes
*********************

- Remove reference to S3 for :meth:`Project.upload_dataset <datarobot.models.Project.upload_dataset>` since it is not supported by the server


2.23.0
======

New Features
************
- Calendars for time series projects can now be automatically generated by providing a country code to the method
  :meth:`CalendarFile.create_calendar_from_country_code<datarobot.CalendarFile.create_calendar_from_country_code>`.
  A list of allowed country codes can be retrieved using :meth:`CalendarFile.get_allowed_country_codes<datarobot.CalendarFile.get_allowed_country_codes>`
  For more information, see the :ref:`calendar documentation <preloaded_calendar_files>`.

- Added `calculate_all_series`` param to
  :meth:`DatetimeModel.compute_series_accuracy<datarobot.models.DatetimeModel.compute_series_accuracy>`.
  This option allows users to compute series accuracy for all available series at once,
  while by default it is computed for first 1000 series only.

- Added ability to specify sampling method when setting target of OTV project. Option can be set
  in :py:class:`AdvancedOptions <datarobot.helpers.AdvancedOptions>` and changes a way training data
  is defined in autopilot steps.

- Add support for custom inference model k8s resources management. This new feature enables
  users to control k8s resources allocation for their executed model in the k8s cluster.
  It involves in adding the following new parameters: ``network_egress_policy``, ``desired_memory``,
  ``maximum_memory``, ``replicas`` to the following classes: :class:`datarobot.CustomInferenceModel`,
  :class:`datarobot.CustomModelVersion`, :class:`datarobot.CustomModelTest`

- Add support for multiclass custom inference and training models. This enables users to create
  classification custom models with more than two class labels. The :class:`datarobot.CustomInferenceModel`
  class can now use ``datarobot.TARGET_TYPE.MULTICLASS`` for their ``target_type`` parameter. Class labels for inference models
  can be set/updated using either a file or as a list of labels.

- Support for Listing all the secondary dataset configuration for a given project:
    - :meth:`SecondaryDatasetConfigurations.list<datarobot.models.SecondaryDatasetConfigurations>`

- Add support for unstructured custom inference models. The :class:`datarobot.CustomInferenceModel`
  class can now use ``datarobot.TARGET_TYPE.UNSTRUCTURED`` for its ``target_type`` parameter.
  ``target_name`` parameter is optional for ``UNSTRUCTURED`` target type.

- All per-class lift chart data is now available for multiclass models using
  :meth:`Model.get_multiclass_lift_chart <datarobot.models.Model.get_all_multiclass_lift_charts>`.

- ``AUTOPILOT_MODE.COMPREHENSIVE``, a new ``mode``, has been added to
  :meth:`Project.set_target <datarobot.models.Project.set_target>`.

- Add support for anomaly detection custom inference models. The :class:`datarobot.CustomInferenceModel`
  class can now use ``datarobot.TARGET_TYPE.ANOMALY`` for its ``target_type`` parameter.
  ``target_name`` parameter is optional for ``ANOMALY`` target type.

- Support for Updating and retrieving the secondary dataset configuration for a Feature discovery deployment:
    - :meth:`Deployment.update_secondary_dataset_config<datarobot.models.Deployment.update_secondary_dataset_config>`
    - :meth:`Deployment.get_secondary_dataset_config<datarobot.models.Deployment.get_secondary_dataset_config>`

- Add support for starting and retrieving Feature Impact information for :class:`datarobot.CustomModelVersion`

- Search for interaction features and Supervised Feature reduction for feature discovery project can now be specified
    in :py:class:`AdvancedOptions <datarobot.helpers.AdvancedOptions>`.

- Feature discovery projects can now be created using the :meth:`Project.start <datarobot.models.Project.start>`
  method by providing ``relationships_configuration_id``.

- Actions applied to input data during automated feature discovery can now be retrieved using :meth:`FeatureLineage.get <datarobot.models.FeatureLineage.get>`
  Corresponding feature lineage id is available as a new :class:`datarobot.models.Feature` field `feature_lineage_id`.


- Lift charts and ROC curves are now calculated for backtests 2+ in time series and OTV models.
  The data can be retrieved for individual backtests using :meth:`Model.get_lift_chart <datarobot.models.Model.get_lift_chart>`
  and :meth:`Model.get_roc_curve <datarobot.models.Model.get_roc_curve>`.

- The following methods now accept a new argument called credential_data, the credentials to authenticate with the database, to use instead of user/password or credential ID:
    - :meth:`Dataset.create_from_data_source<datarobot.models.Dataset.create_from_data_source>`
    - :meth:`Dataset.create_project<datarobot.models.Dataset.create_project>`
    - :meth:`Project.create_from_dataset<datarobot.models.Project.create_from_dataset>`

- Add support for DataRobot Connectors, :class:`datarobot.Connector` provides a simple implementation to interface with connectors.

Enhancements
************
- Running Autopilot on Leakage Removed feature list can now be specified in :py:class:`AdvancedOptions <datarobot.helpers.AdvancedOptions>`.
  By default, Autopilot will always run on Informative Features - Leakage Removed feature list if it exists. If the parameter
  `run_leakage_removed_feature_list` is set to False, then Autopilot will run on Informative Features or available custom feature list.
- Method :py:meth:`Project.upload_dataset <datarobot.models.Project.upload_dataset>`
  and :py:meth:`Project.upload_dataset_from_data_source <datarobot.models.Project.upload_dataset_from_data_source>`
  support new optional parameter ``secondary_datasets_config_id`` for Feature discovery project.

Bugfixes
********
- added ``disable_holdout`` param in :class:`datarobot.DatetimePartitioning`

- Using :meth:`Credential.create_gcp<datarobot.models.Credential.create_gcp>` produced an incompatible credential

- ``SampleImage.list`` now supports Regression & Multilabel projects

- Using :meth:`BatchPredictionJob.score <datarobot.models.BatchPredictionJob.download>` could in some circumstances
  result in a crash from trying to abort the job if it fails to start

- Using :meth:`BatchPredictionJob.score <datarobot.models.BatchPredictionJob.download>` or
  :meth:`BatchPredictionJob.score <datarobot.models.BatchPredictionJob.score_to_file>` would produce incomplete
  results in case a job was aborted while downloading. This will now raise an exception.

API Changes
***********
- New ``sampling_method`` param in :meth:`Model.train_datetime <datarobot.models.Model.train_datetime>`,
  :meth:`Project.train_datetime <datarobot.models.Project.train_datetime>`,
  :meth:`Model.train_datetime <datarobot.models.Model.request_frozen_datetime_model>` and
  :meth:`Model.train_datetime <datarobot.models.Model.retrain>`.
- New ``target_type`` param in :class:`datarobot.CustomInferenceModel`
- New arguments ``secondary_datasets``, ``name``, ``creator_full_name``, ``creator_user_id``, ``created``,
    ``featurelist_id``, ``credentials_ids``, ``project_version`` and ``is_default`` in :class:`datarobot.models.SecondaryDatasetConfigurations`
- New arguments ``secondary_datasets``, ``name``, ``featurelist_id`` to
    :meth:`SecondaryDatasetConfigurations.create <datarobot.models.SecondaryDatasetConfigurations.create>`
- Class ``FeatureEngineeringGraph`` has been removed. Use :class:`datarobot.models.RelationshipsConfiguration` instead.
- Param ``feature_engineering_graphs`` removed from :meth:`Project.set_target<datarobot.models.Project.set_target>`.
- Param ``config`` removed from :meth:`SecondaryDatasetConfigurations.create<datarobot.models.SecondaryDatasetConfigurations.create>`.

Deprecation Summary
*******************
- ``supports_binary_classification`` and  ``supports_regression`` are deprecated
    for :class:`datarobot.CustomInferenceModel` and will be removed in v2.24
- Argument ``config`` and  ``supports_regression`` are deprecated
    for :class:`datarobot.models.SecondaryDatasetConfigurations` and will be removed in v2.24
- ``CustomInferenceImage`` has been deprecated and will be removed in v2.24.
    :class:`datarobot.CustomModelVersion` with base_environment_id should be used in their place.
- ``environment_id`` and ``environment_version_id`` are deprecated for :meth:`CustomModelTest.create<datarobot.CustomModelTest.create>`

Documentation Changes
*********************

- `feature_lineage_id` is added as a new parameter in the response for retrieval of a :class:`datarobot.models.Feature` created by automated feature discovery or time series feature derivation.
  This id is required to retrieve a :class:`datarobot.models.FeatureLineage` instance.

2.22.1
======

New Features
************

- Batch Prediction jobs now support :ref:`dataset <batch_predictions-intake-types-dataset>` as intake settings for
  :meth:`BatchPredictionJob.score <datarobot.models.BatchPredictionJob.score>`.

- Create a Dataset from DataSource:

    - :meth:`Dataset.create_from_data_source<datarobot.models.Dataset.create_from_data_source>`
    - :meth:`DataSource.create_dataset<datarobot.DataSource.create_dataset>`

- Added support for Custom Model Dependency Management.  Please see :ref:`custom model documentation<custom_models>`.
  New features added:

    - Added new argument ``base_environment_id`` to methods
      :meth:`CustomModelVersion.create_clean<datarobot.CustomModelVersion.create_clean>`
      and :meth:`CustomModelVersion.create_from_previous<datarobot.CustomModelVersion.create_from_previous>`
    - New fields ``base_environment_id`` and ``dependencies`` to class
      :class:`datarobot.CustomModelVersion`
    - New class :class:`datarobot.CustomModelVersionDependencyBuild`
      to prepare custom model versions with dependencies.
    - Made argument ``environment_id`` of
      :meth:`CustomModelTest.create<datarobot.CustomModelTest.create>` optional to enable using
      custom model versions with dependencies
    - New field ``image_type`` added to class
      :class:`datarobot.CustomModelTest`
    - :meth:`Deployment.create_from_custom_model_version<datarobot.models.Deployment.create_from_custom_model_version>` can be used to create a deployment from a custom model version.


- Added new parameters for starting and re-running Autopilot with customizable settings within
  :meth:`Project.start_autopilot<datarobot.models.Project.start_autopilot>`.

- Added a new method to trigger Feature Impact calculation for a Custom Inference Image:
  ``CustomInferenceImage.calculate_feature_impact``

- Added new method to retrieve number of iterations trained for early stopping models. Currently supports only tree-based models.
  :meth:`Model.get_num_iterations_trained <datarobot.models.Model.get_num_iterations_trained>`.

Enhancements
************

- A description can now be added or updated for a project.
  :meth:`Project.set_project_description <datarobot.models.Project.set_project_description>`.

- Added new parameters `read_timeout` and `max_wait` to method :meth:`Dataset.create_from_file<datarobot.models.Dataset.create_from_file>`.
  Values larger than the default can be specified for both to avoid timeouts when uploading large files.


- Added new parameter `metric` to :class:`datarobot.models.TargetDrift`, :class:`datarobot.models.FeatureDrift`,
  :meth:`Deployment.get_target_drift<datarobot.models.Deployment.get_target_drift>`
  and :meth:`Deployment.get_feature_drift<datarobot.models.Deployment.get_feature_drift>`.

- Added new parameter `timeout` to :meth:`BatchPredictionJob.download <datarobot.models.BatchPredictionJob.download>` to indicate
  how many seconds to wait for the download to start (in case the job doesn't start processing immediately).
  Set to ``-1`` to disable.
  This parameter can also be sent as `download_timeout` to :meth:`BatchPredictionJob.score <datarobot.models.BatchPredictionJob.score>`
  and :meth:`BatchPredictionJob.score <datarobot.models.BatchPredictionJob.score_to_file>`.
  If the timeout occurs, the pending job will be aborted.

- Added new parameter `read_timeout` to :meth:`BatchPredictionJob.download <datarobot.models.BatchPredictionJob.download>` to indicate
  how many seconds to wait between each downloaded chunk.
  This parameter can also be sent as `download_read_timeout` to :meth:`BatchPredictionJob.score <datarobot.models.BatchPredictionJob.score>`
  and :meth:`BatchPredictionJob.score <datarobot.models.BatchPredictionJob.score_to_file>`.

- Added parameter ``catalog`` to :meth:`BatchPredictionJob <datarobot.models.BatchPredictionJob.score>` to both intake
  and output adapters for type `jdbc`.

- Consider blenders in recommendation can now be specified in :py:class:`AdvancedOptions <datarobot.helpers.AdvancedOptions>`.
  Blenders will be included when autopilot chooses a model to prepare and recommend for deployment.

- Added optional parameter ``max_wait`` to :meth:`Deployment.replace_model <datarobot.models.Deployment.replace_model>` to indicate
  the maximum time to wait for model replacement job to complete before erroring.

Bugfixes
********

- Handle ``null`` values in ``predictionExplanationMetadata["shapRemainingTotal"]`` while converting a predictions
  response to a data frame.

- Handle ``null`` values in ``customModel["latestVersion"]``

- Removed an extra column ``status`` from :class:`BatchPredictionJob <datarobot.models.BatchPredictionJob>` as
  it caused issues with never version of Trafaret validation.

- Make ``predicted_vs_actual`` optional in Feature Effects data because a feature may have insufficient qualified samples.

- Make ``jdbc_url`` optional in Data Store data because some data stores will not have it.

- The method :meth:`Project.get_datetime_models<datarobot.models.Project.get_datetime_models>` now correctly returns all
  ``DatetimeModel`` objects for the project, instead of just the first 100.

- Fixed a documentation error related to snake_case vs camelCase in the JDBC settings payload.

- Make trafaret validator for datasets use a syntax that works properly with a wider range of trafaret versions.

- Handle extra keys in CustomModelTests and CustomModelVersions

- ``ImageEmbedding`` and ``ImageActivationMap`` now supports regression projects.

API Changes
***********

- The default value for the ``mode`` param in :meth:`Project.set_target
  <datarobot.models.Project.set_target>` has been changed from ``AUTOPILOT_MODE.FULL_AUTO``
  to ``AUTOPILOT_MODE.QUICK``

Deprecation Summary
*******************

Configuration Changes
*********************

Documentation Changes
*********************

- Added links to classes with duration parameters such as `validation_duration` and `holdout_duration` to
  provide duration string examples to users.

- The :ref:`models documentation <models>` has been revised to include section on how to train a new model and how to run cross-validation
  or backtesting for a model.

2.21.0
======

New Features
************

- Added new arguments ``explanation_algorithm`` and ``max_explanations`` to method
  :meth:`Model.request_training_predictions <datarobot.models.Model.request_training_predictions>`.
  New fields ``explanation_algorithm``, ``max_explanations`` and ``shap_warnings`` have been added to class
  :class:`TrainingPredictions <datarobot.models.training_predictions.TrainingPredictions>`.
  New fields ``prediction_explanations`` and ``shap_metadata`` have been added to class
  :class:`TrainingPredictionsIterator <datarobot.models.training_predictions.TrainingPredictionsIterator>` that is
  returned by method
  :meth:`TrainingPredictions.iterate_rows <datarobot.models.training_predictions.TrainingPredictions.iterate_rows>`.
- Added new arguments ``explanation_algorithm`` and ``max_explanations`` to method
  :meth:`Model.request_predictions <datarobot.models.Model.request_predictions>`. New fields ``explanation_algorithm``,
  ``max_explanations`` and ``shap_warnings`` have been added to class
  :class:`Predictions <datarobot.models.Predictions>`. Method
  :meth:`Predictions.get_all_as_dataframe <datarobot.models.Predictions.get_all_as_dataframe>` has new argument
  ``serializer`` that specifies the retrieval and results validation method (``json`` or ``csv``) for the predictions.
- Added possibility to compute :meth:`ShapImpact.create <datarobot.models.ShapImpact.create>` and request
  :meth:`ShapImpact.get <datarobot.models.ShapImpact.get>` SHAP impact scores for features in a model.

- Added support for accessing Visual AI images and insights. See the DataRobot
  Python Package documentation, Visual AI Projects, section for details.

- User can specify custom row count when requesting Feature Effects. Extended methods are
  :meth:`Model.request_feature_effect <datarobot.models.Model.request_feature_effect>` and
  :meth:`Model.get_or_request_feature_effect <datarobot.models.Model.get_or_request_feature_effect>`.
- Users can request SHAP based predictions explanations for a models that support SHAP scores using
  :meth:`ShapMatrix.create <datarobot.models.ShapMatrix.create>`.
- Added two new methods to :class:`Dataset<datarobot.models.Dataset>` to lazily retrieve paginated
  responses.

    - :meth:`Dataset.iterate<datarobot.models.Dataset.iterate>` returns an iterator of the datasets
      that a user can view.
    - :meth:`Dataset.iterate_all_features<datarobot.models.Dataset.iterate_all_features>` returns an
      iterator of the features of a dataset.

- It's possible to create an Interaction feature by combining two categorical features together using
  :meth:`Project.create_interaction_feature<datarobot.models.Project.create_interaction_feature>`.
  Operation result represented by :class:`models.InteractionFeature.<datarobot.models.InteractionFeature>`.
  Specific information about an interaction feature may be retrieved by its name using
  :meth:`models.InteractionFeature.get<datarobot.models.InteractionFeature.get>`
- Added the :class:`DatasetFeaturelist<datarobot.DatasetFeaturelist>` class to support featurelists
  on datasets in the AI Catalog. DatasetFeaturelists can be updated or deleted. Two new methods were
  also added to :class:`Dataset<datarobot.models.Dataset>` to interact with DatasetFeaturelists. These are
  :meth:`Dataset.get_featurelists<datarobot.models.Dataset.get_featurelists>` and
  :meth:`Dataset.create_featurelist<datarobot.models.Dataset.create_featurelist>` which list existing
  featurelists and create new featurelists on a dataset, respectively.
- Added ``model_splits`` to :class:`DatetimePartitioningSpecification<datarobot.DatetimePartitioningSpecification>` and
  to :class:`DatetimePartitioning<datarobot.DatetimePartitioning>`. This will allow users to control the
  jobs per model used when building models. A higher number of ``model_splits``  will result in less downsampling,
  allowing the use of more post-processed data.
- Added support for :ref:`unsupervised projects<unsupervised_anomaly>`.
- Added support for external test set. Please see :ref:`testset documentation<external_testset>`
- A new workflow is available for assessing models on external test sets in time series unsupervised projects.
  More information can be found in the :ref:`documentation<unsupervised_external_dataset>`.

  - :meth:`Project.upload_dataset<datarobot.models.Project.upload_dataset>` and
    :meth:`Model.request_predictions<datarobot.models.Model.request_predictions>` now accept
    ``actual_value_column`` - name of the actual value column, can be passed only with date range.
  - :class:`PredictionDataset<datarobot.models.PredictionDataset>` objects now contain the following
    new fields:

    - ``actual_value_column``: Actual value column which was selected for this dataset.
    - ``detected_actual_value_column``: A list of detected actual value column info.

  - New warning is added to ``data_quality_warnings`` of :class:`datarobot.models.PredictionDataset`: ``single_class_actual_value_column``.
  - Scores and insights on external test sets can be retrieved using
    :class:`ExternalScores<datarobot.ExternalScores>`, :class:`ExternalLiftChart<datarobot.ExternalLiftChart>`, :class:`ExternalRocCurve<datarobot.ExternalRocCurve>`.

- Users can create payoff matrices for generating profit curves for binary classification projects
  using :meth:`PayoffMatrix.create <datarobot.models.PayoffMatrix.create>`.

- Deployment Improvements:

  - :class:`datarobot.models.TargetDrift` can be used to retrieve target drift information.
  - :class:`datarobot.models.FeatureDrift` can be used to retrieve feature drift information.
  - :meth:`Deployment.submit_actuals<datarobot.models.Deployment.submit_actuals>` will submit actuals in batches if the total number of actuals exceeds the limit of one single request.
  - ``Deployment.create_from_custom_model_image`` can be used to create a deployment from a custom model image.
  - Deployments now support predictions data collection that enables prediction requests and results to be saved in Predictions Data Storage. See
    :meth:`Deployment.get_predictions_data_collection_settings<datarobot.models.Deployment.get_predictions_data_collection_settings>`
    and :meth:`Deployment.update_predictions_data_collection_settings<datarobot.models.Deployment.update_predictions_data_collection_settings>` for usage.


- New arguments ``send_notification`` and ``include_feature_discovery_entities`` are added to :meth:`Project.share<datarobot.models.Project.share>`.

- Now it is possible to specify the number of training rows to use in feature impact computation on supported project
  types (that is everything except unsupervised, multi-class, time-series). This does not affect SHAP based feature
  impact. Extended methods:

    - :meth:`Model.request_feature_impact <datarobot.models.Model.request_feature_impact>`
    - :meth:`Model.get_or_request_feature_impact <datarobot.models.Model.get_or_request_feature_impact>`

- A new class :class:`FeatureImpactJob <datarobot.models.FeatureImpactJob>` is added to retrieve Feature Impact
  records with metadata. The regular :class:`Job <datarobot.models.Job>` still works as before.

- Added support for custom models. Please see :ref:`custom model documentation<custom_models>`.
  Classes added:

    - :class:`datarobot.ExecutionEnvironment` and :class:`datarobot.ExecutionEnvironmentVersion` to create and manage
      custom model executions environments
    - :class:`datarobot.CustomInferenceModel` and :class:`datarobot.CustomModelVersion`
      to create and manage custom inference models
    - :class:`datarobot.CustomModelTest` to perform testing of custom models

- Batch Prediction jobs now support forecast and historical Time Series predictions using the new
  argument ``timeseries_settings`` for :meth:`BatchPredictionJob.score <datarobot.models.BatchPredictionJob.score>`.

- Batch Prediction jobs now support scoring to Azure and Google Cloud Storage with methods
  :meth:`BatchPredictionJob.score_azure <datarobot.models.BatchPredictionJob.score_azure>` and
  :meth:`BatchPredictionJob.score_gcp <datarobot.models.BatchPredictionJob.score_gcp>`.


- Now it's possible to create Relationships Configurations to introduce secondary datasets to projects. A configuration specifies additional datasets to be included to a project and how these datasets are related to each other, and the primary dataset. When a relationships configuration is specified for a project, Feature Discovery will create features automatically from these datasets.
    - :meth:`RelationshipsConfiguration.create <datarobot.models.RelationshipsConfiguration.create>` creates a new relationships configuration between datasets
    - :meth:`RelationshipsConfiguration.retrieve <datarobot.models.RelationshipsConfiguration.get>` retrieve the requested relationships configuration
    - :meth:`RelationshipsConfiguration.replace <datarobot.models.RelationshipsConfiguration.replace>` replace the relationships configuration details with new one
    - :meth:`RelationshipsConfiguration.delete <datarobot.models.RelationshipsConfiguration.delete>` delete the relationships configuration

Enhancements
************

- Made creating projects from a dataset easier through the new
  :meth:`Dataset.create_project<datarobot.models.Dataset.create_project>`.

- These methods now provide additional metadata fields in Feature Impact results if called with
  `with_metadata=True`. Fields added: ``rowCount``, ``shapBased``, ``ranRedundancyDetection``,
  ``count``.

    - :meth:`Model.get_feature_impact <datarobot.models.Model.get_feature_impact>`
    - :meth:`Model.request_feature_impact <datarobot.models.Model.request_feature_impact>`
    - :meth:`Model.get_or_request_feature_impact <datarobot.models.Model.get_or_request_feature_impact>`

- Secondary dataset configuration retrieve and deletion is easier now though new
  :meth:`SecondaryDatasetConfigurations.delete<datarobot.models.SecondaryDatasetConfigurations>` soft deletes a Secondary dataset configuration.
  :meth:`SecondaryDatasetConfigurations.get<datarobot.models.SecondaryDatasetConfigurations>` retrieve a Secondary dataset configuration.

- Retrieve relationships configuration which is applied on the given feature discovery project using
  :meth:`Project.get_relationships_configuration<datarobot.models.Project.get_relationships_configuration>`.

Bugfixes
********

- An issue with input validation of the Batch Prediction module
- parent_model_id was not visible for all frozen models
- Batch Prediction jobs that used other output types than `local_file` failed when using `.wait_for_completion()`
- A race condition in the Batch Prediction file scoring logic

API Changes
***********

- Three new fields were added to the :class:`Dataset<datarobot.models.Dataset>` object. This reflects the
  updated fields in the public API routes at `api/v2/datasets/`. The added fields are:

    - processing_state: Current ingestion process state of the dataset
    - row_count: The number of rows in the dataset.
    - size: The size of the dataset as a CSV in bytes.

Deprecation Summary
*******************

- ``datarobot.enums.VARIABLE_TYPE_TRANSFORM.CATEGORICAL`` for is deprecated for the following and will be removed in  v2.22.
    - meth:`Project.batch_features_type_transform`
    - meth:`Project.create_type_transform_feature`

2.20.0
======

New Features
************

- There is a new :class:`Dataset<datarobot.models.Dataset>` object that implements some of the
  public API routes at `api/v2/datasets/`. This also adds two new feature classes and a details
  class.

    - :class:`DatasetFeature<datarobot.models.DatasetFeature>`
    - :class:`DatasetFeatureHistogram<datarobot.models.DatasetFeatureHistogram>`
    - :class:`DatasetDetails<datarobot.DatasetDetails>`

  Functionality:

        - Create a Dataset by uploading from a file, URL or in-memory datasource.

            - :meth:`Dataset.create_from_file<datarobot.models.Dataset.create_from_file>`
            - :meth:`Dataset.create_from_in_memory_data<datarobot.models.Dataset.create_from_in_memory_data>`
            - :meth:`Dataset.create_from_url<datarobot.models.Dataset.create_from_url>`

        - Get Datasets or elements of Dataset with:

            - :meth:`Dataset.list<datarobot.models.Dataset.list>` lists available Datasets
            - :meth:`Dataset.get<datarobot.models.Dataset.get>` gets a specified Dataset
            - :meth:`Dataset.update<datarobot.models.Dataset.get>` updates the Dataset with the latest server information.
            - :meth:`Dataset.get_details<datarobot.models.Dataset.get_details>` gets the DatasetDetails of the Dataset.
            - :meth:`Dataset.get_all_features<datarobot.models.Dataset.get_all_features>` gets a list of the Dataset's Features.
            - :meth:`Dataset.get_file<datarobot.models.Dataset.get_file>` downloads the Dataset as a csv file.
            - :meth:`Dataset.get_projects<datarobot.models.Dataset.get_projects>` gets a list of Projects that use the Dataset.

        - Modify, delete or un-delete a Dataset:

            - :meth:`Dataset.modify<datarobot.models.Dataset.modify>` Changes the name and categories of the Dataset
            - :meth:`Dataset.delete<datarobot.models.Dataset.delete>` soft deletes a Dataset.
            - :meth:`Dataset.un_delete<datarobot.models.Dataset.un_delete>` un-deletes the Dataset. You cannot retrieve the
              IDs of deleted Datasets, so if you want to un-delete a Dataset, you need to store its ID before deletion.

        - You can also create a Project using a `Dataset` with:

            - :meth:`Project.create_from_dataset<datarobot.models.Project.create_from_dataset>`

- It is possible to create an alternative configuration for the secondary dataset which can be used during the prediction

    - :meth:`SecondaryDatasetConfigurations.create <datarobot.models.SecondaryDatasetConfigurations.create>` allow to create secondary dataset configuration

- You can now filter the deployments returned by the :meth:`Deployment.list <datarobot.models.Deployment.list>` command. You can do this by passing an instance of the :class:`~datarobot.models.deployment.DeploymentListFilters` class to the ``filters`` keyword argument. The currently supported filters are:

    - ``role``
    - ``service_health``
    - ``model_health``
    - ``accuracy_health``
    - ``execution_environment_type``
    - ``materiality``

- A new workflow is available for making predictions in time series projects. To that end,
  :class:`PredictionDataset<datarobot.models.PredictionDataset>` objects now contain the following
  new fields:

    - ``forecast_point_range``: The start and end date of the range of dates available for use as the forecast point,
      detected based on the uploaded prediction dataset
    - ``data_start_date``: A datestring representing the minimum primary date of the prediction dataset
    - ``data_end_date``: A datestring representing the maximum primary date of the prediction dataset
    - ``max_forecast_date``: A datestring representing the maximum forecast date of this prediction dataset

  Additionally, users no longer need to specify a ``forecast_point`` or ``predictions_start_date`` and
  ``predictions_end_date`` when uploading datasets for predictions in time series projects. More information can be
  found in the :ref:`time series predictions<new_pred_ux>` documentation.

- Per-class lift chart data is now available for multiclass models using
  :meth:`Model.get_multiclass_lift_chart <datarobot.models.Model.get_multiclass_lift_chart>`.

- Unsupervised projects can now be created using the :meth:`Project.start <datarobot.models.Project.start>`
  and :meth:`Project.set_target <datarobot.models.Project.set_target>` methods by providing ``unsupervised_mode=True``,
  provided that the user has access to unsupervised machine learning functionality. Contact support for more information.

- A new boolean attribute ``unsupervised_mode`` was added to :py:class:`datarobot.DatetimePartitioningSpecification <datarobot.DatetimePartitioningSpecification>`.
  When it is set to True, datetime partitioning for unsupervised time series projects will be constructed for
  nowcasting: ``forecast_window_start=forecast_window_end=0``.

- Users can now configure the start and end of the training partition as well as the end of the validation partition for
  backtests in a datetime-partitioned project. More information and example usage can be found in the
  :ref:`backtesting documentation <backtest_configuration>`.

Enhancements
************

- Updated the user agent header to show which python version.
- :meth:`Model.get_frozen_child_models <datarobot.models.Model.get_frozen_child_models>` can be used to retrieve models that are frozen from a given model
- Added ``datarobot.enums.TS_BLENDER_METHOD`` to make it clearer which blender methods are allowed for use in time
  series projects.

Bugfixes
********
- An issue where uploaded CSV's would loose quotes during serialization causing issues when columns containing line terminators where loaded in a dataframe, has been fixed

- :meth:`Project.get_association_featurelists <datarobot.models.Project.get_association_featurelists>` is now using the correct endpoint name, but the old one will continue to work

- Python API :class:`PredictionServer<datarobot.PredictionServer>` supports now on-premise format of API response.

API Changes
***********

Deprecation Summary
*******************

Configuration Changes
*********************

Documentation Changes
*********************

2.19.0
======

New Features
************

- Projects can be cloned using :meth:`Project.clone_project <datarobot.models.Project.clone_project>`
- Calendars used in time series projects now support having series-specific events, for instance if a holiday only affects some stores. This can be controlled by using new argument of the :meth:`CalendarFile.create <datarobot.CalendarFile.create>` method.
  If multiseries id columns are not provided, calendar is considered to be single series and all events are applied to all series.
- We have expanded prediction intervals availability to the following use-cases:

    - Time series model deployments now support prediction intervals. See
      :meth:`Deployment.get_prediction_intervals_settings<datarobot.models.Deployment.get_prediction_intervals_settings>`
      and :meth:`Deployment.update_prediction_intervals_settings<datarobot.models.Deployment.update_prediction_intervals_settings>` for usage.
    - Prediction intervals are now supported for model exports for time series. To that end, a new optional parameter
      ``prediction_intervals_size`` has been added to :meth:`Model.request_transferable_export <datarobot.models.Model.request_transferable_export>`.

  More details on prediction intervals can be found in the :ref:`prediction intervals documentation <prediction_intervals>`.
- Allowed pairwise interaction groups can now be specified in :py:class:`AdvancedOptions <datarobot.helpers.AdvancedOptions>`.
  They will be used in GAM models during training.
- New deployments features:

    - Update the label and description of a deployment using :meth:`Deployment.update<datarobot.models.Deployment.update>`.
    - :ref:`Association ID setting<deployment_association_id>` can be retrieved and updated.
    - Regression deployments now support :ref:`prediction warnings<deployment_prediction_warning>`.

- For multiclass models now it's possible to get feature impact for each individual target class using
  :meth:`Model.get_multiclass_feature_impact <datarobot.models.Model.get_multiclass_feature_impact>`
- Added support for new :ref:`Batch Prediction API <batch_predictions>`.
- It is now possible to create and retrieve basic, oauth and s3 credentials with
  :py:class:`Credential <datarobot.models.Credential>`.


- It's now possible to get feature association statuses for featurelists using
  :meth:`Project.get_association_featurelists <datarobot.models.Project.get_association_featurelists>`

- You can also pass a specific featurelist_id into
  :meth:`Project.get_associations <datarobot.models.Project.get_associations>`

Enhancements
************

- Added documentation to :meth:`Project.get_metrics <datarobot.models.Project.get_metrics>` to detail the new ``ascending`` field that
  indicates how a metric should be sorted.

- Retraining of a model is processed asynchronously and returns a  ``ModelJob`` immediately.

- Blender models can be retrained on a different set of data or a different feature list.

- Word cloud ngrams now has ``variable`` field representing the source of the ngram.

- Method :meth:`WordCloud.ngrams_per_class <datarobot.models.word_cloud.WordCloud.ngrams_per_class>` can be used to
  split ngrams for better usability in multiclass projects.

- Method :meth:`Project.set_target <datarobot.models.Project.set_target>` support new optional parameters ``featureEngineeringGraphs`` and ``credentials``.

- Method :py:meth:`Project.upload_dataset <datarobot.models.Project.upload_dataset>` and :py:meth:`Project.upload_dataset_from_data_source <datarobot.models.Project.upload_dataset_from_data_source>` support new optional parameter ``credentials``.

- Series accuracy retrieval methods (:meth:`DatetimeModel.get_series_accuracy_as_dataframe <datarobot.models.DatetimeModel.get_series_accuracy_as_dataframe>`
  and :meth:`DatetimeModel.download_series_accuracy_as_csv <datarobot.models.DatetimeModel.download_series_accuracy_as_csv>`)
  for multiseries time series projects now support additional parameters for specifying what data to retrieve, including:

    - ``metric``: Which metric to retrieve scores for
    - ``multiseries_value``: Only returns series with a matching multiseries ID
    - ``order_by``: An attribute by which to sort the results


Bugfixes
********
- An issue when using :meth:`Feature.get <datarobot.models.Feature.get>` and :meth:`ModelingFeature.get <datarobot.models.ModelingFeature.get>` to retrieve summarized categorical feature has been fixed.

API Changes
***********
- The datarobot package is now no longer a
  `namespace package <https://packaging.python.org/guides/packaging-namespace-packages/>`_.
- ``datarobot.enums.BLENDER_METHOD.FORECAST_DISTANCE`` is removed (deprecated in 2.18.0).

Documentation Changes
*********************

- Updated :ref:`Residuals charts <residuals_chart>` documentation to reflect that the data rows include row numbers from the source dataset for projects
  created in DataRobot 5.3 and newer.

2.18.0
======

New Features
************
- :ref:`Residuals charts <residuals_chart>` can now be retrieved for non-time-aware regression models.

- :ref:`Deployment monitoring <deployment_monitoring>` can now be used to retrieve service stats, service health, accuracy info, permissions, and feature lists for deployments.

- :ref:`Time series <time_series>` projects now support the Average by Forecast Distance blender, configured with more than one Forecast Distance. The blender blends the selected models, selecting the best three models based on the backtesting score for each Forecast Distance and averaging their predictions. The new blender method ``FORECAST_DISTANCE_AVG`` has been added to ``datarobot.enums.BLENDER_METHOD``.

- :py:meth:`Deployment.submit_actuals <datarobot.models.Deployment.submit_actuals>` can now be used to submit data about actual results from a deployed model, which can be used to calculate accuracy metrics.

Enhancements
************
- Monotonic constraints are now supported for OTV projects. To that end, the parameters ``monotonic_increasing_featurelist_id`` and ``monotonic_decreasing_featurelist_id`` can be specified in calls to :meth:`Model.train_datetime <datarobot.models.Model.train_datetime>` or :meth:`Project.train_datetime <datarobot.models.Project.train_datetime>`.

- When :py:meth:`retrieving information about features <datarobot.models.Feature.get>`, information about summarized categorical variables is now available in a new ``keySummary``.

- For :py:class:`Word Clouds <datarobot.models.word_cloud.WordCloud>` in multiclass projects, values of the target class for corresponding word or ngram can now be passed using the new ``class`` parameter.

- Listing deployments using :py:meth:`Deployment.list <datarobot.models.Deployment.list>` now support sorting and searching the results using the new ``order_by`` and ``search`` parameters.

- You can now get the model associated with a model job by getting the ``model`` variable on the :py:class:`model job object <datarobot.models.ModelJob>`.

- The :class:`Blueprint <datarobot.models.Blueprint>` class can now retrieve the ``recommended_featurelist_id``, which indicates which feature list is recommended for this blueprint. If the field is not present, then there is no recommended feature list for this blueprint.

- The :class:`Model <datarobot.models.Model>` class now can be used to retrieve the ``model_number``.

- The method :py:meth:`Model.get_supported_capabilities <datarobot.models.Model.get_supported_capabilities>` now has an extra field ``supportsCodeGeneration`` to explain whether the model supports code generation.

- Calls to :py:meth:`Project.start <datarobot.models.Project.start>` and :py:meth:`Project.upload_dataset <datarobot.models.Project.upload_dataset>` now support uploading data via S3 URI and `pathlib.Path` objects.

- Errors upon connecting to DataRobot are now clearer when an incorrect API Token is used.

- The datarobot package is now a `namespace package <https://packaging.python.org/guides/packaging-namespace-packages/>`_.

Deprecation Summary
*******************

- ``datarobot.enums.BLENDER_METHOD.FORECAST_DISTANCE`` is deprecated and will be removed in 2.19. Use ``FORECAST_DISTANCE_ENET`` instead.

Documentation Changes
*********************
- Various typo and wording issues have been addressed.

- A new notebook showing regression-specific features is now been added to the :ref:`examples<examples_index>`.

- Documentation for :ref:`Access lists <sharing>` has been added.

2.17.0
======

New Features
************
- :ref:`Deployments <deployments_overview>` can now be managed via the API by using the new :py:class:`Deployment <datarobot.models.Deployment>` class.

- Users can now list available prediction servers using :meth:`PredictionServer.list <datarobot.PredictionServer.list>`.

- When :class:`specifying datetime partitioning <datarobot.DatetimePartitioningSpecification>` settings , :ref:`time series <time_series>` projects can now mark individual features as excluded from feature derivation using the
  :py:class:`FeatureSettings.do_not_derive <datarobot.FeatureSettings>` attribute. Any features not specified will be assigned according to the :py:class:`DatetimePartitioningSpecification.default_to_do_not_derive <datarobot.DatetimePartitioning>` value.

- Users can now submit multiple feature type transformations in a single batch request using :py:meth:`Project.batch_features_type_transform <datarobot.models.Project.batch_features_type_transform>`.

- :ref:`Advanced Tuning <advanced_tuning>` for non-Eureqa models (beta feature) is now enabled by default for all users.
  As of v2.17, all models are now supported other than blenders, open source, prime, scaleout, baseline and user-created.

- Information on feature clustering and the association strength between pairs of numeric or categorical features is now available.
  :py:meth:`Project.get_associations <datarobot.models.Project.get_associations>` can be used to retrieve pairwise feature association statistics and
  :py:meth:`Project.get_association_matrix_details <datarobot.models.Project.get_association_matrix_details>` can be used to get a sample of the actual values used to measure association strength.

Enhancements
************
- `number_of_do_not_derive_features` has been added to the :py:class:`datarobot.DatetimePartitioning <datarobot.DatetimePartitioning>` class to specify the number of features that are marked as excluded from derivation.
- Users with PyYAML>=5.1 will no longer receive a warning when using the `datarobot` package
- It is now possible to use files with unicode names for creating projects and prediction jobs.
- Users can now embed DataRobot-generated content in a :class:`ComplianceDocTemplate <datarobot.models.compliance_doc_template.ComplianceDocTemplate>` using keyword tags. :ref:`See here <automated_documentation_overview>` for more details.
- The field ``calendar_name`` has been added to :py:class:`datarobot.DatetimePartitioning <datarobot.DatetimePartitioning>` to display the name of the calendar used for a project.
- :ref:`Prediction intervals <prediction_intervals>` are now supported for start-end retrained models in a time series project.
- Previously, all backtests had to be run before :ref:`prediction intervals <prediction_intervals>` for a time series project could be requested with predictions.
  Now, backtests will be computed automatically if needed when prediction intervals are requested.

Bugfixes
********
- An issue affecting time series project creation for irregularly spaced dates has been fixed.
- :class:`ComplianceDocTemplate <datarobot.models.compliance_doc_template.ComplianceDocTemplate>` now supports empty text blocks in user sections.
- An issue when using :meth:`Predictions.get <datarobot.models.Predictions.get>` to retrieve predictions metadata has been fixed.

Documentation Changes
*********************
- An overview on working with class ``ComplianceDocumentation`` and :class:`ComplianceDocTemplate <datarobot.models.compliance_doc_template.ComplianceDocTemplate>` has been created. :ref:`See here <automated_documentation_overview>` for more details.


2.16.0
======

New Features
************
- Three new methods for Series Accuracy have been added to the :class:`DatetimeModel <datarobot.models.DatetimeModel>` class.

    - Start a request to calculate Series Accuracy with
      :meth:`DatetimeModel.compute_series_accuracy <datarobot.models.DatetimeModel.compute_series_accuracy>`
    - Once computed, Series Accuracy can be retrieved as a pandas.DataFrame using
      :meth:`DatetimeModel.get_series_accuracy_as_dataframe <datarobot.models.DatetimeModel.get_series_accuracy_as_dataframe>`
    - Or saved as a CSV using
      :meth:`DatetimeModel.download_series_accuracy_as_csv <datarobot.models.DatetimeModel.download_series_accuracy_as_csv>`

- Users can now access :ref:`prediction intervals <prediction_intervals>` data for each prediction with a :class:`DatetimeModel <datarobot.models.DatetimeModel>`.
  For each model, prediction intervals estimate the range of values DataRobot expects actual values of the target to fall within.
  They are similar to a confidence interval of a prediction, but are based on the residual errors measured during the
  backtesting for the selected model.

Enhancements
************
- Information on the effective feature derivation window is now available for :ref:`time series projects <time_series>` to specify the full span of historical data
  required at prediction time. It may be longer than the feature derivation window of the project depending on the differencing settings used.

  Additionally, more of the project partitioning settings are also available on the
  :class:`DatetimeModel <datarobot.models.DatetimeModel>` class.  The new attributes are:

    - ``effective_feature_derivation_window_start``
    - ``effective_feature_derivation_window_end``
    - ``forecast_window_start``
    - ``forecast_window_end``
    - ``windows_basis_unit``

- Prediction metadata is now included in the return of :meth:`Predictions.get <datarobot.models.Predictions.get>`

Documentation Changes
*********************
- Various typo and wording issues have been addressed.
- The example data that was meant to accompany the Time Series examples has been added to the
  zip file of the download in the :ref:`examples<examples_index>`.

2.15.1
======

Enhancements
************
- :meth:`CalendarFile.get_access_list <datarobot.CalendarFile.get_access_list>` has been added to the :class:`CalendarFile <datarobot.CalendarFile>` class to return a list of users with access to a calendar file.
- A ``role`` attribute has been added to the :class:`CalendarFile <datarobot.CalendarFile>` class to indicate the access level a current user has to a calendar file. For more information on the specific access levels, see the :ref:`sharing <sharing>` documentation.

Bugfixes
********
- Previously, attempting to retrieve the ``calendar_id`` of a project without a set target would result in an error.
  This has been fixed to return ``None`` instead.


2.15.0
======

New Features
************
- Previously available for only Eureqa models, Advanced Tuning methods and objects, including
  :meth:`Model.start_advanced_tuning_session <datarobot.models.Model.start_advanced_tuning_session>`,
  :meth:`Model.get_advanced_tuning_parameters <datarobot.models.Model.get_advanced_tuning_parameters>`,
  :meth:`Model.advanced_tune <datarobot.models.Model.advanced_tune>`, and
  :class:`AdvancedTuningSession <datarobot.models.advanced_tuning.AdvancedTuningSession>`,
  now support all models other than blender, open source, and user-created models.  Use of
  Advanced Tuning via API for non-Eureqa models is in beta and not available by default, but can be
  enabled.
- Calendar Files for time series projects can now be created and managed through the :class:`CalendarFile <datarobot.CalendarFile>` class.

Enhancements
************
* The dataframe returned from
  :py:meth:`datarobot.PredictionExplanations.get_all_as_dataframe` will now have
  each class label `class_X` be the same from row to row.
* The client is now more robust to networking issues by default. It will retry on more errors and respects `Retry-After` headers in HTTP 413, 429, and 503 responses.
* Added Forecast Distance blender for Time-Series projects configured with more than one Forecast
  Distance. It blends the selected models creating separate linear models for each Forecast Distance.
* :py:class:`Project <datarobot.models.Project>` can now be :ref:`shared <sharing>` with other users.
* :py:meth:`Project.upload_dataset <datarobot.models.Project.upload_dataset>` and :py:meth:`Project.upload_dataset_from_data_source <datarobot.models.Project.upload_dataset_from_data_source>` will return a :py:class:`PredictionDataset <datarobot.models.PredictionDataset>` with ``data_quality_warnings`` if potential problems exist around the uploaded dataset.
* ``relax_known_in_advance_features_check`` has been added to :py:meth:`Project.upload_dataset <datarobot.models.Project.upload_dataset>` and :py:meth:`Project.upload_dataset_from_data_source <datarobot.models.Project.upload_dataset_from_data_source>` to allow missing values from the known in advance features in the forecast window at prediction time.
* ``cross_series_group_by_columns`` has been added to :py:class:`datarobot.DatetimePartitioning <datarobot.DatetimePartitioning>` to allow users the ability to indicate how to further split series into related groups.
* Information retrieval for :py:class:`ROC Curve <datarobot.models.roc_curve.RocCurve>` has been extended to include ``fraction_predicted_as_positive``, ``fraction_predicted_as_negative``, ``lift_positive`` and ``lift_negative``

Bugfixes
********
* Fixes an issue where the client would not be usable if it could not be sure it was compatible with the configured
  server

API Changes
***********
- Methods for creating :py:class:`datarobot.models.Project`: `create_from_mysql`, `create_from_oracle`, and `create_from_postgresql`, deprecated in 2.11, have now been removed.
  Use :py:meth:`datarobot.models.Project.create_from_data_source` instead.
- :py:class:`datarobot.FeatureSettings <datarobot.FeatureSettings>` attribute `apriori`, deprecated in 2.11, has been removed.
  Use :py:class:`datarobot.FeatureSettings.known_in_advance <datarobot.FeatureSettings>` instead.
- :py:class:`datarobot.DatetimePartitioning <datarobot.DatetimePartitioning>` attribute `default_to_a_priori`, deprecated in 2.11, has been removed. Use
  :py:class:`datarobot.DatetimePartitioning.known_in_advance <datarobot.DatetimePartitioning>` instead.
- :py:class:`datarobot.DatetimePartitioningSpecification <datarobot.DatetimePartitioning>` attribute `default_to_a_priori`, deprecated in 2.11, has been removed.
  Use :py:class:`datarobot.DatetimePartitioningSpecification.known_in_advance <datarobot.DatetimePartitioning>`
  instead.

Deprecation Summary
*******************

Configuration Changes
*********************
- Now requires dependency on package `requests <https://pypi.org/project/requests/>`_  to be at least version 2.21.
- Now requires dependency on package `urllib3 <https://pypi.org/project/urllib3/>`_  to be at least version 1.24.

Documentation Changes
*********************
- Advanced model insights notebook extended to contain information on visualization of cumulative gains and lift charts.

2.14.2
======

Bugfixes
********
- Fixed an issue where searches of the HTML documentation would sometimes hang indefinitely

Documentation Changes
*********************
- Python3 is now the primary interpreter used to build the docs (this does not affect the ability to use the
  package with Python2)

2.14.1
======

Documentation Changes
*********************
 - Documentation for the Model Deployment interface has been removed after the corresponding interface was removed in 2.13.0.

2.14.0
======
New Features
************
- The new method :meth:`Model.get_supported_capabilities <datarobot.models.Model.get_supported_capabilities>`
  retrieves a summary of the capabilities supported by a particular model,
  such as whether it is eligible for Prime and whether it has word cloud data available.
- New class for working with model compliance documentation feature of DataRobot:
  class ``ComplianceDocumentation``
- New class for working with compliance documentation templates:
  :class:`ComplianceDocTemplate <datarobot.models.compliance_doc_template.ComplianceDocTemplate>`
- New class :py:class:`FeatureHistogram <datarobot.models.FeatureHistogram>` has been added to
  retrieve feature histograms for a requested maximum bin count
- Time series projects now support binary classification targets.
- Cross series features can now be created within time series multiseries projects using the
  ``use_cross_series_features`` and ``aggregation_type`` attributes of the
  :py:class:`datarobot.DatetimePartitioningSpecification
  <datarobot.DatetimePartitioningSpecification>`.
  See the :ref:`Time Series <time_series>` documentation for more info.


Enhancements
************
- Client instantiation now checks the endpoint configuration and provides more informative error messages.
  It also automatically corrects HTTP to HTTPS if the server responds with a redirect to HTTPS.
- :meth:`Project.upload_dataset <datarobot.models.Project.upload_dataset>` and :meth:`Project.create <datarobot.models.Project.create>`
  now accept an optional parameter of ``dataset_filename`` to specify a file name for the dataset.
  This is ignored for url and file path sources.
- New optional parameter `fallback_to_parent_insights` has been added to :meth:`Model.get_lift_chart <datarobot.models.Model.get_lift_chart>`,
  :meth:`Model.get_all_lift_charts <datarobot.models.Model.get_all_lift_charts>`, :meth:`Model.get_confusion_chart <datarobot.models.Model.get_confusion_chart>`,
  :meth:`Model.get_all_confusion_charts <datarobot.models.Model.get_all_confusion_charts>`, :meth:`Model.get_roc_curve <datarobot.models.Model.get_roc_curve>`,
  and :meth:`Model.get_all_roc_curves <datarobot.models.Model.get_all_roc_curves>`.  When `True`, a frozen model with
  missing insights will attempt to retrieve the missing insight data from its parent model.
- New ``number_of_known_in_advance_features`` attribute has been added to the
  :py:class:`datarobot.DatetimePartitioning <datarobot.DatetimePartitioning>` class.
  The attribute specifies number of features that are marked as known in advance.
- :meth:`Project.set_worker_count <datarobot.models.Project.set_worker_count>` can now update the worker count on
  a project to the maximum number available to the user.
- :ref:`Recommended Models API <recommended_models>` can now be used to retrieve
  model recommendations for datetime partitioned projects
- Timeseries projects can now accept feature derivation and forecast windows intervals in terms of
  number of the rows rather than a fixed time unit. :class:`DatetimePartitioningSpecification <datarobot.DatetimePartitioningSpecification>`
  and :meth:`Project.set_target <datarobot.models.Project.set_target>` support new optional parameter `windowsBasisUnit`, either 'ROW' or detected time unit.
- Timeseries projects can now accept feature derivation intervals, forecast windows, forecast points and prediction start/end dates in milliseconds.
- :class:`DataSources <datarobot.DataSource>` and :class:`DataStores <datarobot.DataStore>` can now
  be :ref:`shared <sharing>` with other users.
- Training predictions for datetime partitioned projects now support the new data subset
  `dr.enums.DATA_SUBSET.ALL_BACKTESTS` for requesting the predictions for all backtest validation
  folds.

API Changes
*******************
- The model recommendation type "Recommended" (deprecated in version 2.13.0) has been removed.

Documentation Changes
*********************

- Example notebooks have been updated:
    - Notebooks now work in Python 2 and Python 3
    - A notebook illustrating time series capability has been added
    - The financial data example has been replaced with an updated introductory example.
- To supplement the embedded Python notebooks in both the PDF and HTML docs bundles, the notebook files and supporting data can now be downloaded from the HTML docs bundle.
- Fixed a minor typo in the code sample for ``get_or_request_feature_impact``

2.13.0
======

New Features
************
- The new method :meth:`Model.get_or_request_feature_impact <datarobot.models.Model.get_or_request_feature_impact>` functionality will attempt to request feature impact
  and return the newly created feature impact object or the existing object so two calls are no longer required.
- New methods and objects, including
  :meth:`Model.start_advanced_tuning_session <datarobot.models.Model.start_advanced_tuning_session>`,
  :meth:`Model.get_advanced_tuning_parameters <datarobot.models.Model.get_advanced_tuning_parameters>`,
  :meth:`Model.advanced_tune <datarobot.models.Model.advanced_tune>`, and
  :class:`AdvancedTuningSession <datarobot.models.advanced_tuning.AdvancedTuningSession>`,
  were added to support the setting of Advanced Tuning parameters. This is currently supported for
  Eureqa models only.
- New ``is_starred`` attribute has been added to the :py:class:`Model <datarobot.models.Model>` class. The attribute
  specifies whether a model has been marked as starred by user or not.
- Model can be marked as starred or being unstarred with :meth:`Model.star_model <datarobot.models.Model.star_model>` and :meth:`Model.unstar_model <datarobot.models.Model.unstar_model>`.
- When listing models with :meth:`Project.get_models <datarobot.models.Project.get_models>`, the model list can now be filtered by the ``is_starred`` value.
- A custom prediction threshold may now be configured for each model via :meth:`Model.set_prediction_threshold <datarobot.models.Model.set_prediction_threshold>`.  When making
  predictions in binary classification projects, this value will be used when deciding between the positive and negative classes.
- :meth:`Project.check_blendable <datarobot.models.Project.check_blendable>` can be used to confirm if a particular group of models are eligible for blending as
  some are not, e.g. scaleout models and datetime models with different training lengths.
- Individual cross validation scores can be retrieved for new models using :meth:`Model.get_cross_validation_scores <datarobot.models.Model.get_cross_validation_scores>`.

Enhancements
************
- Python 3.7 is now supported.
- Feature impact now returns not only the impact score for the features but also whether they were
  detected to be redundant with other high-impact features.
- A new ``is_blocked`` attribute has been added to the :py:class:`Job <datarobot.models.Job>`
  class, specifying whether a job is blocked from execution because one or more dependencies are not
  yet met.
- The :py:class:`Featurelist <datarobot.models.Featurelist>` object now has new attributes reporting
  its creation time, whether it was created by a user or by DataRobot, and the number of models
  using the featurelist, as well as a new description field.
- Featurelists can now be renamed and have their descriptions updated with
  :py:meth:`Featurelist.update <datarobot.models.Featurelist.update>` and
  :py:meth:`ModelingFeaturelist.update <datarobot.models.ModelingFeaturelist.update>`.
- Featurelists can now be deleted with
  :py:meth:`Featurelist.delete <datarobot.models.Featurelist.delete>`
  and :py:meth:`ModelingFeaturelist.delete <datarobot.models.ModelingFeaturelist.delete>`.
- :meth:`ModelRecommendation.get <datarobot.models.ModelRecommendation.get>` now accepts an optional
  parameter of type ``datarobot.enums.RECOMMENDED_MODEL_TYPE`` which can be used to get a specific
  kind of recommendation.
- Previously computed predictions can now be listed and retrieved with the
  :class:`Predictions <datarobot.models.Predictions>` class, without requiring a
  reference to the original :py:class:`PredictJob <datarobot.models.PredictJob>`.

Bugfixes
********
- The Model Deployment interface which was previously visible in the client has been removed to
  allow the interface to mature, although the raw API is available as a "beta" API without full
  backwards compatibility support.

API Changes
***********
- Added support for retrieving the Pareto Front of a Eureqa model. See
  :py:class:`ParetoFront <datarobot.models.pareto_front.ParetoFront>`.
- A new recommendation type "Recommended for Deployment" has been added to
  :py:class:`ModelRecommendation <datarobot.models.ModelRecommendation>` which is now returns as the
  default recommended model when available. See :ref:`model_recommendation`.

Deprecation Summary
*******************
- The feature previously referred to as "Reason Codes" has been renamed to "Prediction
  Explanations", to provide increased clarity and accessibility. The old
  ReasonCodes interface has been deprecated and replaced with
  :py:class:`PredictionExplanations <datarobot.PredictionExplanations>`.
- The recommendation type "Recommended" is deprecated and  will no longer be returned
  in v2.14 of the API.

Documentation Changes
*********************

- Added a new documentation section :ref:`model_recommendation`.
- Time series projects support multiseries as well as single series data. They are now documented in
  the :ref:`Time Series Projects <time_series>` documentation.

2.12.0
======

New Features
************
- Some models now have Missing Value reports allowing users with access to uncensored blueprints to
  retrieve a detailed breakdown of how numeric imputation and categorical converter tasks handled
  missing values. See the :ref:`documentation <missing_values_report>` for more information on the
  report.

2.11.0
======

New Features
************
- The new ``ModelRecommendation`` class can be used to retrieve the recommended models for a
  project.
- A new helper method cross_validate was added to class Model. This method can be used to request
  Model's Cross Validation score.
- Training a model with monotonic constraints is now supported. Training with monotonic
  constraints allows users to force models to learn monotonic relationships with respect to some features and the target. This helps users create accurate models that comply with regulations (e.g. insurance, banking). Currently, only certain blueprints (e.g. xgboost) support this feature, and it is only supported for regression and binary classification projects.
- DataRobot now supports "Database Connectivity", allowing databases to be used
  as the source of data for projects and prediction datasets. The feature works
  on top of the JDBC standard, so a variety of databases conforming to that standard are available;
  a list of databases with tested support for DataRobot is available in the user guide
  in the web application. See :ref:`Database Connectivity <database_connectivity_overview>`
  for details.
- Added a new feature to retrieve feature logs for time series projects. Check
  :py:meth:`datarobot.DatetimePartitioning.feature_log_list` and
  :py:meth:`datarobot.DatetimePartitioning.feature_log_retrieve` for details.

API Changes
***********
- New attributes supporting monotonic constraints have been added to the
  :py:class:`AdvancedOptions <datarobot.helpers.AdvancedOptions>`,
  :py:class:`Project <datarobot.models.Project>`,
  :py:class:`Model <datarobot.models.Model>`, and :py:class:`Blueprint <datarobot.models.Blueprint>`
  classes. See :ref:`monotonic constraints<monotonic_constraints>` for more information on how to
  configure monotonic constraints.
- New parameters `predictions_start_date` and `predictions_end_date` added to
  :py:meth:`Project.upload_dataset <datarobot.models.Project.upload_dataset>` to support bulk
  predictions upload for time series projects.

Deprecation Summary
*******************
- Methods for creating :py:class:`datarobot.models.Project`: `create_from_mysql`, `create_from_oracle`, and `create_from_postgresql`, have been deprecated and will be removed in 2.14.
  Use :py:meth:`datarobot.models.Project.create_from_data_source` instead.
- :py:class:`datarobot.FeatureSettings <datarobot.FeatureSettings>` attribute `apriori`, has been deprecated and will be removed in 2.14.
  Use :py:class:`datarobot.FeatureSettings.known_in_advance <datarobot.FeatureSettings>` instead.
- :py:class:`datarobot.DatetimePartitioning <datarobot.DatetimePartitioning>` attribute `default_to_a_priori`, has been deprecated and will be removed in 2.14.
  :py:class:`datarobot.DatetimePartitioning.known_in_advance <datarobot.DatetimePartitioning>` instead.
- :py:class:`datarobot.DatetimePartitioningSpecification <datarobot.DatetimePartitioning>` attribute `default_to_a_priori`, has been deprecated and will be removed in 2.14.
  Use :py:class:`datarobot.DatetimePartitioningSpecification.known_in_advance <datarobot.DatetimePartitioning>`
  instead.

Configuration Changes
*********************
- Retry settings compatible with those offered by urllib3\'s `Retry <https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.retry.Retry>`_
  interface can now be configured. By default, we will now retry connection errors that prevented requests from arriving at the server.

Documentation Changes
*********************
- "Advanced Model Insights" example has been updated to properly handle bin weights when rebinning.

2.9.0
=====

New Features
************
- New ``ModelDeployment`` class can be used to track status and health of models deployed for
  predictions.

Enhancements
************
- DataRobot API now supports creating 3 new blender types - Random Forest, TensorFlow, LightGBM.
- Multiclass projects now support blenders creation for 3 new blender types as well as Average
  and ENET blenders.
- Models can be trained by requesting a particular row count using the new ``training_row_count``
  argument with `Project.train`, `Model.train` and `Model.request_frozen_model` in non-datetime
  partitioned projects, as an alternative to the previous option of specifying a desired
  percentage of the project dataset. Specifying model size by row count is recommended when
  the float precision of ``sample_pct`` could be problematic, e.g. when training on a small
  percentage of the dataset or when training up to partition boundaries.
- New attributes ``max_train_rows``, ``scaleout_max_train_pct``, and ``scaleout_max_train_rows``
  have been added to :py:class:`Project <datarobot.models.Project>`. ``max_train_rows`` specified the equivalent
  value to the existing ``max_train_pct`` as a row count. The scaleout fields can be used to see how
  far scaleout models can be trained on projects, which for projects taking advantage of scalable
  ingest may exceed the limits on the data available to non-scaleout blueprints.
- Individual features can now be marked as a priori or not a priori using the new `feature_settings`
  attribute when setting the target or specifying datetime partitioning settings on time
  series projects. Any features not specified in the `feature_settings` parameter will be
  assigned according to the `default_to_a_priori` value.
- Three new options have been made available in the
  :py:class:`datarobot.DatetimePartitioningSpecification` class to fine-tune how time-series projects
  derive modeling features. `treat_as_exponential` can control whether data is analyzed as
  an exponential trend and transformations like log-transform are applied.
  `differencing_method` can control which differencing method to use for stationary data.
  `periodicities` can be used to specify periodicities occurring within the data.
  All are optional and defaults will be chosen automatically if they are unspecified.

API Changes
***********
- Now ``training_row_count`` is available on non-datetime models as well as `rowCount` based
  datetime models. It reports the number of rows used to train the model (equivalent to
  ``sample_pct``).
- Features retrieved from ``Feature.get`` now include ``target_leakage``.

2.8.1
=====

Bugfixes
********
- The documented default connect_timeout will now be correctly set for all configuration mechanisms,
  so that requests that fail to reach the DataRobot server in a reasonable amount of time will now
  error instead of hanging indefinitely. If you observe that you have started seeing
  ``ConnectTimeout`` errors, please configure your connect_timeout to a larger value.
- Version of ``trafaret`` library this package depends on is now pinned to ``trafaret>=0.7,<1.1``
  since versions outside that range are known to be incompatible.


2.8.0
=====

New Features
************
- The DataRobot API supports the creation, training, and predicting of multiclass classification
  projects. DataRobot, by default, handles a dataset with a numeric target column as regression.
  If your data has a numeric cardinality of fewer than 11 classes, you can override this behavior to
  instead create a multiclass classification project from the data. To do so, use the set_target
  function, setting target_type='Multiclass'. If DataRobot recognizes your data as categorical, and
  it has fewer than 11 classes, using multiclass will create a project that classifies which label
  the data belongs to.
- The DataRobot API now includes Rating Tables. A rating table is an exportable csv representation
  of a model. Users can influence predictions by modifying them and creating a new model with the
  modified table. See the :ref:`documentation<rating_table>` for more information on how to use
  rating tables.
- `scaleout_modeling_mode` has been added to the `AdvancedOptions` class
  used when setting a project target. It can be used to control whether
  scaleout models appear in the autopilot and/or available blueprints.
  Scaleout models are only supported in the Hadoop environment with
  the corresponding user permission set.
- A new premium add-on product, Time Series, is now available. New projects can be created as time series
  projects which automatically derive features from past data and forecast the future. See the
  :ref:`time series documentation<time_series>` for more information.
- The `Feature` object now returns the EDA summary statistics (i.e., mean, median, minimum, maximum,
  and standard deviation) for features where this is available (e.g., numeric, date, time,
  currency, and length features). These summary statistics will be formatted in the same format
  as the data it summarizes.
- The DataRobot API now supports Training Predictions workflow. Training predictions are made by a
  model for a subset of data from original dataset. User can start a job which will make those
  predictions and retrieve them. See the :ref:`documentation<predictions>`
  for more information on how to use training predictions.
- DataRobot now supports retrieving a :ref:`model blueprint chart<model_blueprint_chart>` and a
  :ref:`model blueprint docs<model_blueprint_doc>`.
- With the introduction of Multiclass Classification projects, DataRobot needed a better way to
  explain the performance of a multiclass model so we created a new Confusion Chart. The API
  now supports retrieving and interacting with confusion charts.

Enhancements
************
- `DatetimePartitioningSpecification` now includes the optional `disable_holdout` flag that can
  be used to disable the holdout fold when creating a project with datetime partitioning.
- When retrieving reason codes on a project using an exposure column, predictions that are adjusted
  for exposure can be retrieved.
- File URIs can now be used as sourcedata when creating a project or uploading a prediction dataset.
  The file URI must refer to an allowed location on the server, which is configured as described in
  the user guide documentation.
- The advanced options available when setting the target have been extended to include the new
  parameter 'events_count' as a part of the AdvancedOptions object to allow specifying the
  events count column. See the user guide documentation in the webapp for more information
  on events count.
- PredictJob.get_predictions now returns predicted probability for each class in the dataframe.
- PredictJob.get_predictions now accepts prefix parameter to prefix the classes name returned in the
  predictions dataframe.

API Changes
***********
- Add `target_type` parameter to set_target() and start(), used to override the project default.

2.7.2
=====

Documentation Changes
*********************

- Updated link to the publicly hosted documentation.

2.7.1
=====

Documentation Changes
*********************

- Online documentation hosting has migrated from PythonHosted to Read The Docs. Minor code changes
  have been made to support this.

2.7.0
=====

New Features
************
- Lift chart data for models can be retrieved using the `Model.get_lift_chart` and
  `Model.get_all_lift_charts` methods.
- ROC curve data for models in classification projects can be retrieved using the
  `Model.get_roc_curve` and `Model.get_all_roc_curves` methods.
- Semi-automatic autopilot mode is removed.
- Word cloud data for text processing models can be retrieved using `Model.get_word_cloud` method.
- Scoring code JAR file can be downloaded for models supporting code generation.

Enhancements
************
- A `__repr__` method has been added to the `PredictionDataset` class to improve readability when
  using the client interactively.
- `Model.get_parameters` now includes an additional key in the derived features it includes,
  showing the coefficients for individual stages of multistage models (e.g. Frequency-Severity
  models).
- When training a `DatetimeModel` on a window of data, a `time_window_sample_pct` can be specified
  to take a uniform random sample of the training data instead of using all data within the window.
- Installing of DataRobot package now has an "Extra Requirements" section that will install all of
  the dependencies needed to run the example notebooks.

Documentation Changes
*********************
- A new example notebook describing how to visualize some of the newly available model insights
  including lift charts, ROC curves, and word clouds has been added to the examples section.
- A new section for `Common Issues` has been added to `Getting Started` to help debug issues related to client installation and usage.


2.6.1
=====

Bugfixes
********

- Fixed a bug with `Model.get_parameters` raising an exception on some valid parameter values.

Documentation Changes
*********************

- Fixed sorting order in Feature Impact example code snippet.

2.6.0
=====

New Features
************
- A new partitioning method (datetime partitioning) has been added. The recommended workflow is to
  preview the partitioning by creating a `DatetimePartitioningSpecification` and passing it into
  `DatetimePartitioning.generate`, inspect the results and adjust as needed for the specific project
  dataset by adjusting the `DatetimePartitioningSpecification` and re-generating, and then set the
  target by passing the final `DatetimePartitioningSpecification` object to the partitioning_method
  parameter of `Project.set_target`.
- When interacting with datetime partitioned projects, `DatetimeModel` can be used to access more
  information specific to models in datetime partitioned projects. See
  :ref:`the documentation<datetime_modeling_workflow>` for more information on differences in the
  modeling workflow for datetime partitioned projects.
- The advanced options available when setting the target have been extended to include the new
  parameters 'offset' and 'exposure' (part of the AdvancedOptions object) to allow specifying
  offset and exposure columns to apply to predictions generated by models within the project.
  See the user guide documentation in the webapp for more information on offset
  and exposure columns.
- Blueprints can now be retrieved directly by project_id and blueprint_id via `Blueprint.get`.
- Blueprint charts can now be retrieved directly by project_id and blueprint_id via
  `BlueprintChart.get`. If you already have an instance of `Blueprint` you can retrieve its
  chart using `Blueprint.get_chart`.
- Model parameters can now be retrieved using `ModelParameters.get`. If you already have an
  instance of `Model` you can retrieve its parameters using `Model.get_parameters`.
- Blueprint documentation can now be retrieved using `Blueprint.get_documents`. It will contain
  information about the task, its parameters and (when available) links and references to
  additional sources.
- The DataRobot API now includes Reason Codes. You can now compute reason codes for prediction
  datasets. You are able to specify thresholds on which rows to compute reason codes for to speed
  up computation by skipping rows based on the predictions they generate. See the reason codes
  :ref:`documentation<reason_codes>` for more information.

Enhancements
************

- A new parameter has been added to the `AdvancedOptions` used with `Project.set_target`. By
  specifying `accuracyOptimizedMb=True` when creating `AdvancedOptions`, longer-running models
  that may have a high accuracy will be included in the autopilot and made available to run
  manually.
- A new option for `Project.create_type_transform_feature` has been added which explicitly
  truncates data when casting numerical data as categorical data.
- Added 2 new blenders for projects that use MAD or Weighted MAD as a metric. The MAE blender uses
  BFGS optimization to find linear weights for the blender that minimize mean absolute error
  (compared to the GLM blender, which finds linear weights that minimize RMSE), and the MAEL1
  blender uses BFGS optimization to find linear weights that minimize MAE + a L1 penalty on the
  coefficients (compared to the ENET blender, which minimizes RMSE + a combination of the L1 and L2
  penalty on the coefficients).

Bugfixes
********

- Fixed a bug (affecting Python 2 only) with printing any model (including frozen and prime models)
  whose model_type is not ascii.
- FrozenModels were unable to correctly use methods inherited from Model. This has been fixed.
- When calling `get_result` for a Job, ModelJob, or PredictJob that has errored, `AsyncProcessUnsuccessfulError` will now be raised instead of `JobNotFinished`, consistently with the behavior of `get_result_when_complete`.

Deprecation Summary
*******************

- Support for the experimental Recommender Problems projects has been removed. Any code relying on
  `RecommenderSettings` or the `recommender_settings` argument of `Project.set_target` and
  `Project.start` will error.
- ``Project.update``, deprecated in v2.2.32, has been removed in favor of specific updates:
  ``rename``, ``unlock_holdout``, ``set_worker_count``.

Documentation Changes
*********************

- The link to Configuration from the Quickstart page has been fixed.

2.5.1
=====

Bugfixes
********

- Fixed a bug (affecting Python 2 only) with printing blueprints  whose names are
  not ascii.
- Fixed an issue where the weights column (for weighted projects) did not appear
  in the `advanced_options` of a `Project`.


2.5.0
=====

New Features
************

- Methods to work with blender models have been added. Use `Project.blend` method to create new blenders,
  `Project.get_blenders` to get the list of existing blenders and `BlenderModel.get` to retrieve a model
  with blender-specific information.
- Projects created via the API can now use smart downsampling when setting the target by passing
  `smart_downsampled` and `majority_downsampling_rate` into the `AdvancedOptions` object used with
  `Project.set_target`. The smart sampling options used with an existing project will be available
  as part of `Project.advanced_options`.
- Support for frozen models, which use tuning parameters from a parent model for more efficient
  training, has been added. Use `Model.request_frozen_model` to create a new frozen model,
  `Project.get_frozen_models` to get the list of existing frozen models and `FrozenModel.get` to
  retrieve a particular frozen model.

Enhancements
************

- The inferred date format (e.g. "%Y-%m-%d %H:%M:%S") is now included in the Feature object. For
  non-date features, it will be None.
- When specifying the API endpoint in the configuration, the client will now behave correctly for
  endpoints with and without trailing slashes.


2.4.0
=====

New Features
************

- The premium add-on product `DataRobot Prime` has been added. You can now approximate a model
  on the leaderboard and download executable code for it. See documentation for further details, or
  talk to your account representative if the feature is not available on your account.
- (Only relevant for on-premise users with a Standalone Scoring cluster.) Methods
  (`request_transferable_export` and `download_export`) have been added to the `Model` class for exporting models (which will only work if model export is turned on). There is a new class `ImportedModel` for managing imported models on a Standalone
  Scoring cluster.
- It is now possible to create projects from a WebHDFS, PostgreSQL, Oracle or MySQL data source. For more information see the
  documentation for the relevant `Project` classmethods: `create_from_hdfs`, `create_from_postgresql`,
  `create_from_oracle` and `create_from_mysql`.
- `Job.wait_for_completion`, which waits for a job to complete without returning anything, has been added.

Enhancements
************

- The client will now check the API version offered by the server specified in configuration, and
  give a warning if the client version is newer than the server version. The DataRobot server is
  always backwards compatible with old clients, but new clients may have functionality that is
  not implemented on older server versions. This issue mainly affects users with on-premise deployments
  of DataRobot.

Bugfixes
********

- Fixed an issue where `Model.request_predictions` might raise an error when predictions finished
  very quickly instead of returning the job.

API Changes
***********

- To set the target with quickrun autopilot, call `Project.set_target` with `mode=AUTOPILOT_MODE.QUICK` instead of
  specifying `quickrun=True`.

Deprecation Summary
*******************

- Semi-automatic mode for autopilot has been deprecated and will be removed in 3.0.
  Use manual or fully automatic instead.
- Use of the `quickrun` argument in `Project.set_target` has been deprecated and will be removed in
  3.0. Use `mode=AUTOPILOT_MODE.QUICK` instead.

Configuration Changes
*********************

- It is now possible to control the SSL certificate verification by setting the parameter
  `ssl_verify` in the config file.

Documentation Changes
*********************

- The "Modeling Airline Delay" example notebook has been updated to work with the new 2.3
  enhancements.
- Documentation for the generic `Job` class has been added.
- Class attributes are now documented in the `API Reference` section of the documentation.
- The changelog now appears in the documentation.
- There is a new section dedicated to configuration, which lists all of the configuration
  options and their meanings.


2.3.0
=====

New Features
************

- The DataRobot API now includes Feature Impact, an approach to measuring the relevance of each feature
  that can be applied to any model. The `Model` class now includes methods `request_feature_impact`
  (which creates and returns a feature impact job) and `get_feature_impact` (which can retrieve completed feature impact results).
- A new improved workflow for predictions now supports first uploading a dataset via `Project.upload_dataset`,
  then requesting predictions via `Model.request_predictions`. This allows us to better support predictions on
  larger datasets and non-ascii files.
- Datasets previously uploaded for predictions (represented by the `PredictionDataset` class) can be listed from
  `Project.get_datasets` and retrieve and deleted via `PredictionDataset.get` and `PredictionDataset.delete`.
- You can now create a new feature by re-interpreting the type of an existing feature in a project by
  using the `Project.create_type_transform_feature` method.
- The `Job` class now includes a `get` method for retrieving a job and a `cancel` method for
  canceling a job.
- All of the jobs classes (`Job`, `ModelJob`, `PredictJob`) now include the following new methods:
  `refresh` (for refreshing the data in the job object), `get_result` (for getting the
  completed resource resulting from the job), and `get_result_when_complete` (which waits until the job
  is complete and returns the results, or times out).
- A new method `Project.refresh` can be used to update
  `Project` objects with the latest state from the server.
- A new function `datarobot.async.wait_for_async_resolution` can be
  used to poll for the resolution of any generic asynchronous operation
  on the server.


Enhancements
************

- The `JOB_TYPE` enum now includes `FEATURE_IMPACT`.
- The `QUEUE_STATUS` enum now includes `ABORTED` and `COMPLETED`.
- The `Project.create` method now has a `read_timeout` parameter which can be used to
  keep open the connection to DataRobot while an uploaded file is being processed.
  For very large files this time can be substantial. Appropriately raising this value
  can help avoid timeouts when uploading large files.
- The method `Project.wait_for_autopilot` has been enhanced to error if
  the project enters a state where autopilot may not finish. This avoids
  a situation that existed previously where users could wait
  indefinitely on their project that was not going to finish. However,
  users are still responsible to make sure a project has more than
  zero workers, and that the queue is not paused.
- Feature.get now supports retrieving features by feature name. (For backwards compatibility,
  feature IDs are still supported until 3.0.)
- File paths that have unicode directory names can now be used for
  creating projects and PredictJobs. The filename itself must still
  be ascii, but containing directory names can have other encodings.
- Now raises more specific JobAlreadyRequested exception when we refuse a model fitting request as a duplicate.
  Users can explicitly catch this exception if they want it to be ignored.
- A `file_name` attribute has been added to the `Project` class, identifying the file name
  associated with the original project dataset. Note that if the project was created from
  a data frame, the file name may not be helpful.
- The connect timeout for establishing a connection to the server can now be set directly. This can be done in the
  yaml configuration of the client, or directly in the code. The default timeout has been lowered from 60 seconds
  to 6 seconds, which will make detecting a bad connection happen much quicker.

Bugfixes
********

- Fixed a bug (affecting Python 2 only) with printing features and featurelists whose names are
  not ascii.

API Changes
***********

- Job class hierarchy is rearranged to better express the relationship between these objects. See
  documentation for `datarobot.models.job` for details.
- `Featurelist` objects now have a `project_id` attribute to indicate which project they belong
  to. Directly accessing the `project` attribute of a `Featurelist` object is now deprecated
- Support INI-style configuration, which was deprecated in v2.1, has been removed. yaml is the only supported
  configuration format.
- The method `Project.get_jobs` method, which was deprecated in v2.1, has been removed. Users should use
  the `Project.get_model_jobs` method instead to get the list of model jobs.

Deprecation Summary
*******************

- `PredictJob.create` has been deprecated in favor of the alternate workflow using `Model.request_predictions`.
- Feature.converter (used internally for object construction) has been made private.
- Model.fetch_resource_data has been deprecated and will be removed in 3.0. To fetch a model from
   its ID, use Model.get.
- The ability to use Feature.get with feature IDs (rather than names) is deprecated and will
  be removed in 3.0.
- Instantiating a `Project`, `Model`, `Blueprint`, `Featurelist`, or `Feature` instance from a `dict`
  of data is now deprecated. Please use the `from_data` classmethod of these classes instead. Additionally,
  instantiating a `Model` from a tuple or by using the keyword argument `data` is also deprecated.
- Use of the attribute `Featurelist.project` is now deprecated. You can use the `project_id`
  attribute of a `Featurelist` to instantiate a `Project` instance using `Project.get`.
- Use of the attributes `Model.project`, `Model.blueprint`, and `Model.featurelist` are all deprecated now
  to avoid use of partially instantiated objects. Please use the ids of these objects instead.
- Using a `Project` instance as an argument in `Featurelist.get` is now deprecated.
  Please use a project_id instead. Similarly, using a `Project` instance in `Model.get` is also deprecated,
  and a project_id should be used in its place.

Configuration Changes
*********************

- Previously it was possible (though unintended) that the client configuration could be mixed through
  environment variables, configuration files, and arguments to `datarobot.Client`. This logic is now
  simpler - please see the `Getting Started` section of the documentation for more information.


2.2.33
======

Bugfixes
********

- Fixed a bug with non-ascii project names using the package with Python 2.
- Fixed an error that occurred when printing projects that had been constructed from an ID only or
  printing printing models that had been constructed from a tuple (which impacted printing PredictJobs).
- Fixed a bug with project creation from non-ascii file names. Project creation from non-ascii file names
  is not supported, so this now raises a more informative exception. The project name is no longer used as
  the file name in cases where we do not have a file name, which prevents non-ascii project names from
  causing problems in those circumstances.
- Fixed a bug (affecting Python 2 only) with printing projects, features, and featurelists whose names are
  not ascii.


2.2.32
======

New Features
************

- ``Project.get_features`` and ``Feature.get`` methods have been added for feature retrieval.
- A generic ``Job`` entity has been added for use in retrieving the entire queue at once. Calling
  ``Project.get_all_jobs`` will retrieve all (appropriately filtered) jobs from the queue. Those
  can be cancelled directly as generic jobs, or transformed into instances of the specific
  job class using ``ModelJob.from_job`` and ``PredictJob.from_job``, which allow all functionality
  previously available via the ModelJob and PredictJob interfaces.
- ``Model.train`` now supports ``featurelist_id`` and ``scoring_type`` parameters, similar to
  ``Project.train``.

Enhancements
************

- Deprecation warning filters have been updated. By default, a filter will be added ensuring that
  usage of deprecated features will display a warning once per new usage location. In order to
  hide deprecation warnings, a filter like
  `warnings.filterwarnings('ignore', category=DataRobotDeprecationWarning)`
  can be added to a script so no such warnings are shown. Watching for deprecation warnings
  to avoid reliance on deprecated features is recommended.
- If your client is misconfigured and does not specify an endpoint, the cloud production server is
  no longer used as the default as in many cases this is not the correct default.
- This changelog is now included in the distributable of the client.

Bugfixes
********

- Fixed an issue where updating the global client would not affect existing objects with cached clients.
  Now the global client is used for every API call.
- An issue where mistyping a filepath for use in a file upload has been resolved. Now an error will be
  raised if it looks like the raw string content for modeling or predictions is just one single line.

API Changes
***********

- Use of username and password to authenticate is no longer supported - use an API token instead.
- Usage of ``start_time`` and ``finish_time`` parameters in ``Project.get_models`` is not
  supported both in filtering and ordering of models
- Default value of ``sample_pct`` parameter of ``Model.train`` method is now ``None`` instead of ``100``.
  If the default value is used, models will be trained with all of the available *training* data based on
  project configuration, rather than with entire dataset including holdout for the previous default value
  of ``100``.
- ``order_by`` parameter of ``Project.list`` which was deprecated in v2.0 has been removed.
- ``recommendation_settings`` parameter of ``Project.start`` which was deprecated in v0.2 has been removed.
- ``Project.status`` method which was deprecated in v0.2 has been removed.
- ``Project.wait_for_aim_stage`` method which was deprecated in v0.2 has been removed.
- ``Delay``, ``ConstantDelay``, ``NoDelay``, ``ExponentialBackoffDelay``, ``RetryManager``
  classes from ``retry`` module which were deprecated in v2.1 were removed.
- Package renamed to ``datarobot``.

Deprecation Summary
*******************

- ``Project.update`` deprecated in favor of specific updates:
  ``rename``, ``unlock_holdout``, ``set_worker_count``.

Documentation Changes
*********************

- A new use case involving financial data has been added to the ``examples`` directory.
- Added documentation for the partition methods.

2.1.31
======

Bugfixes
********

- In Python 2, using a unicode token to instantiate the client will
  now work correctly.


2.1.30
======

Bugfixes
********

- The minimum required version of ``trafaret`` has been upgraded to 0.7.1
  to get around an incompatibility between it and ``setuptools``.


2.1.29
======

Enhancements
************

- Minimal used version of ``requests_toolbelt`` package changed from 0.4 to 0.6


2.1.28
======

New Features
************

- Default to reading YAML config file from `~/.config/datarobot/drconfig.yaml`
- Allow `config_path` argument to client
- ``wait_for_autopilot`` method added to Project. This method can be used to
  block execution until autopilot has finished running on the project.
- Support for specifying which featurelist to use with initial autopilot in
  ``Project.set_target``
- ``Project.get_predict_jobs`` method has been added, which looks up all prediction jobs for a
  project
- ``Project.start_autopilot`` method has been added, which starts autopilot on
  specified featurelist
- The schema for ``PredictJob`` in DataRobot API v2.1 now includes a ``message``. This attribute has
  been added to the PredictJob class.
- ``PredictJob.cancel`` now exists to cancel prediction jobs, mirroring ``ModelJob.cancel``
- ``Project.from_async`` is a new classmethod that can be used to wait for an async resolution
  in project creation. Most users will not need to know about it as it is used behind the scenes
  in ``Project.create`` and ``Project.set_target``, but power users who may run
  into periodic connection errors will be able to catch the new ProjectAsyncFailureError
  and decide if they would like to resume waiting for async process to resolve

Enhancements
************

- ``AUTOPILOT_MODE`` enum now uses string names for autopilot modes instead of numbers

Deprecation Summary
*******************

- ``ConstantDelay``, ``NoDelay``, ``ExponentialBackoffDelay``, and ``RetryManager`` utils are now deprecated
- INI-style config files are now deprecated (in favor of YAML config files)
- Several functions in the `utils` submodule are now deprecated (they are
  being moved elsewhere and are not considered part of the public interface)
- ``Project.get_jobs`` has been renamed ``Project.get_model_jobs`` for clarity and deprecated
- Support for the experimental date partitioning has been removed in DataRobot API,
  so it is being removed from the client immediately.

API Changes
***********

- In several places where ``AppPlatformError`` was being raised, now ``TypeError``, ``ValueError`` or
  ``InputNotUnderstoodError`` are now used. With this change, one can now safely assume that when
  catching an ``AppPlatformError`` it is because of an unexpected response from the server.
- ``AppPlatformError`` has gained a two new attributes, ``status_code`` which is the HTTP status code
  of the unexpected response from the server, and ``error_code`` which is a DataRobot-defined error
  code. ``error_code`` is not used by any routes in DataRobot API 2.1, but will be in the future.
  In cases where it is not provided, the instance of ``AppPlatformError`` will have the attribute
  ``error_code`` set to ``None``.
- Two new subclasses of ``AppPlatformError`` have been introduced, ``ClientError`` (for 400-level
  response status codes) and ``ServerError`` (for 500-level response status codes). These will make
  it easier to build automated tooling that can recover from periodic connection issues while polling.
- If a ``ClientError`` or ``ServerError`` occurs during a call to ``Project.from_async``, then a
  ``ProjectAsyncFailureError`` (a subclass of AsyncFailureError) will be raised. That exception will
  have the status_code of the unexpected response from the server, and the location that was being
  polled to wait for the asynchronous process to resolve.


2.0.27
======

New Features
************

- ``PredictJob`` class was added to work with prediction jobs
- ``wait_for_async_predictions`` function added to `predict_job` module

Deprecation Summary
*******************

- The `order_by` parameter of the ``Project.list`` is now deprecated.


0.2.26
======

Enhancements
************

- ``Projet.set_target`` will re-fetch the project data after it succeeds,
  keeping the client side in sync with the state of the project on the
  server
- ``Project.create_featurelist`` now throws ``DuplicateFeaturesError``
  exception if passed list of features contains duplicates
- ``Project.get_models`` now supports snake_case arguments to its
  order_by keyword

Deprecation Summary
*******************

- ``Project.wait_for_aim_stage`` is now deprecated, as the REST Async
  flow is a more reliable method of determining that project creation has
  completed successfully
- ``Project.status`` is deprecated in favor of ``Project.get_status``
- ``recommendation_settings`` parameter of ``Project.start`` is
  deprecated in favor of ``recommender_settings``

Bugfixes
********

- ``Project.wait_for_aim_stage`` changed to support Python 3
- Fixed incorrect value of ``SCORING_TYPE.cross_validation``
- Models returned by ``Project.get_models`` will now be correctly
  ordered when the order_by keyword is used


0.2.25
======

- Pinned versions of required libraries

0.2.24
======

Official release of v0.2

0.1.24
======

- Updated documentation
- Renamed parameter `name` of `Project.create` and `Project.start` to `project_name`
- Removed `Model.predict` method
- `wait_for_async_model_creation` function added to `modeljob` module
- `wait_for_async_status_service` of `Project` class renamed to `_wait_for_async_status_service`
- Can now use auth_token in config file to configure SDK


0.1.23
======

- Fixes a method that pointed to a removed route


0.1.22
======

- Added `featurelist_id` attribute to `ModelJob` class


0.1.21
======

- Removes `model` attribute from `ModelJob` class


0.1.20
======

- Project creation raises `AsyncProjectCreationError` if it was unsuccessful
- Removed `Model.list_prime_rulesets` and `Model.get_prime_ruleset` methods
- Removed `Model.predict_batch` method
- Removed `Project.create_prime_model` method
- Removed `PrimeRuleSet` model
- Adds backwards compatibility bridge for ModelJob async
- Adds ModelJob.get and ModelJob.get_model


0.1.19
======

- Minor bugfixes in `wait_for_async_status_service`


0.1.18
======

- Removes `submit_model` from Project until server-side implementation is improved
- Switches training URLs for new resource-based route at /projects/<project_id>/models/
- Job renamed to ModelJob, and using modelJobs route
- Fixes an inconsistency in argument order for `train` methods


0.1.17
======

- `wait_for_async_status_service` timeout increased from 60s to 600s


0.1.16
======

- `Project.create` will now handle both async/sync project creation


0.1.15
======

- All routes pluralized to sync with changes in API
- `Project.get_jobs` will request all jobs when no param specified
- dataframes from `predict` method will have pythonic names
- `Project.get_status` created, `Project.status` now deprecated
- `Project.unlock_holdout` created.
- Added `quickrun` parameter to `Project.set_target`
- Added `modelCategory` to Model schema
- Add `permalinks` feature to Project and Model objects.
- `Project.create_prime_model` created


0.1.14
======

- `Project.set_worker_count` fix for compatibility with API change in project update.


0.1.13
======

- Add positive class to `set_target`.
- Change attributes names of `Project`, `Model`, `Job` and `Blueprint`
    - `features` in `Model`, `Job` and `Blueprint` are now `processes`
    - `dataset_id` and `dataset_name` migrated to `featurelist_id` and `featurelist_name`.
    - `samplepct` -> `sample_pct`
- `Model` has now `blueprint`, `project`, and `featurlist` attributes.
- Minor bugfixes.


0.1.12
======

- Minor fixes regarding rename `Job` attributes. `features` attributes now named `processes`, `samplepct` now is `sample_pct`.


0.1.11
======

(May 27, 2015)

- Minor fixes regarding migrating API from under_score names to camelCase.


0.1.10
======

(May 20, 2015)

- Remove `Project.upload_file`, `Project.upload_file_from_url` and `Project.attach_file` methods. Moved all logic that uploading file to `Project.create` method.


0.1.9
=====

(May 15, 2015)

- Fix uploading file causing a lot of memory usage. Minor bugfixes.
