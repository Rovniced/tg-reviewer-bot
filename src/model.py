class ModelBase:
    def to_dict(self):
        return self.__dict__


class SubmitterInfoModel(ModelBase):
    user_id: int
    username: str
    full_name: str
    origin_message_id: int


class ReviewerModel(ModelBase):
    pass


class SubmissionModel(ModelBase):
    submitter: SubmitterInfoModel
    reviewer_data: int
    text: str
    media_id_list: list
    media_type_list: list
    documents_id_list: list
    document_type_list: list
    append: dict
