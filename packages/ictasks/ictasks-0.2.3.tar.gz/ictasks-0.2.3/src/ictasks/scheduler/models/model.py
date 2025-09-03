class Model:
    _type: str | None = None
    _fields: list = []

    def __init__(self) -> None:
        self.items: list = []

    @staticmethod
    def get_db_schema(model_type):
        refs = []
        ret = f"{model_type._type}("
        for idx, field in enumerate(model_type._fields):
            ret += field.db()
            db_ref = field.db_refs()
            if db_ref is not None:
                refs.append(db_ref)
            if idx < len(model_type._fields) - 1 or refs:
                ret += ","
        for idx, ref in enumerate(refs):
            ret += ref
            if idx < len(refs) - 1:
                ret += ","
        ret += ")"
        return ret

    @staticmethod
    def get_column_names(model_type):
        return [f.name for f in model_type._fields]

    @staticmethod
    def get_db_columns(model_type):
        ret = ""
        columns = Model.get_column_names(model_type)
        for idx, column in enumerate(columns):
            ret += column
            if idx < len(columns):
                ret += ","
        return ret

    def save(self, db):
        pass

    def object(self, id, db):
        pass

    def objects(self, query, db):
        pass
