class SubmitterInfoModel:
    user_id: int
    username: str
    full_name: str
    origin_message_id: int


class SubmissionModel:
    submitter: SubmitterInfoModel
    reviewer_data: int
    text: int
    media_id_list: list
    media_type_list: list
    documents_id_list: list
    document_type_list: list
    append: dict
