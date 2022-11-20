
class Company:
    def __init__(self, name, id, wrds_id, country, type_Desc, cusip, isin, sedol, ticker):
        self.name = name
        self.id = id
        self.wrds_id = wrds_id
        self.country = country
        # one of public, private, extinct, government, nonprofit, holding, college, foundation
        self.type_desc = type_desc
        self.cusip = cusip
        self.isin = isin
        self.sedol = sedol
        self.ticker = ticker

        # List of {other_company_id : [start year*14+month, end year*14+month, # of days]}
        self.recieved_transactions = []
        # See above
        self.sent_transactions = []

    def add_sent_transaction(recieving_id, ):
