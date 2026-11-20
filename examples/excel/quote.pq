// Excel / Power BI: Data > Get Data > From Other Sources > Blank Query > Advanced Editor
// (Italian Excel: Dati > Recupera dati > Da altre origini > Query vuota > Editor avanzato)
// Store your key in a Power Query parameter named NeuraxKey (Manage Parameters).
let
    Body = Json.FromValue([
        workload = "bs-mc-european@1",
        params = [spot = 100, strike = 105, rate = 0.03, volatility = 0.2,
                  maturity_years = 1, option_type = "call", paths = 1000000]
    ]),
    Response = Json.Document(Web.Contents("https://api.neuraxcopute.it/v1/quote",
        [Headers = [Authorization = "Bearer " & NeuraxKey, #"Content-Type" = "application/json"],
         Content = Body])),
    Table = Record.ToTable(Response)
in
    Table
