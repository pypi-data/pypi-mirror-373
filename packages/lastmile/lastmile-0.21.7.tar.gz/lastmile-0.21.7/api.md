# Projects

Types:

```python
from lastmile.types import (
    ProjectCreateResponse,
    ProjectListResponse,
    ProjectDefaultResponse,
    ProjectGetResponse,
)
```

Methods:

- <code title="post /api/2/auto_eval/project/create">client.projects.<a href="./src/lastmile/resources/projects.py">create</a>(\*\*<a href="src/lastmile/types/project_create_params.py">params</a>) -> <a href="./src/lastmile/types/project_create_response.py">ProjectCreateResponse</a></code>
- <code title="post /api/2/auto_eval/project/list">client.projects.<a href="./src/lastmile/resources/projects.py">list</a>(\*\*<a href="src/lastmile/types/project_list_params.py">params</a>) -> <a href="./src/lastmile/types/project_list_response.py">ProjectListResponse</a></code>
- <code title="post /api/2/auto_eval/project/get_default">client.projects.<a href="./src/lastmile/resources/projects.py">default</a>(\*\*<a href="src/lastmile/types/project_default_params.py">params</a>) -> <a href="./src/lastmile/types/project_default_response.py">ProjectDefaultResponse</a></code>
- <code title="post /api/2/auto_eval/project/get">client.projects.<a href="./src/lastmile/resources/projects.py">get</a>(\*\*<a href="src/lastmile/types/project_get_params.py">params</a>) -> <a href="./src/lastmile/types/project_get_response.py">ProjectGetResponse</a></code>

# Experiments

Types:

```python
from lastmile.types import (
    ExperimentCreateResponse,
    ExperimentListResponse,
    ExperimentDeleteResponse,
    ExperimentGetResponse,
)
```

Methods:

- <code title="post /api/2/auto_eval/experiment/create">client.experiments.<a href="./src/lastmile/resources/experiments.py">create</a>(\*\*<a href="src/lastmile/types/experiment_create_params.py">params</a>) -> <a href="./src/lastmile/types/experiment_create_response.py">ExperimentCreateResponse</a></code>
- <code title="post /api/2/auto_eval/experiment/list">client.experiments.<a href="./src/lastmile/resources/experiments.py">list</a>(\*\*<a href="src/lastmile/types/experiment_list_params.py">params</a>) -> <a href="./src/lastmile/types/experiment_list_response.py">ExperimentListResponse</a></code>
- <code title="delete /api/2/auto_eval/experiment/delete">client.experiments.<a href="./src/lastmile/resources/experiments.py">delete</a>(\*\*<a href="src/lastmile/types/experiment_delete_params.py">params</a>) -> <a href="./src/lastmile/types/experiment_delete_response.py">ExperimentDeleteResponse</a></code>
- <code title="post /api/2/auto_eval/experiment/get">client.experiments.<a href="./src/lastmile/resources/experiments.py">get</a>(\*\*<a href="src/lastmile/types/experiment_get_params.py">params</a>) -> <a href="./src/lastmile/types/experiment_get_response.py">ExperimentGetResponse</a></code>

# Datasets

Types:

```python
from lastmile.types import (
    DatasetCreateResponse,
    DatasetListResponse,
    DatasetDeleteResponse,
    DatasetCopyResponse,
    DatasetFinalizeFileUploadResponse,
    DatasetGetResponse,
    DatasetGetDownloadURLResponse,
    DatasetGetViewResponse,
    DatasetUploadFileResponse,
)
```

Methods:

