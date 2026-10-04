class Call:
    def __init__(self, **row):
        self.call_id = row.get('call_id')
        self.call_date = str(row.get('call_date'))
        self.adress = row.get('adress')
        self.short_description = row.get('short_description')

    def to_dict(self):
        return {
            "call_id": self.call_id,
            "call_date": self.call_date,
            "adress": self.adress,
            "short_description": self.short_description
        }