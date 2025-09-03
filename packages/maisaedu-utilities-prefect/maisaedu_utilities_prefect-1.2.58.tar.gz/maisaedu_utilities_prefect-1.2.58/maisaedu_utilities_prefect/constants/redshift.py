from maisaedu_utilities_prefect.constants.env import LOCAL, DEV, PROD

IAM_ROLE_PREFECT_DEV = "arn:aws:iam::977647303146:role/PrefectAssumeRoleInsideRedshiftDEV"

IAM_ROLE_PREFECT_PROD = "arn:aws:iam::977647303146:role/PrefectAssumeRoleInsideRedshiftPROD"

def get_iam_role(env):
    if env == DEV or env == LOCAL:
        return IAM_ROLE_PREFECT_DEV
    elif env == PROD:
        return IAM_ROLE_PREFECT_PROD