- <code title="post /api/2/auto_eval/dataset/create">client.datasets.<a href="./src/lastmile/resources/datasets.py">create</a>(\*\*<a href="src/lastmile/types/dataset_create_params.py">params</a>) -> <a href="./src/lastmile/types/dataset_create_response.py">DatasetCreateResponse</a></code>
- <code title="post /api/2/auto_eval/dataset/list">client.datasets.<a href="./src/lastmile/resources/datasets.py">list</a>(\*\*<a href="src/lastmile/types/dataset_list_params.py">params</a>) -> <a href="./src/lastmile/types/dataset_list_response.py">DatasetListResponse</a></code>
- <code title="post /api/2/auto_eval/dataset/archive">client.datasets.<a href="./src/lastmile/resources/datasets.py">delete</a>(\*\*<a href="src/lastmile/types/dataset_delete_params.py">params</a>) -> <a href="./src/lastmile/types/dataset_delete_response.py">DatasetDeleteResponse</a></code>
- <code title="post /api/2/auto_eval/dataset/clone">client.datasets.<a href="./src/lastmile/resources/datasets.py">copy</a>(\*\*<a href="src/lastmile/types/dataset_copy_params.py">params</a>) -> <a href="./src/lastmile/types/dataset_copy_response.py">DatasetCopyResponse</a></code>
- <code title="post /api/2/auto_eval/dataset/finalize_single_file_upload">client.datasets.<a href="./src/lastmile/resources/datasets.py">finalize_file_upload</a>(\*\*<a href="src/lastmile/types/dataset_finalize_file_upload_params.py">params</a>) -> <a href="./src/lastmile/types/dataset_finalize_file_upload_response.py">DatasetFinalizeFileUploadResponse</a></code>
- <code title="post /api/2/auto_eval/dataset/get">client.datasets.<a href="./src/lastmile/resources/datasets.py">get</a>(\*\*<a href="src/lastmile/types/dataset_get_params.py">params</a>) -> <a href="./src/lastmile/types/dataset_get_response.py">DatasetGetResponse</a></code>
- <code title="post /api/2/auto_eval/dataset/get_download_url">client.datasets.<a href="./src/lastmile/resources/datasets.py">get_download_url</a>(\*\*<a href="src/lastmile/types/dataset_get_download_url_params.py">params</a>) -> <a href="./src/lastmile/types/dataset_get_download_url_response.py">DatasetGetDownloadURLResponse</a></code>
- <code title="post /api/2/auto_eval/dataset/get_view">client.datasets.<a href="./src/lastmile/resources/datasets.py">get_view</a>(\*\*<a href="src/lastmile/types/dataset_get_view_params.py">params</a>) -> <a href="./src/lastmile/types/dataset_get_view_response.py">DatasetGetViewResponse</a></code>
- <code title="post /api/2/auto_eval/dataset/upload_file">client.datasets.<a href="./src/lastmile/resources/datasets.py">upload_file</a>(\*\*<a href="src/lastmile/types/dataset_upload_file_params.py">params</a>) -> <a href="./src/lastmile/types/dataset_upload_file_response.py">DatasetUploadFileResponse</a></code>

# Evaluation

Types:

```python
from lastmile.types import (
    EvaluationDeleteRunResponse,
    EvaluationEvaluateResponse,
    EvaluationEvaluateDatasetResponse,
    EvaluationEvaluateRunResponse,
    EvaluationGetMetricResponse,
    EvaluationGetRunResponse,
    EvaluationListMetricsResponse,
)
```

Methods:

- <code title="delete /api/2/auto_eval/evaluation/delete_run">client.evaluation.<a href="./src/lastmile/resources/evaluation.py">delete_run</a>(\*\*<a href="src/lastmile/types/evaluation_delete_run_params.py">params</a>) -> <a href="./src/lastmile/types/evaluation_delete_run_response.py">EvaluationDeleteRunResponse</a></code>
- <code title="post /api/2/auto_eval/evaluation/evaluate">client.evaluation.<a href="./src/lastmile/resources/evaluation.py">evaluate</a>(\*\*<a href="src/lastmile/types/evaluation_evaluate_params.py">params</a>) -> <a href="./src/lastmile/types/evaluation_evaluate_response.py">EvaluationEvaluateResponse</a></code>
- <code title="post /api/2/auto_eval/evaluation/evaluate_dataset">client.evaluation.<a href="./src/lastmile/resources/evaluation.py">evaluate_dataset</a>(\*\*<a href="src/lastmile/types/evaluation_evaluate_dataset_params.py">params</a>) -> <a href="./src/lastmile/types/evaluation_evaluate_dataset_response.py">EvaluationEvaluateDatasetResponse</a></code>
- <code title="post /api/2/auto_eval/evaluation/evaluate_run">client.evaluation.<a href="./src/lastmile/resources/evaluation.py">evaluate_run</a>(\*\*<a href="src/lastmile/types/evaluation_evaluate_run_params.py">params</a>) -> <a href="./src/lastmile/types/evaluation_evaluate_run_response.py">EvaluationEvaluateRunResponse</a></code>
- <code title="post /api/2/auto_eval/evaluation/get_metric">client.evaluation.<a href="./src/lastmile/resources/evaluation.py">get_metric</a>(\*\*<a href="src/lastmile/types/evaluation_get_metric_params.py">params</a>) -> <a href="./src/lastmile/types/evaluation_get_metric_response.py">EvaluationGetMetricResponse</a></code>
- <code title="post /api/2/auto_eval/evaluation/get_run">client.evaluation.<a href="./src/lastmile/resources/evaluation.py">get_run</a>(\*\*<a href="src/lastmile/types/evaluation_get_run_params.py">params</a>) -> <a href="./src/lastmile/types/evaluation_get_run_response.py">EvaluationGetRunResponse</a></code>
- <code title="post /api/2/auto_eval/evaluation/list_metrics">client.evaluation.<a href="./src/lastmile/resources/evaluation.py">list_metrics</a>() -> <a href="./src/lastmile/types/evaluation_list_metrics_response.py">EvaluationListMetricsResponse</a></code>

