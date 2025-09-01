KONDUKTOR_SSH_PORT = 2222

# Common labels used across JobSets and Deployments
JOB_NAME_LABEL = 'trainy.ai/job-name'
DEPLOYMENT_NAME_LABEL = 'trainy.ai/deployment-name'
AIBRIX_NAME_LABEL = 'model.aibrix.ai/name'
USERID_LABEL = 'trainy.ai/user-id'
USER_LABEL = 'trainy.ai/username'
ACCELERATOR_LABEL = 'trainy.ai/accelerator'
NUM_ACCELERATORS_LABEL = 'trainy.ai/num-accelerators'
MAX_EXECUTION_TIME_LABEL = 'kueue.x-k8s.io/max-exec-time-seconds'

# Start/stop/status related labels
STOP_USERID_LABEL = 'trainy.ai/stop-userid'
STOP_USERNAME_LABEL = 'trainy.ai/stop-username'

# Secret labels
SECRET_BASENAME_LABEL = 'trainy.ai/secret-basename'
SECRET_KIND_LABEL = 'trainy.ai/secret-kind'
SECRET_OWNER_LABEL = 'trainy.ai/secret-owner'