# FineTuneJobs

Types:

```python
from lastmile.types import (
    FineTuneJobCreateResponse,
    FineTuneJobListResponse,
    FineTuneJobGetStatusResponse,
    FineTuneJobListBaseModelsResponse,
    FineTuneJobSubmitResponse,
)
```

Methods:

- <code title="post /api/2/auto_eval/fine_tune_job/create">client.fine_tune_jobs.<a href="./src/lastmile/resources/fine_tune_jobs.py">create</a>(\*\*<a href="src/lastmile/types/fine_tune_job_create_params.py">params</a>) -> <a href="./src/lastmile/types/fine_tune_job_create_response.py">FineTuneJobCreateResponse</a></code>
- <code title="post /api/2/auto_eval/fine_tune_job/list">client.fine_tune_jobs.<a href="./src/lastmile/resources/fine_tune_jobs.py">list</a>(\*\*<a href="src/lastmile/types/fine_tune_job_list_params.py">params</a>) -> <a href="./src/lastmile/types/fine_tune_job_list_response.py">FineTuneJobListResponse</a></code>
- <code title="post /api/2/auto_eval/fine_tune_job/get_status">client.fine_tune_jobs.<a href="./src/lastmile/resources/fine_tune_jobs.py">get_status</a>(\*\*<a href="src/lastmile/types/fine_tune_job_get_status_params.py">params</a>) -> <a href="./src/lastmile/types/fine_tune_job_get_status_response.py">FineTuneJobGetStatusResponse</a></code>
- <code title="post /api/2/auto_eval/fine_tune_job/list_base_models">client.fine_tune_jobs.<a href="./src/lastmile/resources/fine_tune_jobs.py">list_base_models</a>() -> <a href="./src/lastmile/types/fine_tune_job_list_base_models_response.py">FineTuneJobListBaseModelsResponse</a></code>
- <code title="post /api/2/auto_eval/fine_tune_job/submit">client.fine_tune_jobs.<a href="./src/lastmile/resources/fine_tune_jobs.py">submit</a>(\*\*<a href="src/lastmile/types/fine_tune_job_submit_params.py">params</a>) -> <a href="./src/lastmile/types/fine_tune_job_submit_response.py">FineTuneJobSubmitResponse</a></code>

# LabelDatasetJobs

Types:

```python
from lastmile.types import (
    LabelDatasetJobCreateResponse,
    LabelDatasetJobGetStatusResponse,
    LabelDatasetJobSubmitResponse,
)
```

Methods:

- <code title="post /api/2/auto_eval/pseudo_label_job/create">client.label_dataset_jobs.<a href="./src/lastmile/resources/label_dataset_jobs.py">create</a>(\*\*<a href="src/lastmile/types/label_dataset_job_create_params.py">params</a>) -> <a href="./src/lastmile/types/label_dataset_job_create_response.py">LabelDatasetJobCreateResponse</a></code>
- <code title="post /api/2/auto_eval/pseudo_label_job/get_status">client.label_dataset_jobs.<a href="./src/lastmile/resources/label_dataset_jobs.py">get_status</a>(\*\*<a href="src/lastmile/types/label_dataset_job_get_status_params.py">params</a>) -> <a href="./src/lastmile/types/label_dataset_job_get_status_response.py">LabelDatasetJobGetStatusResponse</a></code>
- <code title="post /api/2/auto_eval/pseudo_label_job/submit">client.label_dataset_jobs.<a href="./src/lastmile/resources/label_dataset_jobs.py">submit</a>(\*\*<a href="src/lastmile/types/label_dataset_job_submit_params.py">params</a>) -> <a href="./src/lastmile/types/label_dataset_job_submit_response.py">LabelDatasetJobSubmitResponse</a></code>
